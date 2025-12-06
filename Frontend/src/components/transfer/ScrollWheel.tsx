import { useRef, useState, useEffect } from 'react';

interface ScrollWheelProps {
  value: number;
  onChange: (value: number) => void;
  min: number;
  max: number;
  step: number;
}

export function ScrollWheel({ value, onChange, min, max, step }: ScrollWheelProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [startX, setStartX] = useState(0);
  const [scrollLeft, setScrollLeft] = useState(0);

  const values = [];
  for (let i = min; i <= max; i += step) {
    values.push(i);
  }

  useEffect(() => {
    if (scrollRef.current) {
      const index = values.indexOf(value);
      const itemWidth = 80;
      const containerWidth = scrollRef.current.offsetWidth;
      const scrollPosition = index * itemWidth - containerWidth / 2 + itemWidth / 2;
      scrollRef.current.scrollLeft = scrollPosition;
    }
  }, [value]);

  const handleMouseDown = (e: React.MouseEvent) => {
    if (!scrollRef.current) return;
    setIsDragging(true);
    setStartX(e.pageX - scrollRef.current.offsetLeft);
    setScrollLeft(scrollRef.current.scrollLeft);
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging || !scrollRef.current) return;
    e.preventDefault();
    const x = e.pageX - scrollRef.current.offsetLeft;
    const walk = (x - startX) * 2;
    scrollRef.current.scrollLeft = scrollLeft - walk;
  };

  const handleMouseUp = () => {
    setIsDragging(false);
    snapToNearest();
  };

  const handleTouchStart = (e: React.TouchEvent) => {
    if (!scrollRef.current) return;
    setIsDragging(true);
    setStartX(e.touches[0].pageX - scrollRef.current.offsetLeft);
    setScrollLeft(scrollRef.current.scrollLeft);
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    if (!isDragging || !scrollRef.current) return;
    const x = e.touches[0].pageX - scrollRef.current.offsetLeft;
    const walk = (x - startX) * 2;
    scrollRef.current.scrollLeft = scrollLeft - walk;
  };

  const handleTouchEnd = () => {
    setIsDragging(false);
    snapToNearest();
  };

  const snapToNearest = () => {
    if (!scrollRef.current) return;
    const itemWidth = 80;
    const containerWidth = scrollRef.current.offsetWidth;
    const scrollPosition = scrollRef.current.scrollLeft + containerWidth / 2;
    const index = Math.round(scrollPosition / itemWidth);
    const clampedIndex = Math.max(0, Math.min(index, values.length - 1));
    onChange(values[clampedIndex]);
  };

  return (
    <div className="relative bg-gray-100 rounded-2xl py-8 overflow-hidden">
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-10">
        <div className="w-20 h-16 border-2 border-indigo-600 rounded-xl bg-indigo-50/50"></div>
      </div>

      <div
        ref={scrollRef}
        className="flex gap-2 overflow-x-auto scrollbar-hide cursor-grab active:cursor-grabbing px-[calc(50%-40px)]"
        style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
      >
        {values.map((val, index) => (
          <div
            key={index}
            className="flex-shrink-0 w-20 h-16 flex items-center justify-center select-none"
            onClick={() => onChange(val)}
          >
            <span
              className={`text-2xl transition-all ${
                val === value
                  ? 'text-indigo-600 scale-125'
                  : 'text-gray-400 scale-100'
              }`}
            >
              {val}
            </span>
          </div>
        ))}
      </div>

      <p className="text-center text-sm text-gray-500 mt-4">
        Swipe to select amount
      </p>
    </div>
  );
}
