'use client'

import {
  createContext,
  useCallback,
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
  formatCompactINR,
  formatINR,
  type BusinessProfile,
  type DocumentItem,
  type FinancePlan,
  type RecommendationProfile,
} from '@/lib/data'
import {
  analyzeBusiness,
  type BusinessAnalyzeRequest,
  type BusinessAnalyzeResponse,
} from '@/lib/api'

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
  businessAnalysis: BusinessAnalyzeResponse | null
  setBusinessAnalysis: (res: BusinessAnalyzeResponse | null) => void
  isAnalyzing: boolean
  analysisError: string | null
  runAnalysis: (overridePayload?: Partial<BusinessAnalyzeRequest>) => Promise<BusinessAnalyzeResponse>
}

const BusinessContext = createContext<BusinessContextValue | null>(null)

function mapCategory(interests: string[]): string {
  if (!interests || interests.length === 0) return 'Dairy'
  const primary = interests[0].toLowerCase()
  const mapping: Record<string, string> = {
    dairy: 'Dairy',
    poultry: 'Poultry',
    farming: 'Farming',
    food: 'Food Processing',
    retail: 'Retail',
    manufacturing: 'Manufacturing',
    digital: 'Services',
    recycling: 'Agri-Services',
  }
  return mapping[primary] || 'Dairy'
}

