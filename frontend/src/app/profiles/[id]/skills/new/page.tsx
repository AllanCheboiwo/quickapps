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
import { skillApi } from '@/lib/api'
import type { SkillCreate } from '@/types' 
import { ArrowLeft, Lightbulb, Loader2 } from 'lucide-react'

const skillSchema = z.object({
  name: z.string().min(1, 'Skill name is required'),
  proficiency: z.string().optional().nullable(), // e.g., Beginner, Intermediate, Advanced, Expert
});

type SkillFormValues = z.infer<typeof skillSchema>;

export default function AddSkillPage() {
  const { isAuthenticated, isLoading: authLoading } = useRequireAuth();
  const params = useParams();
  const router = useRouter();
  const queryClient = useQueryClient();
  const profileId = parseInt(params.id as string);

  const [apiError, setApiError] = useState<string | null>(null);

  const form = useForm<SkillFormValues>({
    resolver: zodResolver(skillSchema),
    defaultValues: {
      name: '',
      proficiency: '',
    },
  });

  const createSkillMutation = useMutation({
    mutationFn: (data: SkillCreate) => skillApi.createSkill(profileId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['skills', profileId] });
      queryClient.invalidateQueries({ queryKey: ['profile', profileId] });
      router.push(`/profiles/${profileId}/builder`);
    },
    onError: (error: any) => {
      setApiError(error.response?.data?.detail || 'Failed to add skill. Please try again.');
    },
  });

  const onSubmit = (data: SkillFormValues) => {
    setApiError(null);
    const payload: SkillCreate = {
      name: data.name,
      proficiency: data.proficiency || undefined,
    };
    createSkillMutation.mutate(payload);
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
              <Lightbulb className="h-6 w-6 mr-2 text-primary-600" />
              <CardTitle className="text-2xl">Add New Skill</CardTitle>
            </div>
            <CardDescription>
              Showcase your technical and soft skills.
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
                <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">Skill Name *</label>
                <Input 
                  id="name" 
                  {...form.register('name')} 
                  placeholder="e.g., Python, JavaScript, Project Management"
                />
                {form.formState.errors.name && (
                  <p className="text-sm text-red-600 mt-1">{form.formState.errors.name.message}</p>
                )}
              </div>

              <div>
                <label htmlFor="proficiency" className="block text-sm font-medium text-gray-700 mb-1">Proficiency Level</label>
                <Input 
                  id="proficiency" 
                  {...form.register('proficiency')} 
                  placeholder="e.g., Beginner, Intermediate, Advanced, Expert (Optional)"
                />
                {form.formState.errors.proficiency && (
                  <p className="text-sm text-red-600 mt-1">{form.formState.errors.proficiency.message}</p>
                )}
              </div>

              <div className="flex justify-end space-x-3 pt-4">
                <Button 
                  type="button" 
                  variant="outline"
                  onClick={() => router.push(`/profiles/${profileId}/builder`)}
                  disabled={createSkillMutation.isPending}
                >
                  Cancel
                </Button>
                <Button type="submit" disabled={createSkillMutation.isPending} className="min-w-[100px]">
                  {createSkillMutation.isPending ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    'Save Skill'
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