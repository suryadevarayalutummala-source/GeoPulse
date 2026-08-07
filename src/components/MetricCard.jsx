import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';

export default function MetricCard({
  title,
  value,
  subtext,
  badgeColor = 'sage',
  highlight = false,
  trend = null,
  trendValue = ''
}) {
  const getBadgeStyle = () => {
    switch (badgeColor) {
      case 'sage':
        return 'bg-sage-200/90 text-forest-950 border-sage-400/60';
      case 'olive':
        return 'bg-olive-200/90 text-forest-950 border-olive-400/60';
      case 'beige':
      default:
        return 'bg-beige-300/90 text-forest-950 border-beige-400/60';
    }
  };

  return (
    <div
      className={`glass-card p-3.5 rounded-xl border flex flex-col justify-between transition-all duration-300 ${
        highlight
          ? 'bg-beige-300/90 border-forest-600/60 shadow-[0_4px_16px_rgba(24,42,27,0.08)]'
          : 'border-sage-300/60 hover:border-forest-600/40'
      }`}
    >
      <div>
        <div className="flex items-center justify-between mb-1">
          <span className="text-[10px] font-extrabold tracking-wider text-forest-700 uppercase">
            {title}
          </span>
          {trend && (
            <span
              className={`text-[9px] font-extrabold px-1.5 py-0.5 rounded border flex items-center space-x-0.5 ${
                trend === 'up'
                  ? 'bg-sage-200 text-forest-950 border-sage-400/60'
                  : 'bg-rose-100 text-rose-800 border-rose-300'
              }`}
            >
              {trend === 'up' ? (
                <TrendingUp className="w-2.5 h-2.5" />
              ) : (
                <TrendingDown className="w-2.5 h-2.5" />
              )}
              <span>{trendValue}</span>
            </span>
          )}
        </div>

        <div className="text-base lg:text-lg font-extrabold text-forest-950 font-heading tracking-tight">
          {value}
        </div>
      </div>

      {subtext && (
        <div className="text-[10px] text-forest-700 font-medium mt-1.5 truncate border-t border-sage-300/40 pt-1">
          {subtext}
        </div>
      )}
    </div>
  );
}
