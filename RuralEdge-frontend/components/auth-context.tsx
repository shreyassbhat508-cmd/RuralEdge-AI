'use client'

import React, { createContext, useContext, useEffect, useState } from 'react'

export interface User {
  id: string
  name: string
  email: string
}

interface AuthContextType {
  user: User | null
  signIn: (user: User) => void
  signOut: () => void
  isLoading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Check localStorage on mount
    try {
      const storedUser = localStorage.getItem('ruraledge_demo_user')
      if (storedUser) {
        setUser(JSON.parse(storedUser))
      }
    } catch (e) {
      console.error('Failed to parse user from local storage', e)
    } finally {
      setIsLoading(false)
    }
  }, [])

  const signIn = (userData: User) => {
    setUser(userData)
    localStorage.setItem('ruraledge_demo_user', JSON.stringify(userData))
  }

  const signOut = () => {
    setUser(null)
    localStorage.removeItem('ruraledge_demo_user')
  }

  return (
    <AuthContext.Provider value={{ user, signIn, signOut, isLoading }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
