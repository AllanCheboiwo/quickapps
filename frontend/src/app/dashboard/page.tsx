'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { useQuery } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useRequireAuth } from '@/hooks/use-auth'
import { useAuthStore } from '@/stores/auth'
import { profileApi } from '@/lib/api'
import { GuestBanner } from '@/components/GuestBanner'
import { UpgradeCTA } from '@/components/UpgradeCTA'
import { 
  Plus, 
  FileText, 
  User,
  Briefcase, 
  Settings,
  LogOut
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
              <span className="text-gray-700">Welcome, {user?.username}</span>
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
        {/* Guest Banner */}
        <GuestBanner isGuest={user?.is_guest || false} daysRemaining={7} />

        {/* Welcome Section */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            Welcome back!
          </h2>
          <p className="text-gray-600">
            Ready to create your next amazing resume?
          </p>
        </div>


        {/* Profiles Section */}
        <div className="mb-12">
          <h3 className="text-xl font-semibold text-gray-900 mb-6">Your Profiles</h3>

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
                      Create Your First Profile
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
                          Created {formatDate(profile.created_at)} • Updated {formatDate(profile.updated_at)}
                        </CardDescription>
                      </div>
                      <div className="flex space-x-2">
                        <Link href={`/profiles/${profile.id}/builder`}>
                          <Button variant="outline" size="sm">
                            <Briefcase className="h-4 w-4 mr-2" />
                            Edit
                          </Button>
                        </Link>
                        <Link href={`/profiles/${profile.id}/resumes/generate`}>
                          <Button size="sm">
                            <FileText className="h-4 w-4 mr-2" />
                            Generate Resume
                          </Button>
                        </Link>
                      </div>
                    </div>
                  </CardHeader>
                </Card>
              ))
            )}
          </div>
        </div>

        {/* Quick Actions - Only if has profiles */}
        {profiles.length > 0 && (
          <div className="mt-12">
            <h3 className="text-xl font-semibold text-gray-900 mb-6">Quick Links</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Link href="/profiles/new">
                <Card className="hover:shadow-md transition-shadow cursor-pointer">
                  <CardContent className="flex flex-col items-center p-6">
                    <Plus className="h-8 w-8 text-primary-600 mb-2" />
                    <span className="text-sm font-medium text-center">Create New Profile</span>
                  </CardContent>
                </Card>
              </Link>

              <Link href={`/profiles/${profiles[0].id}/builder`}>
                <Card className="hover:shadow-md transition-shadow cursor-pointer">
                  <CardContent className="flex flex-col items-center p-6">
                    <Briefcase className="h-8 w-8 text-primary-600 mb-2" />
                    <span className="text-sm font-medium text-center">Edit Profile</span>
                  </CardContent>
                </Card>
              </Link>

              <Link href={`/profiles/${profiles[0].id}/resumes/generate`}>
                <Card className="hover:shadow-md transition-shadow cursor-pointer">
                  <CardContent className="flex flex-col items-center p-6">
                    <FileText className="h-8 w-8 text-primary-600 mb-2" />
                    <span className="text-sm font-medium text-center">Generate Resume</span>
                  </CardContent>
                </Card>
              </Link>
            </div>
          </div>
        )}

        {/* Upgrade CTA for guests */}
        {user?.is_guest && (
          <div className="mt-12">
            <UpgradeCTA />
          </div>
        )}
      </div>
    </div>
  )
} 