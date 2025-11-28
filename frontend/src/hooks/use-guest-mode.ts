'use client';

import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/stores/auth';
import { authApi } from '@/lib/api';
import Cookies from 'js-cookie';

export const useGuestMode = () => {
  const router = useRouter();
  const { setUser } = useAuthStore();

  const startGuestMode = async () => {
    try {
      const response = await fetch('/api/auth/guest-login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to start guest mode');
      }

      const data = await response.json();
      const { access_token } = data;

      // 2. Save token to cookies (same as regular login)
      Cookies.set('access_token', access_token, {
        path: '/',
      });

      // 3. Fetch user profile using the auth API
      const user = await authApi.getCurrentUser();

      // 4. Update auth store
      setUser(user);

      // 5. Redirect to dashboard
      router.push('/dashboard');
    } catch (error) {
      console.error('Guest login failed:', error);
      throw error;
    }
  };

  return { startGuestMode };
};

