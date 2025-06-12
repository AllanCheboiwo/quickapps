'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useRequireAuth } from '@/hooks/use-auth'
import { profileApi } from '@/lib/api'
import { ArrowLeft, Loader2, User, Briefcase, GraduationCap, Code } from 'lucide-react'

const profileSchema = z.object({
  name: z.string().min(1, 'Profile name is required').min(3, 'Profile name must be at least 3 characters'),
})

type ProfileForm = z.infer<typeof profileSchema>

export default function NewProfilePage() {
  const { isAuthenticated, isLoading: authLoading } = useRequireAuth()
  const [error, setError] = useState('')
  const router = useRouter()
  const queryClient = useQueryClient()

  const form = useForm<ProfileForm>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      name: '',
    },
  })

  const createProfileMutation = useMutation({
    mutationFn: (data: ProfileForm) => profileApi.createProfile(data),
    onSuccess: (profile) => {
      queryClient.invalidateQueries({ queryKey: ['profiles'] })
      router.push(`/profiles/${profile.id}/builder`)
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Failed to create profile')
    },
  })

  const onSubmit = (data: ProfileForm) => {
    setError('')
    createProfileMutation.mutate(data)
  }

  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <Link 
                href="/dashboard" 
                className="inline-flex items-center text-gray-600 hover:text-gray-900 mr-4 transition-colors"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Dashboard
              </Link>
              <h1 className="text-2xl font-bold text-primary-900">Create New Profile</h1>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Form Section */}
          <div>
            <Card>
              <CardHeader>
                <CardTitle className="text-2xl flex items-center">
                  <User className="h-6 w-6 mr-2 text-primary-600" />
                  Create Your Profile
                </CardTitle>
                <CardDescription>
                  Give your profile a name and we'll help you build it step by step
                </CardDescription>
              </CardHeader>

              <CardContent>
                {error && (
                  <div className="mb-6 p-3 bg-red-50 border border-red-200 rounded-md">
                    <p className="text-red-600 text-sm">{error}</p>
                  </div>
                )}

                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                  <div>
                    <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                      What would you like to call this profile? *
                    </label>
                    <Input
                      id="name"
                      placeholder="e.g. Software Engineer Profile, Data Scientist Profile, Product Manager Profile"
                      {...form.register('name')}
                      className={form.formState.errors.name ? 'border-red-300' : ''}
                    />
                    {form.formState.errors.name && (
                      <p className="mt-1 text-sm text-red-600">
                        {form.formState.errors.name.message}
                      </p>
                    )}
                    <p className="mt-2 text-sm text-gray-500">
                      Choose a name that reflects the type of roles you're targeting with this profile
                    </p>
                  </div>

                  <Button
                    type="submit"
                    disabled={createProfileMutation.isPending}
                    className="w-full"
                  >
                    {createProfileMutation.isPending ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Creating Profile...
                      </>
                    ) : (
                      'Create Profile'
                    )}
                  </Button>
                </form>
              </CardContent>
            </Card>
          </div>

          {/* Preview/Info Section */}
          <div>
            <Card>
              <CardHeader>
                <CardTitle className="text-xl">What happens next?</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0 w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                      <span className="text-sm font-semibold text-primary-600">1</span>
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900">Profile Created</h4>
                      <p className="text-sm text-gray-600">Your profile will be created with the name you choose</p>
                    </div>
                  </div>

                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0 w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                      <span className="text-sm font-semibold text-primary-600">2</span>
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900">Build Your Profile</h4>
                      <p className="text-sm text-gray-600">Add your information section by section at your own pace</p>
                    </div>
                  </div>

                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0 w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                      <span className="text-sm font-semibold text-primary-600">3</span>
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900">Generate Resumes</h4>
                      <p className="text-sm text-gray-600">Create AI-tailored resumes for specific job applications</p>
                    </div>
                  </div>
                </div>

                <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                  <h4 className="font-medium text-blue-900 mb-2">Sections you can add:</h4>
                  <div className="grid grid-cols-2 gap-2 text-sm text-blue-700">
                    <div className="flex items-center">
                      <User className="h-4 w-4 mr-2" />
                      Personal Info
                    </div>
                    <div className="flex items-center">
                      <Briefcase className="h-4 w-4 mr-2" />
                      Experience
                    </div>
                    <div className="flex items-center">
                      <GraduationCap className="h-4 w-4 mr-2" />
                      Education
                    </div>
                    <div className="flex items-center">
                      <Code className="h-4 w-4 mr-2" />
                      Skills & Projects
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
} 