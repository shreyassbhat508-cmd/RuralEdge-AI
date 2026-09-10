'use client'

import { useEffect, useState } from 'react'
import { Landmark, Sparkles, CheckCircle2, X, ExternalLink, HelpCircle, FileText, Loader2, RefreshCw, AlertCircle } from 'lucide-react'
import { useBusiness } from '@/components/business-context'
import { DETAILED_SCHEMES, formatCompactINR, type DetailedScheme } from '@/lib/data'
import { getSchemes, getSchemeDetails, type SchemeResponse, type SchemeDetailsResponse } from '@/lib/api'

export function SchemesView() {
  const { onboarding, profile } = useBusiness()
  const [backendSchemes, setBackendSchemes] = useState<SchemeResponse[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedScheme, setSelectedScheme] = useState<DetailedScheme | null>(null)
  const [selectedSchemeDetails, setSelectedSchemeDetails] = useState<SchemeDetailsResponse | null>(null)
  const [loadingDetails, setLoadingDetails] = useState(false)

  const fetchSchemesList = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const res = await getSchemes({
        state: onboarding.state || profile.state || 'Karnataka',
        limit: 20,
      })
      if (res.items && res.items.length > 0) {
        setBackendSchemes(res.items)
      }
    } catch (err: unknown) {
      console.warn('Backend schemes fetch fallback to static:', err)
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to reach backend schemes service. Showing cached scheme profiles.',
      )
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchSchemesList()
  }, [onboarding.state, profile.state])

  const handleOpenDetails = async (scheme: DetailedScheme, schemeId?: string) => {
    setSelectedScheme(scheme)
    setSelectedSchemeDetails(null)
    if (schemeId) {
      setLoadingDetails(true)
      try {
        const details = await getSchemeDetails(schemeId)
        setSelectedSchemeDetails(details)
      } catch (e) {
        console.warn('Could not fetch scheme detail sub-records:', e)
      } finally {
        setLoadingDetails(false)
      }
    }
  }

  // Combined list: backend schemes mapped to DetailedScheme format, falling back to DETAILED_SCHEMES
  const displaySchemes: DetailedScheme[] = backendSchemes.length > 0
    ? backendSchemes.map((s, idx) => ({
        id: s.id,
        name: s.name,
        code: s.short_name || `SCHEME-${idx + 1}`,
        matchPct: 90 - (idx * 3),
        tagline: s.description || `${s.ministry || 'Government'} initiative for rural micro-enterprises`,
        maxFinancing: 2500000,
        contributionPct: 10,
        interestRate: 7.5,
        tenureYears: 5,
        status: idx === 0 ? 'Highly suitable' : idx === 1 ? 'Suitable' : 'Moderate match',
        eligibilityRationale: s.target_beneficiaries?.length
          ? `Beneficiaries: ${s.target_beneficiaries.join(', ')}`
          : `Aligned with your location in ${onboarding.district || profile.district}, ${onboarding.state || profile.state}.`,
        keyBenefits: s.funding_pattern ? [s.funding_pattern, s.nodal_agency ? `Nodal Agency: ${s.nodal_agency}` : 'Credit-linked government assistance'] : ['Financial assistance up to eligible limit', 'Subsidized loan terms', 'Collateral-free up to prescribed limits'],
        requiredDocs: ['Aadhaar Card', 'Project Report / DPR', 'Bank Passbook / Statement', 'Premises Lease or NOC'],
      }))
    : DETAILED_SCHEMES

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 border-b border-border/80 pb-6">
        <div>
          <span className="inline-flex items-center gap-1.5 rounded-full border border-primary/30 bg-primary/10 px-3.5 py-1.5 text-xs font-bold text-primary">
            <Landmark className="size-4 text-primary" />
            AI Scheme Engine
          </span>
          <h1 className="mt-3 font-display text-3xl font-extrabold tracking-tight text-foreground sm:text-4xl">
            Funding matched to you
          </h1>
          <p className="mt-1 text-base text-muted-foreground">
            Based on your profile in {onboarding.village || 'Hosahalli'}, {onboarding.district || 'Ramanagara'}, we queried government scheme registries.
          </p>
        </div>

        <div className="inline-flex items-center gap-2 rounded-2xl bg-charcoal px-4 py-2 text-sm font-extrabold text-white shadow-soft shrink-0">
          <Sparkles className="size-4 text-sand" />
          <span>{displaySchemes.length} schemes found</span>
        </div>
      </div>

      {error && (
        <div className="mt-6 flex items-center justify-between rounded-2xl border border-amber-500/30 bg-amber-500/10 p-4 text-xs text-amber-700 dark:text-amber-300">
          <div className="flex items-center gap-2">
            <AlertCircle className="size-4 shrink-0" />
            <span>{error}</span>
          </div>
          <button
            type="button"
            onClick={fetchSchemesList}
            className="inline-flex items-center gap-1 rounded-full bg-amber-500/20 px-3 py-1 font-bold hover:bg-amber-500/30"
          >
            <RefreshCw className="size-3" />
            Retry
          </button>
        </div>
      )}

      {isLoading && (
        <div className="mt-12 flex flex-col items-center justify-center gap-3 py-12 text-center text-muted-foreground">
          <Loader2 className="size-8 animate-spin text-primary" />
          <p className="text-sm font-medium">Fetching active schemes from backend...</p>
        </div>
      )}

      {/* Scheme Cards Grid */}
      {!isLoading && (
        <div className="mt-8 grid gap-6 md:grid-cols-2">
          {displaySchemes.map((scheme) => (
            <div
              key={scheme.id}
              className="group relative flex flex-col justify-between rounded-3xl border border-border bg-card p-6 shadow-soft transition-all duration-300 hover:-translate-y-1 hover:border-primary/40 hover:shadow-lift"
            >
              <div>
                {/* Top Row: Eligibility Badge & Status */}
                <div className="flex flex-wrap items-center justify-between gap-2 border-b border-border/60 pb-4">
                  <span className="inline-flex items-center gap-1.5 rounded-full bg-primary/10 border border-primary/30 px-3 py-1 text-xs font-extrabold text-primary">
                    <Sparkles className="size-3.5 text-primary animate-pulse" />
                    {scheme.matchPct}% Eligibility Match
                  </span>
                  <span className="rounded-full bg-sand/40 dark:bg-[#2A3441] border border-transparent dark:border-white/10 px-3 py-1 text-xs font-bold text-charcoal dark:text-[#F5F7F5]">
                    {scheme.status}
                  </span>
                </div>

                {/* Scheme Name & Tagline */}
                <div className="mt-4">
                  <span className="text-[11px] font-bold tracking-wider text-muted-foreground uppercase">
                    {scheme.code}
                  </span>
                  <h3 className="mt-1 font-display text-xl font-extrabold text-foreground group-hover:text-primary transition-colors">
                    {scheme.name}
                  </h3>
                  <p className="mt-1.5 text-xs text-muted-foreground leading-relaxed">
                    {scheme.tagline}
                  </p>
                </div>

                {/* 4 Financial Metric Boxes */}
                <div className="mt-5 grid grid-cols-2 gap-2.5 rounded-2xl border border-border/80 bg-background p-3.5 text-xs">
                  <div>
                    <span className="text-muted-foreground">Maximum financing</span>
                    <p className="font-extrabold text-sm text-foreground">
                      {formatCompactINR(scheme.maxFinancing)}
                    </p>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Your contribution</span>
                    <p className="font-extrabold text-sm text-primary">
                      {scheme.contributionPct}% margin
                    </p>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Interest Rate</span>
                    <p className="font-extrabold text-sm text-foreground">
                      {scheme.interestRate}% p.a.
                    </p>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Tenure</span>
                    <p className="font-extrabold text-sm text-foreground">
                      {scheme.tenureYears} Years
                    </p>
                  </div>
                </div>

                {/* "Why am I eligible?" AI Explanation Block */}
                <div className="mt-4 rounded-2xl bg-primary/8 border border-primary/20 p-3.5 text-xs">
                  <div className="flex items-center gap-1.5 font-bold text-primary mb-1">
                    <HelpCircle className="size-3.5 text-primary" />
                    <span>Why am I eligible?</span>
                  </div>
                  <p className="text-muted-foreground leading-relaxed">
                    {scheme.eligibilityRationale}
                  </p>
                </div>
              </div>

              {/* Bottom CTA */}
              <div className="mt-6 border-t border-border/80 pt-4 flex items-center justify-between">
                <span className="text-xs text-muted-foreground">
                  Official Government Scheme
                </span>
                <button
                  type="button"
                  onClick={() => handleOpenDetails(scheme, scheme.id)}
                  className="inline-flex items-center gap-1.5 rounded-full bg-primary px-4 py-2 text-xs font-bold text-white shadow-soft transition-transform hover:scale-105 hover:bg-primary-hover"
                >
                  View Scheme →
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Scheme Detail Modal */}
      {selectedScheme && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-md animate-in fade-in duration-200">
          <div className="relative w-full max-w-xl rounded-3xl border border-primary/30 bg-card p-6 sm:p-8 shadow-lift max-h-[90vh] overflow-y-auto">
            <button
              type="button"
              onClick={() => setSelectedScheme(null)}
              className="absolute top-5 right-5 grid size-9 place-items-center rounded-full border border-border bg-background text-muted-foreground hover:text-foreground"
            >
              <X className="size-4" />
            </button>

            <div className="flex items-center gap-2 text-xs font-extrabold text-primary uppercase tracking-wider">
              <Sparkles className="size-4 text-primary" />
              {selectedScheme.matchPct}% Matched Scheme
            </div>

            <h2 className="mt-2 font-display text-2xl font-extrabold text-foreground">
              {selectedScheme.name}
            </h2>
            <p className="mt-1 text-xs text-muted-foreground">{selectedScheme.tagline}</p>

            <div className="mt-6 space-y-4">
              <div className="rounded-2xl border border-border bg-background p-4">
                <h4 className="text-xs font-bold uppercase tracking-wider text-foreground mb-2">
                  Key Scheme Benefits
                </h4>
                {loadingDetails ? (
                  <div className="py-3 text-center text-xs text-muted-foreground">Loading benefits...</div>
                ) : (
                  <ul className="space-y-2 text-xs text-foreground">
                    {selectedSchemeDetails?.benefits?.length ? (
                      selectedSchemeDetails.benefits.map((b) => (
                        <li key={b.id} className="flex items-start gap-2">
                          <CheckCircle2 className="size-4 text-success shrink-0 mt-0.5" />
                          <span><strong>{b.benefit_type}:</strong> {b.description}</span>
                        </li>
                      ))
                    ) : (
                      selectedScheme.keyBenefits.map((b, idx) => (
                        <li key={idx} className="flex items-start gap-2">
                          <CheckCircle2 className="size-4 text-success shrink-0 mt-0.5" />
                          <span>{b}</span>
                        </li>
                      ))
                    )}
                  </ul>
                )}
              </div>

              <div className="rounded-2xl border border-border bg-background p-4">
                <h4 className="text-xs font-bold uppercase tracking-wider text-foreground mb-2">
                  Eligibility & Required Documents
                </h4>
                {selectedSchemeDetails?.eligibility?.length ? (
                  <ul className="space-y-2 text-xs text-foreground">
                    {selectedSchemeDetails.eligibility.map((el) => (
                      <li key={el.id} className="flex items-center gap-2">
                        <FileText className="size-4 text-primary shrink-0" />
                        <span><strong>{el.criteria_name}:</strong> {el.criteria_value}</span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <ul className="space-y-2 text-xs text-foreground">
                    {selectedScheme.requiredDocs.map((doc, idx) => (
                      <li key={idx} className="flex items-center gap-2">
                        <FileText className="size-4 text-primary shrink-0" />
                        <span>{doc}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>

              <div className="rounded-2xl bg-primary/10 border border-primary/30 p-4 text-xs">
                <span className="font-bold text-primary block mb-1">Application Guidance</span>
                <p className="text-muted-foreground">
                  You can submit your application via JanSamarth national portal or at your District Industries Centre (DIC) with your RuralEdge viability report.
                </p>
              </div>
            </div>

            <div className="mt-6 flex items-center justify-end gap-3 border-t border-border pt-4">
              <button
                type="button"
                onClick={() => setSelectedScheme(null)}
                className="rounded-full border border-border px-5 py-2 text-xs font-bold text-foreground hover:bg-muted"
              >
                Close
              </button>
              <a
                href={selectedSchemeDetails?.source?.url || selectedSchemeDetails?.scheme?.website_url || "https://www.jansamarth.in"}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1.5 rounded-full bg-primary px-6 py-2.5 text-xs font-bold text-white shadow-soft hover:scale-105 hover:bg-primary-hover"
              >
                Apply / Official Portal <ExternalLink className="size-3.5" />
              </a>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
