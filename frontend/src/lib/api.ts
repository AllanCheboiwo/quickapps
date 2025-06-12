import axios, { AxiosError } from 'axios'
import Cookies from 'js-cookie'
import type {
  User,
  UserLogin,
  UserCreate,
  Profile,
  ProfileCreate,
  ProfileUpdate,
  Experience,
  ExperienceCreate,
  ExperienceUpdate,
  Education,
  EducationCreate,
  EducationUpdate,
  Project,
  ProjectCreate,
  ProjectUpdate,
  Skill,
  SkillCreate,
  SkillUpdate,
  GeneratedResume,
  ResumeGenerateRequest,
  AuthTokens,
  ApiError,
} from '@/types'

// Create axios instance
const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  const token = Cookies.get('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiError>) => {
    if (error.response?.status === 401) {
      // Clear auth tokens and redirect to login
      Cookies.remove('access_token')
      window.location.href = '/auth'
    }
    return Promise.reject(error)
  }
)

// Auth API
export const authApi = {
  async login(credentials: UserLogin): Promise<AuthTokens> {
    const formData = new FormData()
    formData.append('username', credentials.username)
    formData.append('password', credentials.password)

    const response = await api.post<AuthTokens>('/auth/token', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })
    
    // Store token in cookie
    Cookies.set('access_token', response.data.access_token, { expires: 7 })
    
    return response.data
  },

  async register(userData: UserCreate): Promise<User> {
    const response = await api.post<User>('/auth/register', userData)
    return response.data
  },

  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>('/auth/me')
    return response.data
  },

  logout() {
    Cookies.remove('access_token')
    window.location.href = '/'
  },
}

// Profile API
export const profileApi = {
  async getProfiles(): Promise<Profile[]> {
    const response = await api.get<Profile[]>('/profiles')
    return response.data
  },

  async getProfile(id: number): Promise<Profile> {
    const response = await api.get<Profile>(`/profiles/${id}`)
    return response.data
  },

  async createProfile(data: ProfileCreate): Promise<Profile> {
    const response = await api.post<Profile>('/profiles', data)
    return response.data
  },

  async updateProfile(id: number, data: ProfileUpdate): Promise<Profile> {
    const response = await api.put<Profile>(`/profiles/${id}`, data)
    return response.data
  },

  async deleteProfile(id: number): Promise<void> {
    await api.delete(`/profiles/${id}`)
  },
}

// Experience API
export const experienceApi = {
  async getExperiences(profileId: number): Promise<Experience[]> {
    const response = await api.get<Experience[]>(`/profiles/${profileId}/experience`)
    return response.data
  },

  async getExperience(profileId: number, id: number): Promise<Experience> {
    const response = await api.get<Experience>(`/profiles/${profileId}/experience/${id}`)
    return response.data
  },

  async createExperience(profileId: number, data: ExperienceCreate): Promise<Experience> {
    const response = await api.post<Experience>(`/profiles/${profileId}/experience`, data)
    return response.data
  },

  async updateExperience(profileId: number, id: number, data: ExperienceUpdate): Promise<Experience> {
    const response = await api.put<Experience>(`/profiles/${profileId}/experience/${id}`, data)
    return response.data
  },

  async deleteExperience(profileId: number, id: number): Promise<void> {
    await api.delete(`/profiles/${profileId}/experience/${id}`)
  },
}

// Education API
export const educationApi = {
  async getEducations(profileId: number): Promise<Education[]> {
    const response = await api.get<Education[]>(`/profiles/${profileId}/education`)
    return response.data
  },

  async getEducation(profileId: number, id: number): Promise<Education> {
    const response = await api.get<Education>(`/profiles/${profileId}/education/${id}`)
    return response.data
  },

  async createEducation(profileId: number, data: EducationCreate): Promise<Education> {
    const response = await api.post<Education>(`/profiles/${profileId}/education`, data)
    return response.data
  },

  async updateEducation(profileId: number, id: number, data: EducationUpdate): Promise<Education> {
    const response = await api.put<Education>(`/profiles/${profileId}/education/${id}`, data)
    return response.data
  },

  async deleteEducation(profileId: number, id: number): Promise<void> {
    await api.delete(`/profiles/${profileId}/education/${id}`)
  },
}

// Project API
export const projectApi = {
  async getProjects(profileId: number): Promise<Project[]> {
    const response = await api.get<Project[]>(`/profiles/${profileId}/projects`)
    return response.data
  },

  async getProject(profileId: number, id: number): Promise<Project> {
    const response = await api.get<Project>(`/profiles/${profileId}/projects/${id}`)
    return response.data
  },

  async createProject(profileId: number, data: ProjectCreate): Promise<Project> {
    const response = await api.post<Project>(`/profiles/${profileId}/projects`, data)
    return response.data
  },

  async updateProject(profileId: number, id: number, data: ProjectUpdate): Promise<Project> {
    const response = await api.put<Project>(`/profiles/${profileId}/projects/${id}`, data)
    return response.data
  },

  async deleteProject(profileId: number, id: number): Promise<void> {
    await api.delete(`/profiles/${profileId}/projects/${id}`)
  },
}

// Skill API
export const skillApi = {
  async getSkills(profileId: number): Promise<Skill[]> {
    const response = await api.get<Skill[]>(`/profiles/${profileId}/skills`)
    return response.data
  },

  async getSkill(profileId: number, id: number): Promise<Skill> {
    const response = await api.get<Skill>(`/profiles/${profileId}/skills/${id}`)
    return response.data
  },

  async createSkill(profileId: number, data: SkillCreate): Promise<Skill> {
    const response = await api.post<Skill>(`/profiles/${profileId}/skills`, data)
    return response.data
  },

  async updateSkill(profileId: number, id: number, data: SkillUpdate): Promise<Skill> {
    const response = await api.put<Skill>(`/profiles/${profileId}/skills/${id}`, data)
    return response.data
  },

  async deleteSkill(profileId: number, id: number): Promise<void> {
    await api.delete(`/profiles/${profileId}/skills/${id}`)
  },
}

// Resume API
export const resumeApi = {
  async getResumes(): Promise<GeneratedResume[]> {
    const response = await api.get<GeneratedResume[]>('/resumes')
    return response.data
  },

  async getResume(id: number): Promise<GeneratedResume> {
    const response = await api.get<GeneratedResume>(`/resumes/${id}`)
    return response.data
  },

  async generateResume(data: ResumeGenerateRequest): Promise<GeneratedResume> {
    const response = await api.post<GeneratedResume>('/resumes/generate', data)
    return response.data
  },

  async generateResumeForProfile(profileId: number, jobDescription: string): Promise<GeneratedResume> {
    const response = await api.post<GeneratedResume>(
      `/profiles/${profileId}/resumes/generate_resume`,
      { job_description: jobDescription }
    )
    return response.data
  },

  async deleteResume(id: number): Promise<void> {
    await api.delete(`/resumes/${id}`)
  },
}

export default api 