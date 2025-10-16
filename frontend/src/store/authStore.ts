import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { User } from '../types'

interface AuthState {
  user: User | null
  token: string | null
  setAuth: (user: User, token: string) => void
  clearAuth: () => void
  isAuthenticated: () => boolean
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      setAuth: (user, token) => {
        set({ user, token })
        localStorage.setItem('access_token', token)
      },
      clearAuth: () => {
        set({ user: null, token: null })
        localStorage.removeItem('access_token')
      },
      isAuthenticated: () => {
        return !!get().token
      },
    }),
    {
      name: 'auth-storage',
    }
  )
)

