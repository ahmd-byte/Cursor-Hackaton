import { useState } from 'react';
import { Plus, ArrowRight, PiggyBank, Plane, Smartphone, GraduationCap, Home, Heart } from 'lucide-react';

interface Bucket {
  id: string;
  name: string;
  amount: number;
  target: number;
  color: string;
  icon: string;
}

export function Buckets() {
  const [buckets, setBuckets] = useState<Bucket[]>([
    {
      id: '1',
      name: 'Emergency Fund',
      amount: 450,
      target: 5000,
      color: 'bg-red-500',
      icon: 'piggy',
    },
    {
      id: '2',
      name: 'Vacation',
      amount: 320,
      target: 3000,
      color: 'bg-blue-500',
      icon: 'plane',
    },
    {
      id: '3',
      name: 'New Phone',
      amount: 280,
      target: 2500,
      color: 'bg-green-500',
      icon: 'phone',
    },
    {
      id: '4',
      name: 'Education',
      amount: 800,
      target: 4000,
      color: 'bg-purple-500',
      icon: 'education',
    },
    {
      id: '5',
      name: 'House Deposit',
      amount: 1200,
      target: 20000,
      color: 'bg-orange-500',
      icon: 'home',
    },
    {
      id: '6',
      name: 'Medical Fund',
      amount: 150,
      target: 1000,
      color: 'bg-pink-500',
      icon: 'heart',
    },
  ]);

  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedBucket, setSelectedBucket] = useState<Bucket | null>(null);

  const getIcon = (iconName: string) => {
    const icons = {
      piggy: PiggyBank,
      plane: Plane,
      phone: Smartphone,
      education: GraduationCap,
      home: Home,
      heart: Heart,
    };
    return icons[iconName as keyof typeof icons] || PiggyBank;
  };

  const totalSaved = buckets.reduce((sum, bucket) => sum + bucket.amount, 0);

  return (
    <div className="min-h-screen bg-gradient-to-b from-indigo-600 to-indigo-800 pb-24">
      <div className="p-6 text-white">
        <div className="mb-8">
          <h1 className="text-3xl mb-2">Savings Buckets</h1>
          <p className="text-indigo-200">
            Organize your savings goals and track progress
          </p>
        </div>

        <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-3xl p-6 mb-6">
          <p className="text-indigo-200 text-sm mb-1">Total Saved</p>
          <p className="text-4xl mb-4">RM {totalSaved}</p>
          <div className="flex items-center justify-between text-sm">
            <span className="text-indigo-200">{buckets.length} active buckets</span>
            <button
              onClick={() => setShowAddModal(true)}
              className="flex items-center gap-1 bg-white/20 px-3 py-1 rounded-full hover:bg-white/30 transition-colors"
            >
              <Plus className="w-4 h-4" />
              Add New
            </button>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          {buckets.map((bucket) => {
            const Icon = getIcon(bucket.icon);
            const progress = (bucket.amount / bucket.target) * 100;

            return (
              <div
                key={bucket.id}
                onClick={() => setSelectedBucket(bucket)}
                className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-2xl p-4 cursor-pointer hover:bg-white/20 transition-colors"
              >
                <div className={`w-12 h-12 ${bucket.color} rounded-full flex items-center justify-center mb-3`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="mb-1">{bucket.name}</h3>
                <p className="text-2xl mb-2">RM {bucket.amount}</p>
                <div className="mb-2">
                  <div className="bg-white/20 rounded-full h-2 overflow-hidden">
                    <div
                      className="bg-white h-full transition-all"
                      style={{ width: `${Math.min(progress, 100)}%` }}
                    ></div>
                  </div>
                </div>
                <p className="text-xs text-indigo-200">
                  {Math.round(progress)}% of RM {bucket.target}
                </p>
              </div>
            );
          })}
        </div>
      </div>

      {selectedBucket && (
        <div
          className="fixed inset-0 bg-black/50 flex items-end justify-center z-50"
          onClick={() => setSelectedBucket(null)}
        >
          <div
            className="bg-white rounded-t-3xl w-full max-w-md p-6 space-y-4"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="w-12 h-1 bg-gray-300 rounded-full mx-auto mb-4"></div>
            
            <div className="flex items-center gap-3 mb-6">
              {(() => {
                const Icon = getIcon(selectedBucket.icon);
                return (
                  <div className={`w-16 h-16 ${selectedBucket.color} rounded-full flex items-center justify-center`}>
                    <Icon className="w-8 h-8 text-white" />
                  </div>
                );
              })()}
              <div>
                <h2 className="text-2xl">{selectedBucket.name}</h2>
                <p className="text-gray-600">
                  RM {selectedBucket.amount} / RM {selectedBucket.target}
                </p>
              </div>
            </div>

            <div className="bg-gray-50 rounded-2xl p-4">
              <div className="flex justify-between mb-2">
                <span className="text-gray-600">Progress</span>
                <span className="text-gray-900">
                  {Math.round((selectedBucket.amount / selectedBucket.target) * 100)}%
                </span>
              </div>
              <div className="bg-gray-200 rounded-full h-3 overflow-hidden">
                <div
                  className={`${selectedBucket.color} h-full transition-all`}
                  style={{
                    width: `${Math.min((selectedBucket.amount / selectedBucket.target) * 100, 100)}%`,
                  }}
                ></div>
              </div>
            </div>

            <div className="space-y-3">
              <button className="w-full bg-indigo-600 text-white py-4 rounded-full hover:bg-indigo-700 transition-colors flex items-center justify-center gap-2">
                Add Money
                <ArrowRight className="w-5 h-5" />
              </button>
              <button
                onClick={() => setSelectedBucket(null)}
                className="w-full bg-gray-100 text-gray-700 py-4 rounded-full hover:bg-gray-200 transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {showAddModal && (
        <div
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-6"
          onClick={() => setShowAddModal(false)}
        >
          <div
            className="bg-white rounded-3xl w-full max-w-md p-6 space-y-4"
            onClick={(e) => e.stopPropagation()}
          >
            <h2 className="text-2xl mb-4">Create New Bucket</h2>
            
            <div>
              <label className="block text-sm text-gray-600 mb-2">Bucket Name</label>
              <input
                type="text"
                placeholder="e.g., Wedding Fund"
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:border-indigo-600"
              />
            </div>

            <div>
              <label className="block text-sm text-gray-600 mb-2">Target Amount (RM)</label>
              <input
                type="number"
                placeholder="5000"
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:border-indigo-600"
              />
            </div>

            <div className="flex gap-3">
              <button className="flex-1 bg-indigo-600 text-white py-3 rounded-full hover:bg-indigo-700 transition-colors">
                Create Bucket
              </button>
              <button
                onClick={() => setShowAddModal(false)}
                className="flex-1 bg-gray-100 text-gray-700 py-3 rounded-full hover:bg-gray-200 transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
