'use client'

import { useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import { useQuery } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useRequireAuth } from '@/hooks/use-auth'
import { profileApi, experienceApi, educationApi, projectApi, skillApi } from '@/lib/api'
import { 
  ArrowLeft, 
  Briefcase, 
  GraduationCap, 
  Code, 
  Lightbulb,
  Plus,
  CheckCircle2,
  Circle,
  Rocket
} from 'lucide-react'
import type { LucideIcon } from 'lucide-react'

interface SectionItem {
  name: string;
  count: number;
  total: number; // Minimum required items for section to be "complete"
  path: string;
  icon: LucideIcon;
  description: string;
  latestEntry?: string;
}

export default function ProfileBuilderPage() {
  const { isAuthenticated, isLoading: authLoading } = useRequireAuth()
  const params = useParams()
  const router = useRouter()
  const profileId = parseInt(params.id as string)

  // Fetch profile data
  const { data: profile, isLoading: profileLoading, error: profileError } = useQuery({
    queryKey: ['profile', profileId],
    queryFn: () => profileApi.getProfile(profileId),
    enabled: isAuthenticated && !isNaN(profileId),
  })

  // Fetch related data
  const { data: experiences = [] } = useQuery({
    queryKey: ['experiences', profileId],
    queryFn: () => experienceApi.getExperiences(profileId),
    enabled: isAuthenticated && !isNaN(profileId),
  })

  const { data: educationItems = [] } = useQuery({ // Renamed to avoid conflict
    queryKey: ['education', profileId],
    queryFn: () => educationApi.getEducations(profileId),
    enabled: isAuthenticated && !isNaN(profileId),
  })

  const { data: projects = [] } = useQuery({
    queryKey: ['projects', profileId],
    queryFn: () => projectApi.getProjects(profileId),
    enabled: isAuthenticated && !isNaN(profileId),
  })

  const { data: skills = [] } = useQuery({
    queryKey: ['skills', profileId],
    queryFn: () => skillApi.getSkills(profileId),
    enabled: isAuthenticated && !isNaN(profileId),
  })

  if (authLoading || profileLoading) {
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
    return null // or redirect to login
  }

  if (profileError || !profile) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900">Profile not found</h2>
          <p className="mt-2 text-gray-600">The profile you're looking for doesn't exist or you don't have permission to view it.</p>
          <Link href="/dashboard">
            <Button className="mt-4">Back to Dashboard</Button>
          </Link>
        </div>
      </div>
    )
  }

  const sectionsData: SectionItem[] = [
    { 
      name: 'Experience', 
      count: experiences.length, 
      total: 1, 
      path: 'experience/new', 
      icon: Briefcase,
      description: 'Add your work experience, internships, and relevant positions.',
      latestEntry: experiences.length > 0 ? `${experiences[0]?.position} at ${experiences[0]?.company}` : undefined
    },
    { 
      name: 'Education', 
      count: educationItems.length, 
      total: 1, 
      path: 'education/new', 
      icon: GraduationCap,
      description: 'List your degrees, certifications, and educational background.',
      latestEntry: educationItems.length > 0 ? `${educationItems[0]?.degree} at ${educationItems[0]?.institution}` : undefined
    },
    { 
      name: 'Skills', 
      count: skills.length, 
      total: 1, 
      path: 'skills/new', 
      icon: Lightbulb,
      description: 'Highlight your key skills and proficiencies.',
      latestEntry: skills.length > 0 ? skills.slice(0, 3).map(s => s.name).join(', ') : undefined
    },
    { 
      name: 'Projects', 
      count: projects.length, 
      total: 1, 
      path: 'projects/new', 
      icon: Code,
      description: 'Showcase your personal or professional projects.',
      latestEntry: projects.length > 0 ? projects[0]?.title : undefined
    },
  ];

  const completedSections = sectionsData.filter(s => s.count >= s.total).length;
  const totalSections = sectionsData.length;
  const completionPercentage = totalSections > 0 ? Math.round((completedSections / totalSections) * 100) : 0;

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
                Dashboard
              </Link>
              <div>
                <h1 className="text-2xl font-bold text-primary-900">{profile.name}</h1>
                <p className="text-sm text-gray-600">Profile Builder</p>
              </div>
            </div>
            <Button 
              onClick={() => router.push(`/profiles/${profileId}/resumes/generate`)}
              className="bg-primary-600 hover:bg-primary-700"
              disabled={completionPercentage < 1} // Enable if at least one section has an item
              title={completionPercentage < 1 ? "Add at least one item to any section to generate a resume" : "Generate AI Resume"}
            >
              <Rocket className="h-4 w-4 mr-2" />
              Generate Resume
            </Button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Completion Status */}
        <Card className="mb-8">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-xl">Profile Progress</CardTitle>
                <CardDescription>
                  {completedSections} of {totalSections} sections started (at least 1 item added)
                </CardDescription>
              </div>
              <div className="text-right">
                <div className="text-3xl font-bold text-primary-600">{completionPercentage}%</div>
                {/* <div className="text-sm text-gray-500">Complete</div> */}
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div 
                className="bg-primary-600 h-2.5 rounded-full transition-all duration-300"
                style={{ width: `${completionPercentage}%` }}
              ></div>
            </div>
            {completionPercentage < 100 && totalSections > 0 && (
                 <p className="text-sm text-gray-500 mt-2">
                    Add at least one item to each section to maximize your profile strength.
                 </p>
            )}
            {completionPercentage === 100 && (
                 <p className="text-sm text-green-600 mt-2">
                    Great! All sections have items. Your profile is looking strong.
                 </p>
            )}
          </CardContent>
        </Card>

        {/* Profile Sections Grid */}
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Build Your Profile Sections</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {sectionsData.map((section) => (
            <Card key={section.name} className="hover:shadow-lg transition-shadow flex flex-col">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <section.icon className="h-5 w-5 text-primary-600 mr-2" />
                    <CardTitle className="text-lg">{section.name}</CardTitle>
                  </div>
                  {section.count >= section.total ? (
                    <CheckCircle2 className="h-5 w-5 text-green-500" />
                  ) : (
                    <Circle className="h-5 w-5 text-gray-300" />
                  )}
                </div>
              </CardHeader>
              <CardContent className="flex-grow flex flex-col">
                <div className="space-y-1 flex-grow">
                  <div className="flex items-center text-sm">
                    <span className="font-medium">{section.count} {section.count === 1 ? section.name.slice(0, -1) : section.name.toLowerCase()} item(s) added</span>
                  </div>
                  {section.latestEntry && section.count > 0 && (
                    <p className="text-xs text-gray-500 truncate py-1">
                      Latest: {section.latestEntry}
                    </p>
                  )}
                  <p className="text-sm text-gray-600 mt-2 pb-2">
                    {section.description}
                  </p>
                </div>
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="w-full mt-4"
                  onClick={() => router.push(`/profiles/${profileId}/${section.path}`)}
                >
                  <Plus className="h-4 w-4 mr-2" />
                  {section.count === 0 ? `Add ${section.name}` : `Add More ${section.name}`}
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  )
} 