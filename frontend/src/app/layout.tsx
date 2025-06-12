import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { QueryProvider } from '@/lib/providers/query-provider'
import { Toaster } from '@/components/ui/toaster'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'QuickApps - AI-Powered Resume Builder',
  description: 'Create tailored, professional resumes in minutes using AI that understands what employers want',
  keywords: 'resume, AI, job application, career, professional',
  authors: [{ name: 'QuickApps' }],
  openGraph: {
    title: 'QuickApps - AI-Powered Resume Builder',
    description: 'Create tailored, professional resumes in minutes using AI',
    type: 'website',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <QueryProvider>
          {children}
          <Toaster />
        </QueryProvider>
      </body>
    </html>
  )
} 