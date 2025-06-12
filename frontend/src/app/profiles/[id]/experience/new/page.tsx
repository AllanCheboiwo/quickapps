'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useRequireAuth } from '@/hooks/use-auth'
import { experienceApi } from '@/lib/api'
import type { ExperienceCreate } from '@/types'
import { ArrowLeft, Briefcase, CalendarDays, Loader2 } from 'lucide-react'

const experienceSchema = z.object({
  company: z.string().min(1, 'Company name is required'),
  position: z.string().min(1, 'Position is required'),
  start_date: z.string().min(1, 'Start date is required')
    .regex(/^\d{4}-\d{2}-\d{2}$/, 'Date must be YYYY-MM-DD'),
  end_date: z.string().optional().nullable()
    .refine(val => !val || val === '' || /^\d{4}-\d{2}-\d{2}$/.test(val), {message: 'Date must be YYYY-MM-DD or empty'}),
  description: z.string().optional().nullable(),
});

type ExperienceFormValues = z.infer<typeof experienceSchema>;

export default function AddExperiencePage() {
  const { isAuthenticated, isLoading: authLoading } = useRequireAuth();
  const params = useParams();
  const router = useRouter();
  const queryClient = useQueryClient();
  const profileId = parseInt(params.id as string);

  const [apiError, setApiError] = useState<string | null>(null);

  const form = useForm<ExperienceFormValues>({
    resolver: zodResolver(experienceSchema),
    defaultValues: {
      company: '',
      position: '',
      start_date: '',
      end_date: '',
      description: '',
    },
  });

  const createExperienceMutation = useMutation({
    mutationFn: (data: ExperienceCreate) => experienceApi.createExperience(profileId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['experiences', profileId] });
      queryClient.invalidateQueries({ queryKey: ['profile', profileId] });
      router.push(`/profiles/${profileId}/builder`);
    },
    onError: (error: any) => {
      setApiError(error.response?.data?.detail || 'Failed to add experience. Please try again.');
    },
  });

  const onSubmit = (data: ExperienceFormValues) => {
    setApiError(null);
    const finalEndDate = (data.end_date === '' || data.end_date === null || data.end_date === undefined) 
      ? undefined 
      : data.end_date;
      
    const payload: ExperienceCreate = {
      company: data.company,
      position: data.position,
      start_date: data.start_date,
      end_date: finalEndDate,
      description: data.description || undefined,
    };
    createExperienceMutation.mutate(payload);
  };

  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
      </div>
    );
  }

  if (!isAuthenticated || isNaN(profileId)) {
    router.push('/auth');
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <Link 
                href={`/profiles/${profileId}/builder`}
                className="inline-flex items-center text-gray-600 hover:text-gray-900 mr-4 transition-colors"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Profile Builder
              </Link>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Card>
          <CardHeader>
            <div className="flex items-center">
              <Briefcase className="h-6 w-6 mr-2 text-primary-600" />
              <CardTitle className="text-2xl">Add New Experience</CardTitle>
            </div>
            <CardDescription>
              Detail your professional roles and responsibilities.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {apiError && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-md">
                <p>{apiError}</p>
              </div>
            )}
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              <div>
                <label htmlFor="company" className="block text-sm font-medium text-gray-700 mb-1">Company Name *</label>
                <Input 
                  id="company" 
                  {...form.register('company')} 
                  placeholder="e.g., Google, Microsoft"
                />
                {form.formState.errors.company && (
                  <p className="text-sm text-red-600 mt-1">{form.formState.errors.company.message}</p>
                )}
              </div>

              <div>
                <label htmlFor="position" className="block text-sm font-medium text-gray-700 mb-1">Position / Title *</label>
                <Input 
                  id="position" 
                  {...form.register('position')} 
                  placeholder="e.g., Software Engineer, Product Manager"
                />
                {form.formState.errors.position && (
                  <p className="text-sm text-red-600 mt-1">{form.formState.errors.position.message}</p>
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label htmlFor="start_date" className="block text-sm font-medium text-gray-700 mb-1">Start Date (YYYY-MM-DD) *</label>
                  <div className="relative">
                    <Input 
                      id="start_date" 
                      type="date"
                      {...form.register('start_date')} 
                    />
                     <CalendarDays className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400 pointer-events-none" />
                  </div>
                  {form.formState.errors.start_date && (
                    <p className="text-sm text-red-600 mt-1">{form.formState.errors.start_date.message}</p>
                  )}
                </div>
                <div>
                  <label htmlFor="end_date" className="block text-sm font-medium text-gray-700 mb-1">End Date (YYYY-MM-DD or empty)</label>
                   <div className="relative">
                    <Input 
                      id="end_date" 
                      type="date"
                      {...form.register('end_date')} 
                    />
                    <CalendarDays className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400 pointer-events-none" />
                  </div>
                  {form.formState.errors.end_date && (
                    <p className="text-sm text-red-600 mt-1">{form.formState.errors.end_date.message}</p>
                  )}
                </div>
              </div>

              <div>
                <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea 
                  id="description" 
                  {...form.register('description')} 
                  placeholder="Describe your responsibilities, achievements, and skills used. (Optional)"
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm p-2 border h-auto"
                  rows={5}
                />
                {form.formState.errors.description && (
                  <p className="text-sm text-red-600 mt-1">{form.formState.errors.description.message}</p>
                )}
              </div>

              <div className="flex justify-end space-x-3">
                <Button 
                  type="button" 
                  variant="outline"
                  onClick={() => router.push(`/profiles/${profileId}/builder`)}
                  disabled={createExperienceMutation.isPending}
                >
                  Cancel
                </Button>
                <Button type="submit" disabled={createExperienceMutation.isPending} className="min-w-[120px]">
                  {createExperienceMutation.isPending ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    'Save Experience'
                  )}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </main>
    </div>
  );
} 