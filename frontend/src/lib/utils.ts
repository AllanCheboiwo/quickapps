import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(date: string | Date) {
  return new Intl.DateTimeFormat('en-US', {
    month: 'long',
    year: 'numeric',
  }).format(new Date(date))
}

export function formatDateRange(startDate: string | Date, endDate?: string | Date | null) {
  const start = formatDate(startDate)
  if (!endDate) return `${start} - Present`
  return `${start} - ${formatDate(endDate)}`
}

export function truncateText(text: string, maxLength: number) {
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength) + '...'
}

export function sleep(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms))
} 