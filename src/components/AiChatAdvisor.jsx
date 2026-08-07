import React, { useState, useRef, useEffect } from 'react';
import { Bot, Send, User, Sparkles, RefreshCw, HardHat, Home, TrendingUp, ChevronRight, RotateCcw } from 'lucide-react';

// Enhanced Markdown Parser for AI Chat Bubbles (removes raw ** asterisks)
const renderFormattedText = (text) => {
  if (!text) return null;

  const lines = text.split('\n');

  return lines.map((line, lineIdx) => {
    const trimmed = line.trim();
    const isBullet = trimmed.startsWith('- ');
    const lineContent = isBullet ? trimmed.slice(2) : line;

    // Split by **bold** markers
    const parts = lineContent.split(/(\*\*.*?\*\*)/g);
    const formattedParts = parts.map((part, index) => {
      if (part.startsWith('**') && part.endsWith('**') && part.length > 4) {
        return (
          <strong key={index} className="font-extrabold text-forest-950 bg-forest-900/10 px-1 py-0.5 rounded">
            {part.slice(2, -2)}
          </strong>
        );
      }
      return <span key={index}>{part}</span>;
    });

    if (isBullet) {
      return (
        <div key={lineIdx} className="flex items-start space-x-2 my-1">
          <span className="w-1.5 h-1.5 rounded-full bg-forest-800 mt-1.5 shrink-0" />
          <div className="flex-1">{formattedParts}</div>
        </div>
      );
    }

    return (
      <div key={lineIdx} className={lineIdx > 0 ? 'mt-1' : ''}>
        {formattedParts}
      </div>
    );
  });
};

