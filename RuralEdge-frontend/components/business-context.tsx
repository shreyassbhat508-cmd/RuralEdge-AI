'use client'

import {
  createContext,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import {
  DEFAULT_PROFILE,
  DOCUMENT_CHECKLIST,
  MAIN_RECOMMENDATION,
  computeFinance,
  type BusinessProfile,
  type DocumentItem,
  type FinancePlan,
  type RecommendationProfile,
} from '@/lib/data'

export interface OnboardingState {
  state: string
  district: string
  village: string
  budget: number
  selectedResources: string[]
  selectedInterests: string[]
  isAiDecide: boolean
}

interface BusinessContextValue {
  profile: BusinessProfile
  setProfile: (p: BusinessProfile) => void
  updateProfile: (patch: Partial<BusinessProfile>) => void
  finance: FinancePlan
  language: string
  setLanguage: (code: string) => void
  hasCompletedAssessment: boolean
  setHasCompletedAssessment: (v: boolean) => void
  onboarding: OnboardingState
  setOnboarding: React.Dispatch<React.SetStateAction<OnboardingState>>
  updateOnboarding: (patch: Partial<OnboardingState>) => void
  documents: DocumentItem[]
  toggleDocument: (id: string) => void
  activeRecommendation: RecommendationProfile
  setActiveRecommendation: (rec: RecommendationProfile) => void
}

const BusinessContext = createContext<BusinessContextValue | null>(null)

export function BusinessProvider({ children }: { children: ReactNode }) {
  const [profile, setProfile] = useState<BusinessProfile>(DEFAULT_PROFILE)
  const [language, setLanguage] = useState('en')
  const [hasCompletedAssessment, setHasCompletedAssessment] = useState(false)
  const [activeRecommendation, setActiveRecommendation] =
    useState<RecommendationProfile>(MAIN_RECOMMENDATION)

  const [onboarding, setOnboarding] = useState<OnboardingState>({
    state: 'Karnataka',
    district: 'Ramanagara',
    village: 'Hosahalli',
    budget: 200000,
    selectedResources: ['land', 'water'],
    selectedInterests: ['dairy'],
    isAiDecide: false,
  })

  const [documents, setDocuments] = useState<DocumentItem[]>(DOCUMENT_CHECKLIST)

  const toggleDocument = (id: string) => {
    setDocuments((prev) =>
      prev.map((doc) => (doc.id === id ? { ...doc, isDone: !doc.isDone } : doc)),
    )
  }

  // Synchronize margin from onboarding budget or profile.margin
  const marginToUse = onboarding.budget > 0 ? onboarding.budget / 2 : profile.margin
  const finance = useMemo(() => computeFinance(marginToUse), [marginToUse])

  const updateOnboarding = (patch: Partial<OnboardingState>) => {
    setOnboarding((prev) => {
      const next = { ...prev, ...patch }
      if (patch.budget && patch.budget !== prev.budget) {
        setProfile((p) => ({ ...p, margin: patch.budget! / 2 }))
      }
      return next
    })
  }

  const value = useMemo<BusinessContextValue>(
    () => ({
      profile,
      setProfile,
      updateProfile: (patch) => setProfile((prev) => ({ ...prev, ...patch })),
      finance,
      language,
      setLanguage,
      hasCompletedAssessment,
      setHasCompletedAssessment,
      onboarding,
      setOnboarding,
      updateOnboarding,
      documents,
      toggleDocument,
      activeRecommendation,
      setActiveRecommendation,
    }),
    [
      profile,
      finance,
      language,
      hasCompletedAssessment,
      onboarding,
      documents,
      activeRecommendation,
    ],
  )

  return (
    <BusinessContext.Provider value={value}>
      {children}
    </BusinessContext.Provider>
  )
}

export function useBusiness() {
  const ctx = useContext(BusinessContext)
  if (!ctx) throw new Error('useBusiness must be used within BusinessProvider')
  return ctx
}

