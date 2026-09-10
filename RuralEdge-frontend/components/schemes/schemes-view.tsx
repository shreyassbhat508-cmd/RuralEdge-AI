'use client'

import { useState, useEffect, useCallback } from 'react'
import { Landmark, Sparkles, CheckCircle2, ChevronRight, X, ExternalLink, HelpCircle, FileText, RefreshCw, Search, AlertTriangle } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useBusiness } from '@/components/business-context'
import { formatCompactINR, formatINR } from '@/lib/data'
import { getSchemes, searchSchemes, getSchemeDetails } from '@/lib/api/schemes'
import { SchemeResponse, SchemeDetailsResponse, ApiError } from '@/lib/api/types'

export function SchemesView() {
  const { onboarding } = useBusiness()
  const [schemes, setSchemes] = useState<SchemeResponse[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [totalCount, setTotalCount] = useState(0)

  // Selected scheme modal state
  const [selectedSchemeId, setSelectedSchemeId] = useState<string | null>(null)
  const [selectedDetails, setSelectedDetails] = useState<SchemeDetailsResponse | null>(null)
  const [modalLoading, setModalLoading] = useState(false)
  const [modalError, setModalError] = useState<string | null>(null)

  const fetchSchemesList = useCallback(async (query = '') => {
    setLoading(true)
    setError(null)
    try {
      if (query.trim()) {
        const results = await searchSchemes({ query: query.trim() })
        setSchemes(results || [])
        setTotalCount(results?.length || 0)
      } else {
        const res = await getSchemes({ page: 1, limit: 50 })
        setSchemes(res.items || [])
        setTotalCount(res.total || res.items?.length || 0)
      }
    } catch (err: any) {
      console.error('Error fetching schemes:', err)
      setError(err.message || 'Failed to load schemes from server')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchSchemesList()
  }, [fetchSchemesList])

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    fetchSchemesList(searchQuery)
  }

  const handleViewScheme = async (schemeId: string) => {
    setSelectedSchemeId(schemeId)
    setModalLoading(true)
    setModalError(null)
    setSelectedDetails(null)
    try {
      const details = await getSchemeDetails(schemeId)
      setSelectedDetails(details)
    } catch (err: any) {
      console.error('Error fetching scheme details:', err)
      setModalError(err.message || 'Failed to load scheme details')
    } finally {
      setModalLoading(false)
    }
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 border-b border-border/80 pb-6">
        <div>
          <span className="inline-flex items-center gap-1.5 rounded-full border border-primary/30 bg-primary/10 px-3.5 py-1.5 text-xs font-bold text-primary">
            <Landmark className="size-4 text-primary" />
            Government Scheme Engine
          </span>
          <h1 className="mt-3 font-display text-3xl font-extrabold tracking-tight text-foreground sm:text-4xl">
            Government Schemes & Grants
          </h1>
          <p className="mt-1 text-base text-muted-foreground">
            Explore verified government schemes available for {onboarding.village || 'Hosahalli'}, {onboarding.district || 'Ramanagara'}, {onboarding.state || 'Karnataka'}.
          </p>
        </div>

        <div className="inline-flex items-center gap-2 rounded-2xl bg-charcoal px-4 py-2 text-sm font-extrabold text-white shadow-soft shrink-0">
          <Sparkles className="size-4 text-sand" />
          <span>{loading ? 'Searching...' : `${totalCount} schemes found`}</span>
        </div>
      </div>

      {/* Search Bar */}
      <form onSubmit={handleSearchSubmit} className="mt-6 flex gap-3 max-w-xl">
        <div className="relative flex-1">
          <Search className="absolute left-3.5 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search schemes by keyword, ministry, or details..."
            className="w-full rounded-full border border-input bg-card pl-10 pr-4 py-2.5 text-xs font-semibold text-foreground placeholder:text-muted-foreground outline-none focus:ring-2 focus:ring-ring"
          />
          {searchQuery && (
            <button
              type="button"
              onClick={() => {
                setSearchQuery('')
                fetchSchemesList('')
              }}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground text-xs"
            >
              <X className="size-4" />
            </button>
          )}
        </div>
        <button
          type="submit"
          disabled={loading}
          className="rounded-full bg-primary px-5 py-2.5 text-xs font-extrabold text-white shadow-soft hover:bg-primary-hover disabled:opacity-50"
        >
          Search
        </button>
      </form>

      {/* Content Area */}
      {loading ? (
        <div className="mt-12 flex flex-col items-center justify-center p-12 text-center">
          <RefreshCw className="size-8 animate-spin text-primary mb-3" />
          <p className="text-sm font-semibold text-muted-foreground">Loading schemes from FastAPI backend...</p>
        </div>
      ) : error ? (
        <div className="mt-8 rounded-3xl border border-destructive/30 bg-destructive/10 p-6 text-center">
          <AlertTriangle className="mx-auto size-8 text-destructive mb-2" />
          <h3 className="font-bold text-foreground text-base">Failed to Load Schemes</h3>
          <p className="mt-1 text-xs text-muted-foreground">{error}</p>
          <button
            type="button"
            onClick={() => fetchSchemesList(searchQuery)}
            className="mt-4 inline-flex items-center gap-2 rounded-full bg-primary px-4 py-2 text-xs font-bold text-white shadow-soft hover:bg-primary-hover"
          >
            <RefreshCw className="size-3.5" /> Retry
          </button>
        </div>
      ) : schemes.length === 0 ? (
        <div className="mt-12 flex flex-col items-center justify-center rounded-3xl border border-border bg-card p-12 text-center">
          <Landmark className="size-12 text-muted-foreground mb-3 opacity-50" />
          <h3 className="font-bold text-foreground text-lg">No Schemes Found</h3>
          <p className="mt-1 text-xs text-muted-foreground max-w-md">
            No government schemes match your criteria in the database. Try clearing your search or updating filters.
          </p>
          {searchQuery && (
            <button
              type="button"
              onClick={() => {
                setSearchQuery('')
                fetchSchemesList('')
              }}
              className="mt-4 rounded-full border border-border bg-background px-4 py-2 text-xs font-bold text-foreground hover:bg-muted"
            >
              Clear Search
            </button>
          )}
        </div>
      ) : (
        /* Scheme Cards Grid */
        <div className="mt-8 grid gap-6 md:grid-cols-2">
          {schemes.map((scheme) => (
            <div
              key={scheme.id}
              className="group relative flex flex-col justify-between rounded-3xl border border-border bg-card p-6 shadow-soft transition-all duration-300 hover:-translate-y-1 hover:border-primary/40 hover:shadow-lift"
            >
              <div>
                {/* Top Row */}
                <div className="flex flex-wrap items-center justify-between gap-2 border-b border-border/60 pb-4">
                  <span className="inline-flex items-center gap-1.5 rounded-full bg-primary/10 border border-primary/30 px-3 py-1 text-xs font-extrabold text-primary">
                    {scheme.scheme_type || 'Central / State'}
                  </span>
                  <span className="rounded-full bg-sand/40 dark:bg-[#2A3441] border border-transparent dark:border-white/10 px-3 py-1 text-xs font-bold text-charcoal dark:text-[#F5F7F5]">
                    {scheme.status || 'Active'}
                  </span>
                </div>

                {/* Scheme Name & Ministry */}
                <div className="mt-4">
                  <span className="text-[11px] font-bold tracking-wider text-muted-foreground uppercase">
                    {scheme.short_name || scheme.ministry || 'GOI SCHEME'}
                  </span>
                  <h3 className="mt-1 font-display text-xl font-extrabold text-foreground group-hover:text-primary transition-colors">
                    {scheme.name}
                  </h3>
                  <p className="mt-1.5 text-xs text-muted-foreground leading-relaxed line-clamp-3">
                    {scheme.description || 'No detailed description provided.'}
                  </p>
                </div>

                {/* Meta details box */}
                <div className="mt-5 grid grid-cols-2 gap-2.5 rounded-2xl border border-border/80 bg-background p-3.5 text-xs">
                  <div>
                    <span className="text-muted-foreground">Ministry</span>
                    <p className="font-extrabold text-xs text-foreground truncate">
                      {scheme.ministry || 'N/A'}
                    </p>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Department</span>
                    <p className="font-extrabold text-xs text-foreground truncate">
                      {scheme.department || 'N/A'}
                    </p>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Target Group</span>
                    <p className="font-extrabold text-xs text-foreground truncate">
                      {typeof scheme.target_beneficiaries === 'string'
                        ? scheme.target_beneficiaries
                        : Array.isArray(scheme.target_beneficiaries)
                        ? scheme.target_beneficiaries.join(', ')
                        : 'General'}
                    </p>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Launch Date</span>
                    <p className="font-extrabold text-xs text-foreground">
                      {scheme.launch_date || 'N/A'}
                    </p>
                  </div>
                </div>
              </div>

              {/* Bottom CTA */}
              <div className="mt-6 border-t border-border/80 pt-4 flex items-center justify-between">
                <span className="text-xs text-muted-foreground truncate max-w-[200px]">
                  {scheme.official_url ? 'Official portal available' : 'Verified Database Record'}
                </span>
                <button
                  type="button"
                  onClick={() => handleViewScheme(scheme.id)}
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
      {selectedSchemeId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-md animate-in fade-in duration-200">
          <div className="relative w-full max-w-xl rounded-3xl border border-primary/30 bg-card p-6 sm:p-8 shadow-lift max-h-[90vh] overflow-y-auto">
            <button
              type="button"
              onClick={() => {
                setSelectedSchemeId(null)
                setSelectedDetails(null)
              }}
              className="absolute top-5 right-5 grid size-9 place-items-center rounded-full border border-border bg-background text-muted-foreground hover:text-foreground"
            >
              <X className="size-4" />
            </button>

            {modalLoading ? (
              <div className="flex flex-col items-center justify-center p-12 text-center">
                <RefreshCw className="size-8 animate-spin text-primary mb-3" />
                <p className="text-xs font-semibold text-muted-foreground">Loading scheme details...</p>
              </div>
            ) : modalError ? (
              <div className="p-4 text-center">
                <AlertTriangle className="mx-auto size-8 text-destructive mb-2" />
                <p className="text-xs text-destructive font-semibold">{modalError}</p>
                <button
                  type="button"
                  onClick={() => handleViewScheme(selectedSchemeId)}
                  className="mt-4 rounded-full bg-primary px-4 py-2 text-xs font-bold text-white"
                >
                  Retry
                </button>
              </div>
            ) : selectedDetails ? (
              <>
                <div className="flex items-center gap-2 text-xs font-extrabold text-primary uppercase tracking-wider">
                  <Landmark className="size-4 text-primary" />
                  {selectedDetails.scheme.scheme_type || 'Government Scheme'}
                </div>

                <h2 className="mt-2 font-display text-2xl font-extrabold text-foreground">
                  {selectedDetails.scheme.name}
                </h2>
                {selectedDetails.scheme.short_name && (
                  <span className="text-xs font-bold text-muted-foreground">
                    ({selectedDetails.scheme.short_name})
                  </span>
                )}
                <p className="mt-2 text-xs text-muted-foreground leading-relaxed">
                  {selectedDetails.scheme.description}
                </p>

                <div className="mt-6 space-y-4">
                  {/* Eligibility Criteria */}
                  <div className="rounded-2xl border border-border bg-background p-4">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-foreground mb-2">
                      Eligibility Requirements
                    </h4>
                    {selectedDetails.eligibility.length === 0 ? (
                      <p className="text-xs text-muted-foreground">No specific eligibility constraints listed.</p>
                    ) : (
                      <ul className="space-y-2 text-xs text-foreground">
                        {selectedDetails.eligibility.map((e) => (
                          <li key={e.id} className="flex items-start gap-2">
                            <CheckCircle2 className="size-4 text-success shrink-0 mt-0.5" />
                            <span>
                              {[
                                e.occupation && `Occupation: ${e.occupation}`,
                                e.gender && `Gender: ${e.gender}`,
                                e.caste_category && `Category: ${e.caste_category}`,
                                e.min_age && `Min Age: ${e.min_age}`,
                                e.max_age && `Max Age: ${e.max_age}`,
                                e.max_income && `Max Income: ₹${e.max_income.toLocaleString('en-IN')}`,
                                e.land_required && 'Land Ownership Required',
                              ]
                                .filter(Boolean)
                                .join(' • ') || 'General Eligibility Criteria'}
                            </span>
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>

                  {/* Financial & Non-Financial Benefits */}
                  <div className="rounded-2xl border border-border bg-background p-4">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-foreground mb-2">
                      Scheme Benefits & Financing
                    </h4>
                    {selectedDetails.benefits.length === 0 ? (
                      <p className="text-xs text-muted-foreground">Standard scheme guidelines apply.</p>
                    ) : (
                      <ul className="space-y-2 text-xs text-foreground">
                        {selectedDetails.benefits.map((b) => (
                          <li key={b.id} className="flex items-start gap-2">
                            <Sparkles className="size-4 text-primary shrink-0 mt-0.5" />
                            <span>
                              {[
                                b.maximum_amount && `Max Limit: ${formatINR(b.maximum_amount)}`,
                                b.subsidy_percentage && `Subsidy: ${b.subsidy_percentage}%`,
                                b.interest_rate && `Interest Rate: ${b.interest_rate}% p.a.`,
                                b.repayment_period_months && `Tenure: ${b.repayment_period_months} months`,
                                b.moratorium_months && `Grace Period: ${b.moratorium_months} months`,
                              ]
                                .filter(Boolean)
                                .join(' • ') || 'Financial Assistance Scheme'}
                            </span>
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                </div>

                <div className="mt-6 flex items-center justify-end gap-3 border-t border-border pt-4">
                  <button
                    type="button"
                    onClick={() => {
                      setSelectedSchemeId(null)
                      setSelectedDetails(null)
                    }}
                    className="rounded-full border border-border px-5 py-2 text-xs font-bold text-foreground hover:bg-muted"
                  >
                    Close
                  </button>
                  {selectedDetails.scheme.official_url || selectedDetails.scheme.application_url ? (
                    <a
                      href={selectedDetails.scheme.application_url || selectedDetails.scheme.official_url || '#'}
                      target="_blank"
                      rel="noreferrer"
                      className="inline-flex items-center gap-1.5 rounded-full bg-primary px-6 py-2.5 text-xs font-bold text-white shadow-soft hover:scale-105 hover:bg-primary-hover"
                    >
                      Official Portal <ExternalLink className="size-3.5" />
                    </a>
                  ) : null}
                </div>
              </>
            ) : null}
          </div>
        </div>
      )}
    </div>
  )
}