export function BusinessProvider({ children }: { children: ReactNode }) {
  const [profile, setProfile] = useState<BusinessProfile>(DEFAULT_PROFILE)
  const [language, setLanguage] = useState('en')
  const [hasCompletedAssessment, setHasCompletedAssessment] = useState(false)
  const [activeRecommendation, setActiveRecommendation] =
    useState<RecommendationProfile>(MAIN_RECOMMENDATION)
  const [businessAnalysis, setBusinessAnalysis] =
    useState<BusinessAnalyzeResponse | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisError, setAnalysisError] = useState<string | null>(null)

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

  // Offline UI preview fallback for finance
  const marginToUse = onboarding.budget > 0 ? onboarding.budget / 2 : profile.margin
  const fallbackFinance = useMemo(() => computeFinance(marginToUse), [marginToUse])

  // Real backend analysis finance representation
  const finance = useMemo<FinancePlan>(() => {
    if (businessAnalysis?.finance) {
      const bf = businessAnalysis.finance
      return {
        margin: bf.own_contribution,
        projectCost: bf.project_cost,
        loan: bf.loan_amount,
        scheme: {
          id: bf.project_cost <= 140000 ? 'micro' : 'term',
          name: businessAnalysis.scheme?.recommended_scheme || 'Term Loan Scheme',
          tagline: 'Calculated by RuralEdge backend finance engine',
          minCost: 0,
          maxCost: 5000000,
          fundingPct: bf.project_cost > 0 ? bf.loan_amount / bf.project_cost : 0.9,
          maxLoan: bf.loan_amount,
          interest: 7.0,
          tenureYears: bf.payback_months ? Math.round(bf.payback_months / 12) : 5,
          moratoriumMonths: 6,
          audience: 'Rural micro and small enterprises',
        },
        capApplied: false,
        aboveMax: bf.project_cost > 5000000,
        emi: bf.emi,
        totalInterest: bf.total_interest,
        totalPayable: bf.loan_amount + bf.total_interest,
        monthlyDuringMoratorium: (bf.loan_amount * 0.07) / 12,
        appliedMoratoriumMonths: 6,
        interestTreatment: 'pay_separately',
      }
    }
    return fallbackFinance
  }, [businessAnalysis, fallbackFinance])

  const updateOnboarding = (patch: Partial<OnboardingState>) => {
    setOnboarding((prev) => {
      const next = { ...prev, ...patch }
      if (patch.budget && patch.budget !== prev.budget) {
        setProfile((p) => ({ ...p, margin: patch.budget! / 2 }))
      }
      return next
    })
  }

  const runAnalysis = useCallback(
    async (overridePayload?: Partial<BusinessAnalyzeRequest>): Promise<BusinessAnalyzeResponse> => {
      setIsAnalyzing(true)
      setAnalysisError(null)

      const category =
        overridePayload?.business_category || mapCategory(onboarding.selectedInterests)
      const margin =
        overridePayload?.margin_capital ??
        (onboarding.budget > 0 ? onboarding.budget : profile.margin || 100000)
      // Project cost default: 10x margin (10% own contribution)
      const projectCost =
        overridePayload?.project_cost ??
        Math.max(margin * 10, 100000)

      const payload: BusinessAnalyzeRequest = {
        location: {
          state: overridePayload?.location?.state || onboarding.state || profile.state || 'Karnataka',
          district: overridePayload?.location?.district || onboarding.district || profile.district || 'Ramanagara',
          village: overridePayload?.location?.village || onboarding.village || profile.village || 'Hosahalli',
        },
        business_category: category,
        margin_capital: margin,
        project_cost: projectCost,
      }

      try {
        const response = await analyzeBusiness(payload)
        setBusinessAnalysis(response)

        // Sync recommendation profile
        const newRec: RecommendationProfile = {
          title: response.business?.category
            ? `${response.business.category} Enterprise`
            : MAIN_RECOMMENDATION.title,
          category: response.business?.category || 'Livestock & Agriculture',
          matchScore: response.opportunity?.score ?? MAIN_RECOMMENDATION.matchScore,
          description:
            response.opportunity?.reasons?.[0] ||
            `Tailored for ${payload.location.village}, ${payload.location.district} under ${response.scheme?.recommended_scheme || 'Government Scheme'}.`,
          demandScore: response.opportunity?.components?.market ?? 85,
          demandLabel:
            response.opportunity?.level === 'High'
              ? 'High local demand'
              : `${response.opportunity?.level || 'Solid'} viability`,
          investmentAmount: response.finance.project_cost,
          fundingAmount: response.finance.loan_amount,
          competitionLevel:
            response.market.status === 'success' && response.market.competitor_count !== null
              ? response.market.competitor_count > 5
                ? 'High'
                : response.market.competitor_count > 2
                  ? 'Moderate'
                  : 'Low'
              : 'Data Unavailable',
          whyWeRecommend:
            response.opportunity?.reasons?.length > 0
              ? response.opportunity.reasons
              : MAIN_RECOMMENDATION.whyWeRecommend,
          keyHighlights: [
            { label: 'Monthly EMI', value: formatINR(response.finance.emi) },
            {
              label: 'Tenure',
              value: `${response.finance.payback_months ? Math.round(response.finance.payback_months / 12) : 5} Years`,
            },
            {
              label: 'Own Contribution',
              value: formatCompactINR(response.finance.own_contribution),
            },
            {
              label: 'Loan Scheme',
              value: response.scheme.recommended_scheme || 'PMEGP / Term Loan',
            },
          ],
        }

        setActiveRecommendation(newRec)
        setProfile((prev) => ({
          ...prev,
          state: payload.location.state,
          district: payload.location.district,
          village: payload.location.village || prev.village,
          margin: payload.margin_capital,
          typeLabel: `${category} Enterprise`,
        }))

        return response
      } catch (err: unknown) {
        const errorMsg =
          err instanceof Error
            ? err.message
            : 'Unable to connect to RuralEdge backend analysis service.'
        setAnalysisError(errorMsg)
        throw err
      } finally {
        setIsAnalyzing(false)
      }
    },
    [onboarding, profile],
  )

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
      businessAnalysis,
      setBusinessAnalysis,
      isAnalyzing,
      analysisError,
      runAnalysis,
    }),
    [
      profile,
      finance,
      language,
      hasCompletedAssessment,
      onboarding,
      documents,
      activeRecommendation,
      businessAnalysis,
      isAnalyzing,
      analysisError,
      runAnalysis,
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
