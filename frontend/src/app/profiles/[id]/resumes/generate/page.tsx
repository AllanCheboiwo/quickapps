'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useRequireAuth } from '@/hooks/use-auth'
import { resumeApi, profileApi } from '@/lib/api' // Assuming resumeApi is set up
import type { ResumeGenerateRequest, GeneratedResume } from '@/types' 
import { ArrowLeft, Loader2, Rocket, Download, FileText, AlertTriangle } from 'lucide-react'

const generateResumeSchema = z.object({
  job_description: z.string().min(50, 'Job description should be at least 50 characters'),
});

type GenerateResumeFormValues = z.infer<typeof generateResumeSchema>;

export default function GenerateResumePage() {
  const { isAuthenticated, isLoading: authLoading } = useRequireAuth();
  const params = useParams();
  const router = useRouter();
  const queryClient = useQueryClient();
  const profileId = parseInt(params.id as string);

  const [apiError, setApiError] = useState<string | null>(null);
  const [generatedResumeData, setGeneratedResumeData] = useState<GeneratedResume | null>(null);

  const { data: profile, isLoading: profileIsLoading } = useQuery({
    queryKey: ['profile', profileId],
    queryFn: () => profileApi.getProfile(profileId),
    enabled: isAuthenticated && !isNaN(profileId),
  });

  const form = useForm<GenerateResumeFormValues>({
    resolver: zodResolver(generateResumeSchema),
    defaultValues: {
      job_description: '',
    },
  });

  const generateResumeMutation = useMutation({
    mutationFn: (data: ResumeGenerateRequest) => 
      resumeApi.generateResume(data),
    onSuccess: (newResume: GeneratedResume) => {
      setGeneratedResumeData(newResume);
      queryClient.invalidateQueries({ queryKey: ['resumes', profileId] }); 
      setApiError(null);
      form.reset(); 
    },
    onError: (error: any) => {
      setGeneratedResumeData(null);
      const detail = error.response?.data?.detail;
      if (typeof detail === 'string' && detail.includes("Profile has no content")) {
        setApiError("Cannot generate resume: The profile is empty. Please add experience, education, skills, or projects.");
      } else if (typeof detail === 'string' && detail.includes("LaTeX template is not loaded properly")){
        setApiError("Cannot generate resume: Critical server error with LaTeX template. Please contact support.");
      } else {
        setApiError(detail || 'Failed to generate resume. Please try again.');
      }
    },
  });

  const onSubmit = (data: GenerateResumeFormValues) => {
    setApiError(null);
    setGeneratedResumeData(null);
    generateResumeMutation.mutate({ profile_id: profileId, job_description: data.job_description });
  };

  if (authLoading || profileIsLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
      </div>
    );
  }

  if (!isAuthenticated || isNaN(profileId) || !profile) {
    // Redirect or show error if not authenticated, profileId is invalid, or profile not found
    router.push(isNaN(profileId) || !profile ? '/dashboard' : '/auth'); 
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-16">
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
              <h1 className="text-xl font-semibold text-gray-800 truncate">Generate Resume for {profile.name}</h1>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Card>
          <CardHeader>
            <div className="flex items-center">
              <Rocket className="h-6 w-6 mr-2 text-primary-600" />
              <CardTitle className="text-2xl">AI Resume Generation</CardTitle>
            </div>
            <CardDescription>
              Paste the job description below. Our AI will tailor your profile information to create a targeted resume.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {apiError && (
              <div className="mb-4 p-3 bg-red-50 border border-red-300 text-red-700 rounded-md whitespace-pre-wrap flex items-start">
                <AlertTriangle className="h-5 w-5 mr-2 flex-shrink-0" />
                <p className="flex-grow">{apiError}</p>
              </div>
            )}
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              <div>
                <label htmlFor="job_description" className="block text-sm font-medium text-gray-700 mb-1">Job Description *</label>
                <textarea 
                  id="job_description" 
                  {...form.register('job_description')} 
                  placeholder="Paste the full job description here..."
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm p-2.5 border h-auto min-h-[200px]"
                  rows={10}
                  disabled={generateResumeMutation.isPending}
                />
                {form.formState.errors.job_description && (
                  <p className="text-sm text-red-600 mt-1">{form.formState.errors.job_description.message}</p>
                )}
              </div>

              <div className="flex justify-end">
                <Button type="submit" disabled={generateResumeMutation.isPending || !form.formState.isValid} className="min-w-[200px]">
                  {generateResumeMutation.isPending ? (
                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  ) : (
                    <Rocket className="h-4 w-4 mr-2" />
                  )}
                  Generate Resume
                </Button>
              </div>
            </form>

            {generateResumeMutation.isSuccess && generatedResumeData && (
              <div className="mt-8 pt-6 border-t">
                <h3 className="text-xl font-semibold text-gray-800 mb-3 flex items-center">
                  <FileText className="h-5 w-5 mr-2 text-green-600" />
                  Resume Generated Successfully!
                </h3>
                
                {generatedResumeData.pdf_file_path ? (
                  <>
                    <p className="text-sm text-gray-600 mb-4">
                      Your tailored resume has been created. You can now download it as a PDF.
                    </p>
                    <a 
                      href={`/api/resumes/${generatedResumeData.id}/pdf`} // Using /api prefix for Next.js proxy
                      target="_blank"
                      rel="noopener noreferrer"
                      download // Suggests download, browser might still open in new tab depending on settings
                    >
                      <Button variant="default" className="w-full md:w-auto">
                        <Download className="h-4 w-4 mr-2" />
                        Download PDF Resume
                      </Button>
                    </a>
                  </>
                ) : (
                  <div className="p-3 bg-yellow-50 border border-yellow-300 text-yellow-700 rounded-md flex items-start">
                    <AlertTriangle className="h-5 w-5 mr-2 flex-shrink-0 text-yellow-500" />
                    <p className="flex-grow">
                      PDF generation for this resume failed or is still processing. 
                      The LaTeX content has been saved and can be compiled manually.
                    </p>
                  </div>
                )}
                <div className="mt-6">
                    <h4 className="text-md font-semibold text-gray-700 mb-2">Raw LaTeX Content:</h4>
                    <p className="text-xs text-gray-500 mb-1">This is the raw LaTeX code generated. Useful for debugging or manual compilation if needed.</p>
                    <pre className="bg-gray-100 p-3 rounded-md text-xs overflow-x-auto max-h-60 border border-gray-200">
                        {generatedResumeData.latex_content || "No LaTeX content available."}
                    </pre>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </main>
    </div>
  );
} 