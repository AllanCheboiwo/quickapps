import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Bot, Zap, FileText, ArrowRight, CheckCircle } from 'lucide-react'

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-primary-900">QuickApps</h1>
            </div>
            <nav className="hidden md:flex space-x-8">
              <a href="#features" className="text-gray-600 hover:text-primary-600 transition-colors">
                Features
              </a>
              <a href="#how-it-works" className="text-gray-600 hover:text-primary-600 transition-colors">
                How it Works
              </a>
            </nav>
            <div className="flex items-center space-x-4">
              <Link href="/auth">
                <Button variant="outline">Sign In</Button>
              </Link>
              <Link href="/auth">
                <Button>Get Started</Button>
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20 lg:py-32">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-4xl mx-auto">
            <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
              AI-Powered Resumes That{' '}
              <span className="text-primary-600">Get You Hired</span>
            </h1>
            <p className="text-xl md:text-2xl text-gray-600 mb-8 leading-relaxed">
              Create tailored, professional resumes in minutes using AI that understands what employers want
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
              <Link href="/auth">
                <Button size="lg" className="text-lg px-8 py-6">
                  Build My Resume
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </Link>
              <Button variant="outline" size="lg" className="text-lg px-8 py-6">
                Watch Demo
              </Button>
            </div>
            <p className="text-gray-500 text-sm">
              Join 10,000+ professionals who landed their dream jobs
            </p>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-gray-50">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Why Choose QuickApps?
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Our AI-powered platform makes creating professional resumes effortless and effective
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            <Card className="text-center border-0 shadow-lg hover:shadow-xl transition-shadow">
              <CardHeader>
                <div className="mx-auto w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mb-4">
                  <Bot className="h-8 w-8 text-primary-600" />
                </div>
                <CardTitle className="text-2xl">AI-Powered Tailoring</CardTitle>
                <CardDescription className="text-gray-600">
                  Adapts your experience to any job description automatically
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-gray-500">
                  Our AI analyzes job requirements and highlights your most relevant skills and experiences
                </p>
              </CardContent>
            </Card>

            <Card className="text-center border-0 shadow-lg hover:shadow-xl transition-shadow">
              <CardHeader>
                <div className="mx-auto w-16 h-16 bg-secondary-100 rounded-full flex items-center justify-center mb-4">
                  <Zap className="h-8 w-8 text-secondary-400" />
                </div>
                <CardTitle className="text-2xl">Multiple Profiles</CardTitle>
                <CardDescription className="text-gray-600">
                  Create different resumes for different career paths
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-gray-500">
                  Organize your experience into targeted profiles for software engineering, data science, and more
                </p>
              </CardContent>
            </Card>

            <Card className="text-center border-0 shadow-lg hover:shadow-xl transition-shadow">
              <CardHeader>
                <div className="mx-auto w-16 h-16 bg-success-100 rounded-full flex items-center justify-center mb-4">
                  <FileText className="h-8 w-8 text-success-500" />
                </div>
                <CardTitle className="text-2xl">Professional LaTeX</CardTitle>
                <CardDescription className="text-gray-600">
                  Export beautiful, ATS-friendly PDFs
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-gray-500">
                  Generate clean, professional documents that pass through applicant tracking systems
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="py-20">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              How It Works
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Three simple steps to your perfect resume
            </p>
          </div>

          <div className="max-w-5xl mx-auto">
            <div className="grid md:grid-cols-3 gap-8">
              {/* Step 1 */}
              <div className="text-center">
                <div className="mx-auto w-16 h-16 bg-primary-600 text-white rounded-full flex items-center justify-center mb-6 text-2xl font-bold">
                  1
                </div>
                <h3 className="text-xl font-semibold mb-4">Build Your Profile</h3>
                <p className="text-gray-600">
                  Add your experience, education, skills, and projects once
                </p>
              </div>

              {/* Step 2 */}
              <div className="text-center">
                <div className="mx-auto w-16 h-16 bg-primary-600 text-white rounded-full flex items-center justify-center mb-6 text-2xl font-bold">
                  2
                </div>
                <h3 className="text-xl font-semibold mb-4">Paste Job Description</h3>
                <p className="text-gray-600">
                  AI analyzes requirements and tailors your resume automatically
                </p>
              </div>

              {/* Step 3 */}
              <div className="text-center">
                <div className="mx-auto w-16 h-16 bg-primary-600 text-white rounded-full flex items-center justify-center mb-6 text-2xl font-bold">
                  3
                </div>
                <h3 className="text-xl font-semibold mb-4">Download & Apply</h3>
                <p className="text-gray-600">
                  Get your polished, professional resume ready for applications
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-primary-900 text-white">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Ready to Land Your Dream Job?
          </h2>
          <p className="text-xl text-primary-100 mb-8 max-w-2xl mx-auto">
            Join thousands of professionals who have successfully used QuickApps to advance their careers
          </p>
          <Link href="/auth">
            <Button size="lg" className="bg-white text-primary-900 hover:bg-gray-100 text-lg px-8 py-6">
              Start Building Now
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 bg-gray-900 text-white">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h3 className="text-2xl font-bold mb-4">QuickApps</h3>
            <p className="text-gray-400 mb-6">
              AI-powered resume builder for the modern job seeker
            </p>
            <div className="text-gray-400">
              <a href="mailto:kiplongeiallan@gmail.com" className="hover:text-white transition-colors">
                kiplongeiallan@gmail.com
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
} 