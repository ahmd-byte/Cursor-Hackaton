import { useState, useEffect } from 'react';
import { Crown, Star, Zap, ChevronLeft, ChevronRight } from 'lucide-react';

export function TierCarousel() {
  const [currentSlide, setCurrentSlide] = useState(0);

  const tiers = [
    {
      name: 'Basic',
      icon: Star,
      color: 'from-gray-400 to-gray-600',
      benefits: [
        'Access up to 30% of earned wages',
        'Standard processing time',
        'Basic savings features',
      ],
      price: 'Free',
    },
    {
      name: 'Premium',
      icon: Zap,
      color: 'from-blue-400 to-blue-600',
      benefits: [
        'Access up to 50% of earned wages',
        'Instant transfers',
        'AI financial advisor',
        'Advanced savings buckets',
      ],
      price: 'RM 11.99/year',
    },
    {
      name: 'Elite',
      icon: Crown,
      color: 'from-yellow-400 to-yellow-600',
      benefits: [
        'Access up to 70% of earned wages',
        'Priority support 24/7',
        'Exclusive investment opportunities',
        'Personal finance coaching',
      ],
      price: 'RM 29.99/year',
    },
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % tiers.length);
    }, 5000);
    return () => clearInterval(interval);
  }, [tiers.length]);

  const nextSlide = () => {
    setCurrentSlide((prev) => (prev + 1) % tiers.length);
  };

  const prevSlide = () => {
    setCurrentSlide((prev) => (prev - 1 + tiers.length) % tiers.length);
  };

  return (
    <div className="relative">
      <div className="overflow-hidden">
        <div
          className="flex transition-transform duration-500 ease-in-out"
          style={{ transform: `translateX(-${currentSlide * 100}%)` }}
        >
          {tiers.map((tier, index) => {
            const Icon = tier.icon;
            return (
              <div key={index} className="w-full flex-shrink-0 px-2">
                <div
                  className={`bg-gradient-to-br ${tier.color} rounded-3xl p-6 text-white`}
                >
                  <div className="flex items-center gap-3 mb-4">
                    <Icon className="w-8 h-8" />
                    <div>
                      <h3 className="text-2xl">{tier.name}</h3>
                      <p className="text-sm opacity-90">{tier.price}</p>
                    </div>
                  </div>
                  
                  <ul className="space-y-2 mb-6">
                    {tier.benefits.map((benefit, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm">
                        <span className="mt-1">✓</span>
                        <span>{benefit}</span>
                      </li>
                    ))}
                  </ul>

                  <button className="w-full bg-white text-gray-800 py-3 rounded-full hover:bg-gray-100 transition-colors">
                    {index === 0 ? 'Current Plan' : 'Upgrade Now'}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <button
        onClick={prevSlide}
        className="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-2 w-10 h-10 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center hover:bg-white/30 transition-colors"
      >
        <ChevronLeft className="w-5 h-5 text-white" />
      </button>

      <button
        onClick={nextSlide}
        className="absolute right-0 top-1/2 -translate-y-1/2 translate-x-2 w-10 h-10 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center hover:bg-white/30 transition-colors"
      >
        <ChevronRight className="w-5 h-5 text-white" />
      </button>

      <div className="flex justify-center gap-2 mt-4">
        {tiers.map((_, index) => (
          <button
            key={index}
            onClick={() => setCurrentSlide(index)}
            className={`w-2 h-2 rounded-full transition-all ${
              index === currentSlide
                ? 'bg-white w-6'
                : 'bg-white/30'
            }`}
          />
        ))}
      </div>
    </div>
  );
}