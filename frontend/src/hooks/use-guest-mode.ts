'use client';

import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/stores/auth';
import Cookies from 'js-cookie';

export const useGuestMode = () => {
  const router = useRouter();
  const { setUser } = useAuthStore();

  const startGuestMode = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      
      // 1. Call guest login endpoint
      const response = await fetch(`${apiUrl}/auth/guest-login`, {
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
        secure: true,
        sameSite: 'Strict',
        path: '/',
      });

      // 3. Fetch user profile
      const userResponse = await fetch(`${apiUrl}/auth/me`, {
        headers: {
          Authorization: `Bearer ${access_token}`,
        },
      });

      if (!userResponse.ok) {
        throw new Error('Failed to fetch user profile');
      }

      const user = await userResponse.json();

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

