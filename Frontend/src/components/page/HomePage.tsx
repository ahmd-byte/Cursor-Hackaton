import { ArrowUpRight, TrendingUp, PiggyBank } from 'lucide-react';
import { TierCarousel } from './TierCarousel';

interface HomePageProps {
  userData: {
    name: string;
    monthlySalary: number;
    amountSaved: number;
    amountTransferred: number;
  };
  onTransfer: () => void;
}

export function HomePage({ userData, onTransfer }: HomePageProps) {
  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  const buckets = [
    { name: 'Emergency Fund', amount: 450, color: 'bg-red-500' },
    { name: 'Vacation', amount: 320, color: 'bg-blue-500' },
    { name: 'New Phone', amount: 280, color: 'bg-green-500' },
    { name: 'Education', amount: 800, color: 'bg-purple-500' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-indigo-600 to-indigo-800 pb-24">
      <div className="p-6 text-white">
        <div className="flex items-center justify-between mb-8">
          <div>
            <p className="text-indigo-200">9:41</p>
          </div>
          <div className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5" />
          </div>
        </div>

        <div className="mb-8">
          <h1 className="text-2xl mb-1">{getGreeting()}.</h1>
          <p className="text-indigo-200">Let&apos;s step it up!</p>
        </div>

        {/* Salary Comparison Card */}
        <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-3xl p-6 mb-6">
          <div className="grid grid-cols-2 gap-6 mb-6">
            <div>
              <p className="text-indigo-200 text-sm mb-1">Amount Saved</p>
              <p className="text-3xl">RM {userData.amountSaved}</p>
            </div>
            <div>
              <p className="text-indigo-200 text-sm mb-1">Monthly Salary</p>
              <p className="text-3xl">RM {userData.monthlySalary}</p>
            </div>
          </div>
          
          <div className="text-center py-4 border-t border-white/20">
            <p className="text-indigo-200 text-sm mb-1">Amount Transferred</p>
            <p className="text-4xl">RM {userData.amountTransferred}</p>
          </div>

          <button
            onClick={onTransfer}
            className="w-full mt-4 bg-white text-indigo-600 py-3 rounded-full flex items-center justify-center gap-2 hover:bg-indigo-50 transition-colors"
          >
            Transfer Now
            <ArrowUpRight className="w-5 h-5" />
          </button>
        </div>

        {/* Tier Membership Carousel */}
        <div className="mb-6">
          <h2 className="text-xl mb-4">Membership Tiers</h2>
          <TierCarousel />
        </div>

        {/* Buckets Section */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl">Savings Buckets</h2>
            <PiggyBank className="w-5 h-5" />
          </div>
          
          <div className="grid grid-cols-2 gap-3">
            {buckets.map((bucket, index) => (
              <div
                key={index}
                className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-2xl p-4"
              >
                <div className={`w-10 h-10 ${bucket.color} rounded-full mb-3`}></div>
                <p className="text-sm text-indigo-200 mb-1">{bucket.name}</p>
                <p className="text-xl">RM {bucket.amount}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
