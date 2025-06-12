// User types
export interface User {
  id: number
  username: string
  email: string
  firstName?: string
  lastName?: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface UserCreate {
  username: string
  email: string
  password: string
  firstName?: string
  lastName?: string
}

export interface UserLogin {
  username: string
  password: string
}

// Profile types
export interface Profile {
  id: number
  user_id: number
  name: string
  created_at: string
  updated_at: string
}

export interface ProfileCreate {
  name: string
}

export interface ProfileUpdate extends Partial<ProfileCreate> {}

// Experience types
export interface Experience {
  id: number
  profile_id: number
  company: string
  position: string
  start_date: string
  end_date?: string
  description?: string
  created_at: string
  updated_at: string
}

export interface ExperienceCreate {
  company: string
  position: string
  start_date: string
  end_date?: string
  description?: string
}

export interface ExperienceUpdate extends Partial<ExperienceCreate> {}

// Education types
export interface Education {
  id: number
  profile_id: number
  institution: string
  degree: string
  field_of_study?: string
  start_date: string
  end_date?: string
  gpa?: number
  description?: string
  created_at: string
  updated_at: string
}

export interface EducationCreate {
  institution: string
  degree: string
  field_of_study?: string
  start_date: string
  end_date?: string
  gpa?: number
  description?: string
}

export interface EducationUpdate extends Partial<EducationCreate> {}

// Project types
export interface Project {
  id: number
  profile_id: number
  title: string
  description?: string
  technologies?: string
  start_date: string
  end_date?: string
  github_url?: string
  live_url?: string
  created_at: string
  updated_at: string
}

export interface ProjectCreate {
  title: string
  description?: string
  technologies?: string
  start_date?: string
  end_date?: string
  github_url?: string
  live_url?: string
}

export interface ProjectUpdate extends Partial<ProjectCreate> {}

// Skill types
export interface Skill {
  id: number
  profile_id: number
  name: string
  category?: string
  proficiency_level?: string
  created_at: string
  updated_at: string
}

export interface SkillCreate {
  name: string
  proficiency?: string
}

export interface SkillUpdate extends Partial<SkillCreate> {}

// Resume types
export interface GeneratedResume {
  id: number
  profile_id: number
  job_description: string
  latex_content: string
  pdf_file_path: string | null
  created_at: string
  updated_at: string
}

export interface ResumeGenerateRequest {
  profile_id: number
  job_description: string
}

export interface ResumeListResponse {
  id: number
  profile_id: number
  job_description: string
  pdf_file_path: string | null
  created_at: string
  updated_at: string
}

// API Response types
export interface ApiResponse<T> {
  data: T
  message?: string
}

export interface ApiError {
  detail: string
}

export interface AuthTokens {
  access_token: string
  token_type: string
}

// Form types
export interface LoginFormData {
  email: string
  password: string
}

export interface RegisterFormData {
  email: string
  password: string
  confirmPassword: string
} 