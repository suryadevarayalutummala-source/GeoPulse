#!/usr/bin/env python3
"""Demo script for the Smart Infrastructure backend pipeline.

Runs: reverse geocode -> overpass queries -> soil lookup -> market lookup -> scoring -> AIContextBuilder
Prints colored output, execution time, and a success message. Gracefully handles failures.
"""
from __future__ import annotations

import json
import time
import sys
from pathlib import Path

try:
    from colorama import Fore, Style, init as colorama_init
    colorama_init()
except Exception:
        # fallback minimal colors
        class _C:
            RED = "\u001b[31m"
            GREEN = "\u001b[32m"
            YELLOW = "\u001b[33m"
            CYAN = "\u001b[36m"
            RESET = "\u001b[0m"
            RESET_ALL = "\u001b[0m"

        Fore = _C
        Style = _C
# Ensure local backend package is importable when running from repo root
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import importlib


def safe_import(name: str):
    try:
        return importlib.import_module(name)
    except Exception as exc:
        print(f"{Fore.YELLOW}Warning:{Style.RESET_ALL} Failed to import {name}: {exc}")
        return None


def count_from_overpass_result(obj):
    if obj is None:
        return 0
    if isinstance(obj, dict) and "count" in obj:
        try:
            return int(obj["count"])
        except Exception:
            return 0
    if isinstance(obj, (list, tuple)):
        return len(obj)
    return 0


