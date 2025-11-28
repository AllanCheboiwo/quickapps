'use client';

import { ArrowRight, Lock, Zap, Clock } from 'lucide-react';
import { useRouter } from 'next/navigation';

export const UpgradeCTA = () => {
  const router = useRouter();

  const benefits = [
    { icon: Zap, label: 'Unlimited profiles' },
    { icon: Zap, label: 'Unlimited resumes' },
    { icon: ArrowRight, label: 'Download & share' },
    { icon: Clock, label: 'Save forever' },
  ];

  return (
    <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg p-8 shadow-lg">
      <div className="flex items-start justify-between gap-6">
        <div className="flex-1">
          <h3 className="text-2xl font-bold mb-2">
            Ready for unlimited resumes?
          </h3>
          <p className="text-blue-100 mb-6">
            Create a free account to unlock all features and save your work forever.
          </p>

          <div className="grid grid-cols-2 gap-3 mb-6">
            {benefits.map((benefit, idx) => {
              const Icon = benefit.icon;
              return (
                <div key={idx} className="flex items-center gap-2">
                  <Icon className="w-4 h-4" />
                  <span className="text-sm">{benefit.label}</span>
                </div>
              );
            })}
          </div>

          <button
            onClick={() => router.push('/auth?tab=register')}
            className="bg-white text-blue-600 font-semibold py-3 px-6 rounded-lg hover:bg-blue-50 transition flex items-center gap-2"
          >
            Upgrade Now
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>

        <Lock className="w-16 h-16 text-blue-200 flex-shrink-0" />
      </div>
    </div>
  );
};

