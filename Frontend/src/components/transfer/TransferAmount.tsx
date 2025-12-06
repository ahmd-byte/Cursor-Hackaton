import { useState } from 'react';
import { ArrowLeft } from 'lucide-react';
import { ScrollWheel } from './ScrollWheel';

interface TransferAmountProps {
  onConfirm: (amount: number) => void;
  onBack: () => void;
}

export function TransferAmount({ onConfirm, onBack }: TransferAmountProps) {
  const [selectedAmount, setSelectedAmount] = useState(80);

  const getAmount = selectedAmount;
  const saveAmount = Math.round(selectedAmount * 0.20); // 20% goes to savings
  const transferAmount = selectedAmount - saveAmount;

  return (
    <div className="min-h-screen bg-white flex flex-col">
      <div className="p-6">
        <button
          onClick={onBack}
          className="flex items-center gap-2 text-gray-600 mb-8"
        >
          <ArrowLeft className="w-5 h-5" />
          Back
        </button>

        <h1 className="text-3xl mb-2">Transfer Amount</h1>
        <p className="text-gray-600 mb-8">
          Select how much you want to access from your earned wages
        </p>
      </div>

      <div className="flex-1 flex flex-col items-center justify-center px-6">
        <div className="w-full max-w-sm bg-gray-50 rounded-3xl p-8 mb-8">
          <div className="grid grid-cols-2 gap-8 mb-8">
            <div className="text-center">
              <p className="text-gray-600 mb-2">Get</p>
              <p className="text-6xl">{transferAmount}</p>
            </div>
            <div className="text-center">
              <p className="text-gray-600 mb-2">Save</p>
              <p className="text-6xl">{saveAmount}</p>
            </div>
          </div>

          <div className="text-center py-4 border-t border-gray-200">
            <p className="text-2xl">= RM {getAmount}</p>
          </div>
        </div>

        <div className="w-full max-w-sm mb-8">
          <ScrollWheel
            value={selectedAmount}
            onChange={setSelectedAmount}
            min={20}
            max={1200}
            step={10}
          />
        </div>
      </div>

      <div className="p-6">
        <button
          onClick={() => onConfirm(transferAmount)}
          className="w-full bg-indigo-600 text-white py-4 rounded-full hover:bg-indigo-700 transition-colors"
        >
          Transfer Now
        </button>
        <p className="text-center text-sm text-gray-500 mt-4">
          RM {saveAmount} will be automatically saved to your bucket
        </p>
      </div>
    </div>
  );
}
