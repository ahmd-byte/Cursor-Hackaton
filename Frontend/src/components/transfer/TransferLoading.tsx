import { useEffect, useState } from 'react';
import { CheckCircle2, Loader2 } from 'lucide-react';

interface TransferLoadingProps {
  onComplete: () => void;
}

export function TransferLoading({ onComplete }: TransferLoadingProps) {
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState<'processing' | 'complete'>('processing');

  useEffect(() => {
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          setStatus('complete');
          setTimeout(() => {
            onComplete();
          }, 1500);
          return 100;
        }
        return prev + 10;
      });
    }, 200);

    return () => clearInterval(interval);
  }, [onComplete]);

  return (
    <div className="min-h-screen bg-gradient-to-b from-indigo-600 to-indigo-800 flex flex-col items-center justify-center p-6 text-white">
      <div className="text-center space-y-8">
        {status === 'processing' ? (
          <>
            <div className="w-24 h-24 mx-auto">
              <Loader2 className="w-24 h-24 animate-spin" />
            </div>
            <div>
              <h2 className="text-3xl mb-2">Processing Transfer</h2>
              <p className="text-indigo-200">
                Please wait while we process your request...
              </p>
            </div>
            <div className="w-full max-w-xs mx-auto">
              <div className="bg-white/20 rounded-full h-2 overflow-hidden">
                <div
                  className="bg-white h-full transition-all duration-300"
                  style={{ width: `${progress}%` }}
                ></div>
              </div>
              <p className="text-center mt-2 text-indigo-200">{progress}%</p>
            </div>
          </>
        ) : (
          <>
            <div className="w-24 h-24 mx-auto bg-green-500 rounded-full flex items-center justify-center">
              <CheckCircle2 className="w-16 h-16" />
            </div>
            <div>
              <h2 className="text-3xl mb-2">Transfer Successful!</h2>
              <p className="text-indigo-200">
                Your funds have been transferred successfully
              </p>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
