'use client'

import { useState, useEffect, useCallback } from 'react'
import Link from 'next/link'
import { motion } from 'framer-motion'
import {
  Sparkles,
  ArrowRight,
  CheckCircle2,
  TrendingUp,
  BadgeIndianRupee,
  ShieldCheck,
  Building2,
  ChevronRight,
  RefreshCw,
  AlertTriangle,
  Landmark,
  AlertCircle,
} from 'lucide-react'
import { useBusiness } from '@/components/business-context'
import { formatCompactINR, formatINR } from '@/lib/data'
import { getRecommendations } from '@/lib/api/recommendations'
import { SchemeRecommendation, RecommendationRequest } from '@/lib/api/types'
import { cn } from '@/lib/utils'

export function RecommendationView({ onComplete }: { onComplete?: () => void }) {
  const { onboarding, profile } = useBusiness()
  const [recommendations, setRecommendations] = useState<SchemeRecommendation[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedRecIndex, setSelectedRecIndex] = useState<number>(0)

  const fetchBackendRecommendations = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const payload: RecommendationRequest = {
        state: onboarding.state || 'Karnataka',
        district: onboarding.district || 'Ramanagara',
        age: profile.age || 30,
        gender: profile.gender || 'female',
        occupation: onboarding.selectedInterests[0] || 'farmer',
        annual_income: profile.annualIncome || 150000,
        caste_category: profile.category || 'General',
        education: 'graduate',
        disability: false,
        land_owned: onboarding.selectedResources.includes('land'),
        business_exists: false,
      }

      const results = await getRecommendations(payload)
      setRecommendations(results || [])
    } catch (err: any) {
      console.error('Error fetching recommendations:', err)
      setError(err.message || 'Failed to fetch recommendations from FastAPI server')
    } finally {
      setLoading(false)
    }
  }, [onboarding, profile])

  useEffect(() => {
    fetchBackendRecommendations()
  }, [fetchBackendRecommendations])

  const activeRec = recommendations[selectedRecIndex] || null

  return (
    <div className="mx-auto w-full max-w-4xl px-4 py-8 sm:px-6">
      {/* Top Banner Header */}
      <div className="text-center">
        <span className="inline-flex items-center gap-2 rounded-full border border-primary/30 bg-primary/10 px-4 py-1.5 text-xs font-bold text-primary">
          <Sparkles className="size-4 text-primary animate-pulse" />
          FastAPI Scheme Recommendation Engine
        </span>
        <h1 className="mt-4 font-display text-3xl font-extrabold tracking-tight text-foreground sm:text-4xl">
          Matched Schemes & Opportunities
        </h1>
        <p className="mt-2 text-base text-muted-foreground">
          Calculated for {onboarding.village || 'Hosahalli'}, {onboarding.district || 'Ramanagara'} ({onboarding.state || 'Karnataka'}) with budget of {formatINR(onboarding.budget || 200000)}.
        </p>
      </div>

      {loading ? (
        <div className="mt-12 flex flex-col items-center justify-center rounded-3xl border border-border bg-card p-12 text-center">
          <RefreshCw className="size-8 animate-spin text-primary mb-3" />
          <p className="text-sm font-semibold text-muted-foreground">
            Evaluating deterministic scheme match scores via FastAPI backend...
          </p>
        </div>
      ) : error ? (
        <div className="mt-8 rounded-3xl border border-destructive/30 bg-destructive/10 p-8 text-center">
          <AlertTriangle className="mx-auto size-10 text-destructive mb-3" />
          <h3 className="font-bold text-foreground text-lg">Recommendation Request Failed</h3>
          <p className="mt-1 text-xs text-muted-foreground max-w-md mx-auto">{error}</p>
          <button
            type="button"
            onClick={fetchBackendRecommendations}
            className="mt-5 inline-flex items-center gap-2 rounded-full bg-primary px-6 py-2.5 text-xs font-bold text-white shadow-soft hover:bg-primary-hover"
          >
            <RefreshCw className="size-3.5" /> Retry Request
          </button>
        </div>
      ) : recommendations.length === 0 ? (
        <div className="mt-12 flex flex-col items-center justify-center rounded-3xl border border-border bg-card p-12 text-center">
          <Landmark className="size-12 text-muted-foreground mb-3 opacity-50" />
          <h3 className="font-bold text-foreground text-lg">No Recommendations Available</h3>
          <p className="mt-1 text-xs text-muted-foreground max-w-md">
            No matching government schemes were found for your specified demographic profile and location.
          </p>
        </div>
      ) : (
        <>
          {/* Main Selected Recommendation Card */}
          {activeRec && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-8 overflow-hidden rounded-3xl border border-primary/30 bg-card p-6 sm:p-8 shadow-lift relative"
            >
              <div className="absolute top-0 right-0 h-48 w-48 bg-radial from-primary/15 to-transparent blur-3xl pointer-events-none" />

              {/* Card Title & Deterministic Match Score */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border/80 pb-6">
                <div className="flex items-center gap-4">
                  <div className="grid size-14 place-items-center rounded-2xl bg-charcoal text-3xl shadow-soft">
                    🏛️
                  </div>
                  <div>
                    <span className="text-xs font-bold uppercase tracking-wider text-primary">
                      {activeRec.scheme.scheme_type || 'Government Scheme'}
                    </span>
                    <h2 className="text-2xl font-extrabold text-foreground sm:text-3xl">
                      {activeRec.scheme.name}
                    </h2>
                    {activeRec.scheme.short_name && (
                      <span className="text-xs font-semibold text-muted-foreground">
                        ({activeRec.scheme.short_name})
                      </span>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-2 self-start sm:self-auto rounded-2xl bg-primary/10 border border-primary/30 px-4 py-2.5">
                  <Sparkles className="size-5 text-primary" />
                  <div>
                    <span className="text-2xl font-black text-primary">
                      {activeRec.match_score}%
                    </span>
                    <span className="ml-1 text-xs font-bold text-primary uppercase">
                      Match Score
                    </span>
                  </div>
                </div>
              </div>

              <p className="mt-4 text-sm leading-relaxed text-muted-foreground">
                {activeRec.scheme.description || 'Verified government scheme record matched by FastAPI deterministic algorithm.'}
              </p>

              {/* Scheme Financial Benefits Summary */}
              {activeRec.benefits && activeRec.benefits.length > 0 && (
                <div className="mt-6 grid grid-cols-2 gap-4 lg:grid-cols-4">
                  {activeRec.benefits.map((benefit, idx) => (
                    <div key={idx} className="rounded-2xl border border-border/80 bg-background p-4 relative">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
                        BENEFIT {idx + 1}
                      </span>
                      <div className="mt-2 text-xl font-black text-foreground">
                        {benefit.maximum_amount ? formatCompactINR(benefit.maximum_amount) : 'Financial Grant'}
                      </div>
                      <p className="mt-1 text-xs text-primary font-semibold">
                        {benefit.subsidy_percentage ? `${benefit.subsidy_percentage}% Subsidy` : 'Direct Assistance'}
                      </p>
                      {benefit.interest_rate !== undefined && benefit.interest_rate !== null && (
                        <p className="mt-0.5 text-[11px] text-muted-foreground">
                          {benefit.interest_rate}% p.a. Interest
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {/* Match Reasons (Returned directly by Backend) */}
              <div className="mt-8 border-t border-border/80 pt-6">
                <h3 className="text-lg font-bold text-foreground">
                  Match Reasons (Backend Evaluation)
                </h3>
                {activeRec.match_reasons.length === 0 ? (
                  <p className="mt-2 text-xs text-muted-foreground">Base eligibility criteria matched.</p>
                ) : (
                  <ul className="mt-3 grid gap-2.5 sm:grid-cols-2">
                    {activeRec.match_reasons.map((reason, idx) => (
                      <li key={idx} className="flex items-start gap-2.5 text-sm text-foreground">
                        <CheckCircle2 className="size-5 shrink-0 text-success mt-0.5" />
                        <span className="font-medium">{reason}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>

              {/* Warnings (Returned directly by Backend) */}
              {activeRec.warnings && activeRec.warnings.length > 0 && (
                <div className="mt-6 rounded-2xl border border-amber-500/30 bg-amber-500/10 p-4 text-xs">
                  <div className="flex items-center gap-2 font-bold text-amber-700 dark:text-amber-400 mb-1.5">
                    <AlertCircle className="size-4 shrink-0" />
                    <span>Evaluation Warnings</span>
                  </div>
                  <ul className="space-y-1 text-amber-800 dark:text-amber-300">
                    {activeRec.warnings.map((w, idx) => (
                      <li key={idx}>• {w}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Primary CTA */}
              <div className="mt-8 flex flex-col sm:flex-row items-center justify-between gap-4 border-t border-border/80 pt-6">
                <div className="text-xs text-muted-foreground">
                  View complete business, loan & financial plan on your dashboard.
                </div>
                <Link
                  href="/dashboard"
                  onClick={onComplete}
                  className="w-full sm:w-auto inline-flex items-center justify-center gap-2 rounded-full bg-primary px-8 py-4 text-base font-bold text-white shadow-lift transition-all hover:scale-105 hover:bg-primary-hover"
                >
                  View Complete Business Plan →
                </Link>
              </div>
            </motion.div>
          )}

          {/* Alternative Recommended Schemes */}
          {recommendations.length > 1 && (
            <div className="mt-12">
              <h3 className="font-display text-xl font-extrabold text-foreground">
                Other Matched Schemes ({recommendations.length - 1})
              </h3>
              <p className="text-sm text-muted-foreground">
                Select another scheme recommended for your profile.
              </p>

              <div className="mt-5 grid gap-4 sm:grid-cols-3">
                {recommendations.map((rec, idx) => {
                  if (idx === selectedRecIndex) return null
                  return (
                    <div
                      key={rec.scheme.id}
                      onClick={() => setSelectedRecIndex(idx)}
                      className={cn(
                        'group cursor-pointer rounded-2xl border p-5 transition-all hover:-translate-y-1 hover:shadow-soft border-border bg-card hover:border-primary/40'
                      )}
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-primary uppercase truncate max-w-[120px]">
                          {rec.scheme.short_name || 'SCHEME'}
                        </span>
                        <span className="rounded-full bg-primary/10 border border-primary/30 px-2.5 py-0.5 text-xs font-extrabold text-primary">
                          {rec.match_score}% score
                        </span>
                      </div>

                      <h4 className="mt-3 font-bold text-base text-foreground leading-snug line-clamp-2">
                        {rec.scheme.name}
                      </h4>
                      <p className="mt-1 text-xs text-muted-foreground line-clamp-2">
                        {rec.scheme.description || 'Verified government scheme.'}
                      </p>

                      <div className="mt-4 flex items-center justify-between text-xs border-t border-border/60 pt-3">
                        <span className="text-muted-foreground">View details</span>
                        <ChevronRight className="size-4 text-primary transition-transform group-hover:translate-x-1" />
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}
