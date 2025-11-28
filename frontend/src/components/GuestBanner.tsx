'use client';

import { AlertCircle, Zap } from 'lucide-react';
import { useRouter } from 'next/navigation';

interface GuestBannerProps {
  isGuest: boolean;
  daysRemaining?: number;
  resumesUsed?: number;
  maxResumes?: number;
}

export const GuestBanner = ({
  isGuest,
  daysRemaining = 7,
  resumesUsed = 0,
  maxResumes = 1,
}: GuestBannerProps) => {
  const router = useRouter();

  if (!isGuest) return null;

  return (
    <div className="space-y-3 mb-6">
      {/* Main guest badge */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <Zap className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
          <div className="flex-1">
            <h3 className="font-semibold text-blue-900 mb-1">
              ✨ Guest Account - 7 Day Trial
            </h3>
            <p className="text-sm text-blue-800 mb-3">
              You're trying QuickApps as a guest! Your data will be deleted after{' '}
              <strong>{daysRemaining} days</strong>.
            </p>
            <button
              onClick={() => router.push('/auth?tab=register')}
              className="text-sm font-medium text-blue-600 hover:text-blue-700 underline"
            >
              Create account to save your work permanently →
            </button>
          </div>
        </div>
      </div>

      {/* Resume usage warning */}
      {resumesUsed >= maxResumes && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-yellow-600 mt-0.5 flex-shrink-0" />
          <div>
            <p className="text-sm font-medium text-yellow-900">
              Daily limit reached!
            </p>
            <p className="text-sm text-yellow-800">
              You've used your {maxResumes} free resume today. Create an account for{' '}
              <strong>unlimited resumes</strong>.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

