import { ArrowRight } from 'lucide-react';

interface WelcomeProps {
  onNext: () => void;
}

export function Welcome({ onNext }: WelcomeProps) {
  return (
    <div className="min-h-screen bg-gradient-to-b from-indigo-600 to-indigo-800 flex flex-col items-center justify-center p-6 text-white">
      <div className="w-full max-w-sm space-y-8">
        <div className="text-center space-y-4">
          <div className="w-20 h-20 bg-white rounded-full mx-auto flex items-center justify-center">
            <span className="text-indigo-600 text-3xl">💰</span>
          </div>
          <h1 className="text-4xl">
            Early Wage Access
          </h1>
          <p className="text-indigo-200">
            Get paid as you earn. Access your wages before payday.
          </p>
        </div>

        <div className="space-y-4">
          <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
            <h3 className="text-xl mb-2">🚀 Instant Access</h3>
            <p className="text-indigo-200 text-sm">
              Access up to 50% of your earned wages instantly
            </p>
          </div>

          <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
            <h3 className="text-xl mb-2">💡 Smart Savings</h3>
            <p className="text-indigo-200 text-sm">
              Automatically save a portion of every transfer
            </p>
          </div>

          <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
            <h3 className="text-xl mb-2">🤖 AI Assistant</h3>
            <p className="text-indigo-200 text-sm">
              Get personalized financial advice and budgeting tips
            </p>
          </div>
        </div>

        <button
          onClick={onNext}
          className="w-full bg-white text-indigo-600 py-4 rounded-full flex items-center justify-center gap-2 hover:bg-indigo-50 transition-colors"
        >
          Get Started
          <ArrowRight className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
}
