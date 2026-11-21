import React, { useState, useEffect, useRef } from 'react';
import { Play, Pause, ChevronLeft, ChevronRight, Calendar, FastForward } from 'lucide-react';

export default function ReplayControls({
  dates = [],
  selectedDate,
  onSelectDate,
  isLoading
}) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [speed, setSpeed] = useState(1); // 1 = 2000ms, 2 = 1000ms
  const timerRef = useRef(null);

  const currentIndex = dates.indexOf(selectedDate);
  const totalDates = dates.length;

  const handlePrev = () => {
    if (currentIndex > 0) {
      onSelectDate(dates[currentIndex - 1]);
    }
  };

  const handleNext = () => {
    if (currentIndex < totalDates - 1) {
      onSelectDate(dates[currentIndex + 1]);
    } else {
      // Loop back to start if playing
      onSelectDate(dates[0]);
    }
  };

  // Autoplay loop
  useEffect(() => {
    if (isPlaying && totalDates > 0) {
      const intervalMs = speed === 2 ? 1000 : 2000;
      timerRef.current = setInterval(() => {
        onSelectDate((prevDate) => {
          const idx = dates.indexOf(prevDate);
          if (idx >= 0 && idx < dates.length - 1) {
            return dates[idx + 1];
          } else {
            return dates[0]; // Loop
          }
        });
      }, intervalMs);
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
    }

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isPlaying, speed, dates, onSelectDate, totalDates]);

  // Pause if user manually changes date or error occurs
  const togglePlay = () => {
    setIsPlaying(!isPlaying);
  };

  return (
    <div className="card-base p-2.5 flex flex-wrap items-center justify-between gap-3 bg-[#111827] border-white/10">
      {/* Left: Playback & Step Controls */}
      <div className="flex items-center gap-1.5">
        <button
          onClick={togglePlay}
          className={`px-3 py-1.5 rounded-md font-semibold text-xs flex items-center gap-1.5 transition-all ${
            isPlaying
              ? 'bg-amber-600/80 text-white hover:bg-amber-600 border border-amber-400/40'
              : 'btn-primary'
          }`}
          title={isPlaying ? 'Pause historical replay' : 'Autoplay through historical sequence'}
          disabled={isLoading || totalDates === 0}
        >
          {isPlaying ? (
            <>
              <Pause size={13} />
              <span>PAUSE</span>
            </>
          ) : (
            <>
              <Play size={13} />
              <span>PLAY REPLAY</span>
            </>
          )}
        </button>

        <button
          onClick={handlePrev}
          disabled={currentIndex <= 0 || isLoading}
          className="btn-secondary text-xs px-2.5 py-1.5"
          title="Previous day"
        >
          <ChevronLeft size={14} />
        </button>

        <button
          onClick={handleNext}
          disabled={isLoading || totalDates === 0}
          className="btn-secondary text-xs px-2.5 py-1.5"
          title="Next day"
        >
          <ChevronRight size={14} />
        </button>

        {/* Speed toggle */}
        <button
          onClick={() => setSpeed(speed === 1 ? 2 : 1)}
          className="btn-ghost text-xs px-2 py-1 text-slate-400 hover:text-white"
          title={`Replay speed: ${speed}x`}
        >
          <FastForward size={12} className={speed === 2 ? 'text-sky-400' : 'text-slate-500'} />
          <span className="font-mono text-[11px]">{speed}x</span>
        </button>
      </div>

      {/* Middle: Active Date Display */}
      <div className="flex items-center gap-2">
        <Calendar size={14} className="text-amber-400" />
        <span className="font-mono text-base font-bold text-white tracking-wide">
          {selectedDate || 'Select Date'}
        </span>
        <span className="text-xs text-slate-400 font-mono">
          ({currentIndex >= 0 ? `Day ${currentIndex + 1} of ${totalDates}` : '—'})
        </span>
      </div>

      {/* Right: Quick Date Dropdown */}
      <div className="flex items-center gap-2">
        <label htmlFor="replay-date-select" className="text-xs text-slate-400">
          Jump to:
        </label>
        <select
          id="replay-date-select"
          value={selectedDate}
          onChange={(e) => {
            setIsPlaying(false);
            onSelectDate(e.target.value);
          }}
          disabled={isLoading || totalDates === 0}
          className="bg-[#1e293b] text-slate-200 border border-white/10 rounded-md px-2.5 py-1.5 text-xs font-mono focus:outline-none focus:border-sky-500 cursor-pointer"
        >
          {dates.map((d, i) => (
            <option key={d} value={d}>
              Day {i + 1}: {d}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}
