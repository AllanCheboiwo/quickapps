'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { useQuery } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useRequireAuth } from '@/hooks/use-auth'
import { useAuthStore } from '@/stores/auth'
import { profileApi, resumeApi } from '@/lib/api'
import { 
  Plus, 
  FileText, 
  User, 
  Briefcase, 
  GraduationCap, 
  Code,
  Settings,
  LogOut,
  Calendar,
  Download
} from 'lucide-react'
import { formatDate } from '@/lib/utils'

export default function DashboardPage() {
  const { isAuthenticated, isLoading: authLoading } = useRequireAuth()
  const { user, logout } = useAuthStore()

  const { data: profiles = [], isLoading: profilesLoading } = useQuery({
    queryKey: ['profiles'],
    queryFn: profileApi.getProfiles,
    enabled: isAuthenticated,
  })

  const { data: resumes = [], isLoading: resumesLoading } = useQuery({
    queryKey: ['resumes'],
    queryFn: resumeApi.getResumes,
    enabled: isAuthenticated,
  })

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
              <h1 className="text-2xl font-bold text-primary-900">QuickApps</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-gray-700">Welcome, {user?.email}</span>
              <Button variant="outline" size="sm" onClick={() => {}}>
                <Settings className="h-4 w-4 mr-2" />
                Settings
              </Button>
              <Button variant="outline" size="sm" onClick={logout}>
                <LogOut className="h-4 w-4 mr-2" />
                Sign Out
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            Welcome back!
          </h2>
          <p className="text-gray-600">
            Ready to create your next amazing resume?
          </p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Profiles</CardTitle>
              <User className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{profiles.length}</div>
              <p className="text-xs text-muted-foreground">
                Professional profiles created
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Generated Resumes</CardTitle>
              <FileText className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{resumes.length}</div>
              <p className="text-xs text-muted-foreground">
                AI-tailored resumes generated
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">This Month</CardTitle>
              <Calendar className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {resumes.filter(r => 
                  new Date(r.created_at).getMonth() === new Date().getMonth()
                ).length}
              </div>
              <p className="text-xs text-muted-foreground">
                Resumes generated this month
              </p>
            </CardContent>
          </Card>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Profiles Section */}
          <div>
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold text-gray-900">Your Profiles</h3>
              <Link href="/profiles/new">
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  New Profile
                </Button>
              </Link>
            </div>

            <div className="space-y-4">
              {profilesLoading ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600 mx-auto"></div>
                  <p className="mt-2 text-gray-600 text-sm">Loading profiles...</p>
                </div>
              ) : profiles.length === 0 ? (
                <Card className="text-center py-8">
                  <CardContent>
                    <User className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <h4 className="text-lg font-medium text-gray-900 mb-2">No profiles yet</h4>
                    <p className="text-gray-600 mb-4">
                      Create your first profile to get started with AI-powered resumes
                    </p>
                    <Link href="/profiles/new">
                      <Button>
                        <Plus className="h-4 w-4 mr-2" />
                        Create Profile
                      </Button>
                    </Link>
                  </CardContent>
                </Card>
              ) : (
                profiles.map((profile) => (
                  <Card key={profile.id} className="hover:shadow-md transition-shadow">
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <div>
                          <CardTitle className="text-lg">{profile.name}</CardTitle>
                          <CardDescription>
                            Profile created {formatDate(profile.created_at)}
                          </CardDescription>
                        </div>
                        <div className="flex space-x-2">
                          <Link href={`/profiles/${profile.id}/builder`}>
                            <Button variant="outline" size="sm">
                              Edit
                            </Button>
                          </Link>
                          <Link href={`/profiles/${profile.id}/resumes/generate`}>
                            <Button size="sm">
                              Generate Resume
                            </Button>
                          </Link>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="flex items-center space-x-4 text-sm text-gray-600">
                        <span>
                          Updated {formatDate(profile.updated_at)}
                        </span>
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          </div>

          {/* Recent Resumes Section */}
          <div>
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold text-gray-900">Recent Resumes</h3>
              {profiles.length > 0 && (
                <Link href={`/profiles/${profiles[0]?.id}/resumes/generate`}>
                  <Button variant="outline">
                    <Plus className="h-4 w-4 mr-2" />
                    Generate New
                  </Button>
                </Link>
              )}
            </div>

            <div className="space-y-4">
              {resumesLoading ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600 mx-auto"></div>
                  <p className="mt-2 text-gray-600 text-sm">Loading resumes...</p>
                </div>
              ) : resumes.length === 0 ? (
                <Card className="text-center py-8">
                  <CardContent>
                    <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <h4 className="text-lg font-medium text-gray-900 mb-2">No resumes yet</h4>
                    <p className="text-gray-600 mb-4">
                      Generate your first AI-tailored resume
                    </p>
                    {profiles.length > 0 ? (
                      <Link href={`/profiles/${profiles[0].id}/resumes/generate`}>
                        <Button>
                          <Plus className="h-4 w-4 mr-2" />
                          Generate Resume
                        </Button>
                      </Link>
                    ) : (
                      <p className="text-sm text-gray-500">
                        Create a profile first to generate resumes
                      </p>
                    )}
                  </CardContent>
                </Card>
              ) : (
                resumes.slice(0, 5).map((resume) => (
                  <Card key={resume.id} className="hover:shadow-md transition-shadow">
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <div>
                          <CardTitle className="text-lg">
                            Resume #{resume.id}
                          </CardTitle>
                          <CardDescription>
                            {resume.job_description.length > 100 
                              ? `${resume.job_description.substring(0, 100)}...`
                              : resume.job_description
                            }
                          </CardDescription>
                        </div>
                        <div className="flex space-x-2">
                          <Link href={`/resumes/${resume.id}`}>
                            <Button variant="outline" size="sm">
                              <FileText className="h-4 w-4 mr-2" />
                              View
                            </Button>
                          </Link>
                          {resume.pdf_path && (
                            <Button size="sm">
                              <Download className="h-4 w-4 mr-2" />
                              Download
                            </Button>
                          )}
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-gray-600">
                        Generated {formatDate(resume.created_at)}
                      </p>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mt-12">
          <h3 className="text-xl font-semibold text-gray-900 mb-6">Quick Actions</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Link href="/profiles/new">
              <Card className="hover:shadow-md transition-shadow cursor-pointer">
                <CardContent className="flex flex-col items-center p-6">
                  <User className="h-8 w-8 text-primary-600 mb-2" />
                  <span className="text-sm font-medium text-center">Create Profile</span>
                </CardContent>
              </Card>
            </Link>

            {profiles.length > 0 && (
              <Link href={`/profiles/${profiles[0].id}/builder`}>
                <Card className="hover:shadow-md transition-shadow cursor-pointer">
                  <CardContent className="flex flex-col items-center p-6">
                    <Briefcase className="h-8 w-8 text-primary-600 mb-2" />
                    <span className="text-sm font-medium text-center">Add Experience</span>
                  </CardContent>
                </Card>
              </Link>
            )}

            {profiles.length > 0 && (
              <Link href={`/profiles/${profiles[0].id}/builder`}>
                <Card className="hover:shadow-md transition-shadow cursor-pointer">
                  <CardContent className="flex flex-col items-center p-6">
                    <GraduationCap className="h-8 w-8 text-primary-600 mb-2" />
                    <span className="text-sm font-medium text-center">Add Education</span>
                  </CardContent>
                </Card>
              </Link>
            )}

            {profiles.length > 0 && (
              <Link href={`/profiles/${profiles[0].id}/builder`}>
                <Card className="hover:shadow-md transition-shadow cursor-pointer">
                  <CardContent className="flex flex-col items-center p-6">
                    <Code className="h-8 w-8 text-primary-600 mb-2" />
                    <span className="text-sm font-medium text-center">Add Project</span>
                  </CardContent>
                </Card>
              </Link>
            )}
          </div>
        </div>
      </div>
    </div>
  )
} 