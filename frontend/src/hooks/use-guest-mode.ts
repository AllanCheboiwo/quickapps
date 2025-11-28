'use client';

import { useRouter } from 'next/navigation';
import { useAuth } from './use-auth';

export const useGuestMode = () => {
  const router = useRouter();
  const { setToken, setUser } = useAuth();

  const startGuestMode = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
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

      // Save token to localStorage
      localStorage.setItem('token', access_token);
      localStorage.setItem('is_guest', 'true');

      // Update auth store
      setToken(access_token);

      // Fetch user profile
      const userResponse = await fetch(`${apiUrl}/auth/me`, {
        headers: {
          Authorization: `Bearer ${access_token}`,
        },
      });

      if (userResponse.ok) {
        const user = await userResponse.json();
        setUser(user);
      }

      // Redirect to dashboard
      router.push('/dashboard');
    } catch (error) {
      console.error('Guest login failed:', error);
      throw error;
    }
  };

  return { startGuestMode };
};