def main():
    lat, lon = 17.4325, 78.3434
    start = time.perf_counter()

    print(f"{Fore.CYAN}SmartInfra Demo Starting{Style.RESET_ALL}")

    # Geocode
    GeocoderMod = safe_import("services.geocoder_service")
    geocode_res = {}
    if GeocoderMod:
        try:
            svc = GeocoderMod.GeocoderService()
            geocode_res = svc.reverse_geocode(lat, lon)
            print(f"{Fore.GREEN}Reverse geocode:{Style.RESET_ALL} {geocode_res.get('display_name') or geocode_res}")
        except Exception as exc:
            print(f"{Fore.RED}Reverse geocode failed:{Style.RESET_ALL} {exc}")

    # Overpass
    OverpassMod = safe_import("services.overpass_service")
    overpass_counts = {}
    overpass_details = {}
    if OverpassMod:
        try:
            svc = OverpassMod.OverpassService()
            amenities = svc.get_amenities(lat, lon, 1000) if hasattr(svc, "get_amenities") else {}
            if isinstance(amenities, dict):
                overpass_counts = {k: int(v.get("count", 0)) for k, v in amenities.items()}
                overpass_details = amenities
            else:
                raise TypeError("Unexpected amenities payload from OverpassService")
            print(f"{Fore.GREEN}Overpass counts:{Style.RESET_ALL} {overpass_counts}")
        except Exception as exc:
            print(f"{Fore.RED}Overpass queries failed:{Style.RESET_ALL} {exc}")
            try:
                fallback_path = ROOT / "data" / "plots_final.json"
                with open(fallback_path, "r", encoding="utf-8") as handle:
                    plots = json.load(handle)
                fallback_counts = {
                    "schools": sum(int(plot.get("poi_amenities", {}).get("schools_nearby", 0)) for plot in plots),
                    "hospitals": sum(int(plot.get("poi_amenities", {}).get("hospitals_nearby", 0)) for plot in plots),
                    "parks": sum(int(plot.get("poi_amenities", {}).get("parks_nearby", 0)) for plot in plots),
                }
                overpass_counts = fallback_counts
                overpass_details = {"fallback_plots": plots}
                print(f"{Fore.YELLOW}Using cached plot amenities fallback counts:{Style.RESET_ALL} {overpass_counts}")
            except Exception as fallback_exc:
                print(f"{Fore.RED}Overpass fallback failed:{Style.RESET_ALL} {fallback_exc}")

    # Soil
    SoilMod = safe_import("services.soil_service")
    soil_info = {}
    if SoilMod:
        try:
            svc = SoilMod.SoilService()
            soil_info = svc.get_soil_information(lat, lon)
            print(f"{Fore.GREEN}Soil lookup:{Style.RESET_ALL} region={soil_info.get('region')}, soil_type={soil_info.get('soil_type')}")
        except Exception as exc:
            print(f"{Fore.RED}Soil lookup failed:{Style.RESET_ALL} {exc}")

    # Market
    MarketMod = safe_import("services.market_service")
    market_info = {}
    if MarketMod:
        try:
            svc = MarketMod.MarketService()
            market_info = svc.get_market_information(lat, lon)
            print(f"{Fore.GREEN}Market lookup:{Style.RESET_ALL} region={market_info.get('region')}, price_per_sqft={market_info.get('price_per_sqft')}")
        except Exception as exc:
            print(f"{Fore.RED}Market lookup failed:{Style.RESET_ALL} {exc}")

    # Scoring
    ScoringMod = safe_import("services.scoring_service")
    scores = {}
    if ScoringMod:
        try:
            ScoringService = ScoringMod.ScoringService
            ConnectivityFactors = ScoringMod.ConnectivityFactors
            LivabilityFactors = ScoringMod.LivabilityFactors
            InvestmentFactors = ScoringMod.InvestmentFactors
            ConstructionFactors = ScoringMod.ConstructionFactors

            conn = ConnectivityFactors(
                schools_count=overpass_counts.get("schools", 0),
                hospitals_count=overpass_counts.get("hospitals", 0),
                bus_stops_count=0,
                metro_count=0,
                parks_count=overpass_counts.get("parks", 0),
            )

            liv = LivabilityFactors(
                schools_count=conn.schools_count,
                hospitals_count=conn.hospitals_count,
                parks_count=conn.parks_count,
                water_table_depth=float(soil_info.get("water_table_depth_m") or soil_info.get("water_table_depth", 0) or 0.0),
            )

            inv = InvestmentFactors(
                price_per_sqft=float(market_info.get("price_per_sqft") or 1.0),
                historical_growth_percent=float(market_info.get("historical_growth_percent") or 0.0),
                future_growth_percent=float(market_info.get("future_growth_percent") or 0.0),
                rental_yield_percent=float(market_info.get("rental_yield_percent") or 0.0),
                roi_index=float(market_info.get("roi_index") or 0.0),
            )

            constr = ConstructionFactors(
                bearing_capacity_kpa=float(soil_info.get("bearing_capacity_kpa") or 0.0),
                water_table_depth_m=float(soil_info.get("water_table_depth_m") or 0.0),
                construction_suitability=str(soil_info.get("construction_suitability") or "Unknown"),
            )

            svc = ScoringService()
            score_fn = getattr(svc, "calculate_scores", getattr(svc, "generate_property_scores", None))
            if score_fn is None:
                raise RuntimeError("No scoring entrypoint available on ScoringService")
            scores = score_fn(conn, liv, inv, constr)
            print(f"{Fore.GREEN}Scores:{Style.RESET_ALL} {scores}")
        except Exception as exc:
            print(f"{Fore.RED}Scoring failed:{Style.RESET_ALL} {exc}")

    # AI Context Builder
    AIContextMod = safe_import("services.ai_context_builder")
    ai_ctx = {}
    if AIContextMod:
        try:
            builder = AIContextMod.AIContextBuilder()
            ai_ctx = builder.build_context(lat, lon)
            print(f"{Fore.CYAN}AI Context built successfully{Style.RESET_ALL}")
        except Exception as exc:
            print(f"{Fore.RED}AIContextBuilder failed:{Style.RESET_ALL} {exc}")

    end = time.perf_counter()
    elapsed = end - start

    # Final pretty print
    print("\n" + Fore.CYAN + "Final AI Context JSON:" + Style.RESET_ALL)
    fallback_payload = {
        "location": geocode_res,
        "amenities": overpass_counts,
        "amenity_details": overpass_details,
        "soil": soil_info,
        "market": market_info,
        "scores": scores,
    }
    print(json.dumps(ai_ctx or fallback_payload, indent=2, ensure_ascii=False))

    print(f"\n{Fore.GREEN}Demo finished in {elapsed:.2f}s{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