export default function AiChatAdvisor({ selectedPlot, activeRole, setActiveRole }) {
  const [messages, setMessages] = useState([
    {
      sender: 'ai',
      text: `Hello! I am your GeoPulse Spatial Advisor. I am analyzing **${selectedPlot?.name || 'the selected land parcel'}** from your **${activeRole.toUpperCase()}** perspective. Select a recommendation chip below or type any custom question!`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const chatContainerRef = useRef(null);
  const isFirstRender = useRef(true);

  // Auto scroll to bottom of internal chat box ONLY (prevents main window scrolling)
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  // Dynamically post a new AI greeting prompt when role or plot changes
  useEffect(() => {
    if (isFirstRender.current) {
      isFirstRender.current = false;
      return;
    }

    const roleName = activeRole.toUpperCase();
    const plotName = selectedPlot?.name || 'Selected Parcel';
    const plotId = selectedPlot?.plot_id || '';

    const newRolePrompt = `🔄 **Context Switched to ${roleName} View**\nNow evaluating **${plotName}** (${plotId}) for **${activeRole}** metrics. Check the updated recommendation chips below or ask me any question!`;

    setMessages((prev) => [
      ...prev,
      {
        sender: 'ai',
        text: newRolePrompt,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
    ]);
  }, [activeRole, selectedPlot?.plot_id]);

  // Role-specific recommendation prompt chips
  const recommendationChips = {
    builder: [
      `What foundation type is best for ${selectedPlot?.bearing_capacity_kpa} kPa bearing capacity?`,
      `Analyze construction cost feasibility at ₹${selectedPlot?.construction_cost_estimate_per_sqft}/sqft`,
      `Check floor area ratio (FAR) for ${selectedPlot?.max_permissible_floors} floors permitted`
    ],
    homebuyer: [
      `How quiet and livable is ${selectedPlot?.locality} with nearby parks & green buffers?`,
      `Evaluate commute time (${selectedPlot?.commute_time_to_city_center_min} mins) to IT hubs`,
      `What top schools and hospitals are within ${selectedPlot?.nearest_hospital_km}km?`
    ],
    investor: [
      `Is the ${selectedPlot?.roi_percentage}% ROI sustainable over the next 5 years?`,
      `Compare ${selectedPlot?.current_price_sqft}/sqft price with ${selectedPlot?.locality} average`,
      `Impact of upcoming Metro & ORR infrastructure on appreciation`
    ]
  };

  const currentChips = recommendationChips[activeRole] || recommendationChips.builder;

  const handleResetChat = () => {
    setMessages([
      {
        sender: 'ai',
        text: `Chat reset. Analyzing **${selectedPlot?.name}** (${selectedPlot?.plot_id}) from your **${activeRole.toUpperCase()}** perspective. How can I assist you?`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
    ]);
  };

  const handleSendMessage = (textToSend = inputValue) => {
    const text = textToSend.trim();
    if (!text) return;

    const userMsg = {
      sender: 'user',
      text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputValue('');
    setIsTyping(true);

    setTimeout(() => {
      let aiResponseText = '';

      if (activeRole === 'builder') {
        aiResponseText = `Based on geotechnical analysis for **${selectedPlot.name}** (${selectedPlot.plot_id}):\n- **Foundation Strategy**: With a soil bearing capacity of **${selectedPlot.bearing_capacity_kpa} kPa** (${selectedPlot.soil_type}), deep raft foundation with micro-piles is recommended for up to **${selectedPlot.max_permissible_floors} floors**.\n- **Water Table**: Depth is recorded at **${selectedPlot.water_table_depth_m}m**, requiring standard sub-surface waterproofing for basement parking levels.\n- **Estimated Construction Cost**: Baseline structure cost is **₹${selectedPlot.construction_cost_estimate_per_sqft}/sqft** with full access to high-tension power line and storm drain grid.`;
      } else if (activeRole === 'homebuyer') {
        aiResponseText = `Here is your livability assessment for **${selectedPlot.name}** in **${selectedPlot.locality}**:\n- **Parks & Greenery**: Surrounding area features abundant parklands and eco-buffer zones ideal for residential living.\n- **Connectivity**: Commute time to the main business corridor is only **${selectedPlot.commute_time_to_city_center_min} minutes**.\n- **Social Infrastructure**: Excellent proximity with **${selectedPlot.schools_nearby} reputed schools** and hospital access within **${selectedPlot.nearest_hospital_km} km**.`;
      } else {
        aiResponseText = `Investment Analysis for **${selectedPlot.name}** (${selectedPlot.zoning_type} Zone):\n- **Appreciation Outlook**: Currently priced at **₹${selectedPlot.current_price_sqft}/sqft**, yielding a projected **5-year ROI of ${selectedPlot.roi_percentage}%**.\n- **Rental Yield**: Strong commercial/mixed rental yield of **${selectedPlot.rental_yield_percentage}%**.\n- **Catalysts**: Value driver supported by key pipeline projects: ${selectedPlot.infrastructure_development_pipeline.join(', ')}.`;
      }

      setMessages((prev) => [
        ...prev,
        {
          sender: 'ai',
          text: aiResponseText,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
      setIsTyping(false);
    }, 1000);
  };

  return (
    <div id="ai-advisor-section" className="w-full glass-panel rounded-2xl border border-forest-600/20 p-4 lg:p-5 shadow-sm flex flex-col space-y-4">
      
      {/* AI Assistant Title Bar */}
      <div className="flex items-center justify-between border-b border-sage-300/60 pb-3">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-xl bg-forest-800 shadow-sm text-beige-100">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="text-base font-extrabold text-forest-950">
                GeoPulse AI Advisor
              </h3>
              <span className="px-2 py-0.5 text-[10px] font-extrabold text-forest-950 bg-sage-200 border border-sage-400/50 rounded-md">
                Spatial Engine v2.0
              </span>
            </div>
            <p className="text-xs text-forest-700 font-medium">
              Context-Aware Real Estate Reasoning • Active Parcel: <strong className="text-forest-950">{selectedPlot.name}</strong>
            </p>
          </div>
        </div>

        {/* Role Quick Switcher Pills & Reset Chat */}
        <div className="flex items-center space-x-2">
          <div className="hidden sm:flex items-center space-x-1.5 bg-beige-200 p-1 rounded-xl border border-sage-300">
            <button
              onClick={() => setActiveRole('builder')}
              className={`px-2.5 py-1 rounded-lg text-xs font-bold transition-all flex items-center space-x-1 ${
                activeRole === 'builder'
                  ? 'bg-forest-800 text-beige-100 shadow'
                  : 'text-forest-800 hover:text-forest-950'
              }`}
            >
              <HardHat className="w-3.5 h-3.5" />
              <span>Builder</span>
            </button>

            <button
              onClick={() => setActiveRole('homebuyer')}
              className={`px-2.5 py-1 rounded-lg text-xs font-bold transition-all flex items-center space-x-1 ${
                activeRole === 'homebuyer'
                  ? 'bg-sage-700 text-beige-100 shadow'
                  : 'text-forest-800 hover:text-forest-950'
              }`}
            >
              <Home className="w-3.5 h-3.5" />
              <span>Homebuyer</span>
            </button>

            <button
              onClick={() => setActiveRole('investor')}
              className={`px-2.5 py-1 rounded-lg text-xs font-bold transition-all flex items-center space-x-1 ${
                activeRole === 'investor'
                  ? 'bg-olive-700 text-beige-100 shadow'
                  : 'text-forest-800 hover:text-forest-950'
              }`}
            >
              <TrendingUp className="w-3.5 h-3.5" />
              <span>Investor</span>
            </button>
          </div>

          <button
            onClick={handleResetChat}
            className="p-2 rounded-xl bg-beige-200 hover:bg-beige-300 text-forest-800 hover:text-forest-950 border border-sage-300 transition-all cursor-pointer"
            title="Reset Conversation"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Chat Messages Box */}
      <div ref={chatContainerRef} className="h-[220px] overflow-y-auto pr-2 space-y-3 bg-beige-100/90 p-4 rounded-xl border border-sage-300/60">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex items-start space-x-3 ${
              msg.sender === 'user' ? 'flex-row-reverse space-x-reverse' : ''
            }`}
          >
            <div
              className={`w-7 h-7 rounded-lg flex items-center justify-center text-xs font-bold shrink-0 ${
                msg.sender === 'user'
                  ? 'bg-beige-300 text-forest-950 shadow-xs'
                  : 'bg-forest-800 text-beige-100 shadow-xs'
              }`}
            >
              {msg.sender === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
            </div>

            <div
              className={`max-w-[85%] p-3 rounded-2xl text-xs leading-relaxed font-medium ${
                msg.sender === 'user'
                  ? 'bg-beige-200 text-forest-950 border border-sage-300/60 rounded-tr-none'
                  : 'bg-sage-200 text-forest-950 border border-sage-400/60 rounded-tl-none'
              }`}
            >
              <div>{renderFormattedText(msg.text)}</div>
              <div className="text-[9px] text-forest-700 mt-1 text-right font-bold">{msg.timestamp}</div>
            </div>
          </div>
        ))}

        {isTyping && (
          <div className="flex items-center space-x-2 text-xs text-forest-800 font-bold italic">
            <Bot className="w-4 h-4 animate-spin text-forest-700" />
            <span>GeoPulse AI is thinking...</span>
          </div>
        )}
      </div>

      {/* Role Recommendation Chips */}
      <div>
        <div className="text-[11px] font-extrabold text-forest-800 mb-2 flex items-center space-x-1.5">
          <Sparkles className="w-3.5 h-3.5 text-forest-700" />
          <span className="capitalize">{activeRole} Recommendation Prompts:</span>
        </div>
        <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-none">
          {currentChips.map((chip, idx) => (
            <button
              key={idx}
              onClick={() => handleSendMessage(chip)}
              className="px-3 py-1.5 rounded-xl text-xs font-extrabold bg-beige-200 hover:bg-sage-200 text-forest-950 border border-sage-300/80 transition-all whitespace-nowrap shrink-0 flex items-center space-x-1 cursor-pointer"
            >
              <span>{chip}</span>
              <ChevronRight className="w-3 h-3 text-forest-700" />
            </button>
          ))}
        </div>
      </div>

      {/* Input Box Bar */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSendMessage();
        }}
        className="relative flex items-center"
      >
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder={`Ask any custom question about ${selectedPlot?.name} or locality...`}
          className="w-full pl-4 pr-12 py-3 rounded-xl text-xs glass-input focus:ring-1 focus:ring-forest-600 transition-all placeholder:text-forest-700/60 font-semibold"
        />
        <button
          type="submit"
          disabled={!inputValue.trim()}
          className="absolute right-2 p-2 rounded-lg bg-forest-800 hover:bg-forest-900 disabled:opacity-40 text-beige-100 font-bold transition-all shadow-sm cursor-pointer"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>

    </div>
  );
}
