'use client'

import { useState, useEffect, useCallback } from 'react'
import Link from 'next/link'
import {
  ArrowUpRight,
  Banknote,
  Calculator,
  Landmark,
  Lightbulb,
  MapPinned,
  MessageCircle,
  Pencil,
  TrendingDown,
  TrendingUp,
  Wallet,
  CheckCircle2,
  Clock,
  FileCheck,
  CheckSquare,
  Sparkles,
  ChevronRight,
  RefreshCw,
  AlertTriangle,
  Info,
} from 'lucide-react'
import { useBusiness } from '@/components/business-context'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { CountUp } from '@/components/count-up'
import { PlainTip } from '@/components/plain-tip'
import { HealthGauge } from '@/components/charts/health-gauge'
import { RevenueTrendChart } from '@/components/charts/revenue-trend-chart'
import { CostBreakdownChart } from '@/components/charts/cost-breakdown-chart'
import { BreakEvenChart } from '@/components/charts/break-even-chart'
import {
  JOURNEY_STEPS,
  OPERATING,
  buildBreakEven,
  formatCompactINR,
  formatINR,
} from '@/lib/data'
import { analyzeBusiness } from '@/lib/api/business'
import { BusinessAnalyzeResponse, BusinessAnalyzeRequest } from '@/lib/api/types'
import { cn } from '@/lib/utils'

const QUICK_ACTIONS = [
  { href: '/market', icon: MapPinned, label: 'Market Intelligence', tone: 'text-primary bg-primary/10' },
  { href: '/finance', icon: Calculator, label: 'Financial Plan', tone: 'text-primary bg-primary/10' },
  { href: '/schemes', icon: Landmark, label: 'Government Support', tone: 'text-charcoal bg-sand/40 dark:text-foreground' },
  { href: '/advisor', icon: MessageCircle, label: 'Ask RuralEdge AI', tone: 'text-muted bg-muted/15' },
]

export function DashboardView() {
  const { profile, finance, documents, toggleDocument, activeRecommendation, onboarding } = useBusiness()
  
  // API State for /api/business/analyze
  const [analysis, setAnalysis] = useState<BusinessAnalyzeResponse | null>(null)
  const [analysisLoading, setAnalysisLoading] = useState<boolean>(true)
  const [analysisError, setAnalysisError] = useState<string | null>(null)

  const fetchAnalysis = useCallback(async () => {
    setAnalysisLoading(true)
    setAnalysisError(null)

    const state = onboarding.state || profile.state || 'Karnataka'
    const district = onboarding.district || profile.district || 'Kodagu'
    const village = onboarding.village || profile.village || 'XYZ Village'
    const category = onboarding.selectedInterests[0] || 'Dairy'
    const margin = onboarding.budget > 0 ? onboarding.budget / 2 : profile.margin || 100000
    const cost = margin * 10 || 1000000

    // Basic Validation
    if (!state.trim() || !district.trim()) {
      setAnalysisError('State and District location details are required')
      setAnalysisLoading(false)
      return
    }

    if (margin < 0 || cost <= 0 || margin > cost) {
      setAnalysisError('Invalid financial margin capital or project cost values')
      setAnalysisLoading(false)
      return
    }

    try {
      const reqPayload: BusinessAnalyzeRequest = {
        location: { state, district, village },
        business_category: category,
        margin_capital: margin,
        project_cost: cost,
      }

      const res = await analyzeBusiness(reqPayload)
      setAnalysis(res)
    } catch (err: any) {
      console.error('Error fetching business analysis:', err)
      setAnalysisError(err.message || 'Failed to fetch business analysis from FastAPI endpoint')
    } finally {
      setAnalysisLoading(false)
    }
  }, [onboarding, profile])

  useEffect(() => {
    fetchAnalysis()
  }, [fetchAnalysis])

  const rec = activeRecommendation

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
      {/* Top Header Greeting */}
      <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between border-b border-border/80 pb-6">
        <div>
          <span className="inline-flex items-center gap-1.5 text-xs font-bold text-primary uppercase tracking-wider">
            Good morning 👋
          </span>
          <h1 className="mt-1 font-display text-3xl font-extrabold tracking-tight md:text-4xl text-foreground">
            {profile.ownerName}&apos;s Enterprise Dashboard
          </h1>
          <p className="mt-1 text-base text-muted-foreground">
            Your personalized rural business roadmap in {onboarding.village || profile.village}, {onboarding.district || profile.district}, {onboarding.state || profile.state}.
          </p>
        </div>
        <Link
          href="/assessment"
          className="inline-flex w-fit items-center gap-2 rounded-full border border-border bg-card px-5 py-2.5 text-sm font-bold text-foreground transition-all hover:bg-muted hover:scale-105"
        >
          <Pencil className="size-4 text-primary" />
          Update Assessment
        </Link>
      </div>

      {/* Main Selected Business Banner */}
      <div className="mt-8 rounded-3xl border border-primary/30 bg-card p-6 sm:p-8 shadow-lift relative overflow-hidden">
        <div className="absolute top-0 right-0 h-40 w-40 bg-radial from-primary/15 to-transparent blur-3xl pointer-events-none" />

        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-border/80 pb-6">
          <div className="flex items-center gap-4">
            <div className="grid size-14 place-items-center rounded-2xl bg-charcoal text-3xl shadow-soft">
              🐄
            </div>
            <div>
              <span className="text-xs font-bold uppercase tracking-wider text-primary">
                ACTIVE BUSINESS PLAN
              </span>
              <h2 className="text-2xl font-extrabold text-foreground sm:text-3xl">
                {rec.title}
              </h2>
            </div>
          </div>

          <div className="flex items-center gap-2 rounded-2xl bg-primary/10 border border-primary/30 px-4 py-2">
            <Sparkles className="size-5 text-primary animate-pulse" />
            <span className="text-2xl font-black text-primary">{rec.matchScore}%</span>
            <span className="text-xs font-bold text-primary uppercase">Viability Index</span>
          </div>
        </div>

        {/* Financial Summary */}
        <div className="mt-6 grid grid-cols-2 gap-4 lg:grid-cols-3">
          <div className="rounded-2xl border border-border/80 bg-background p-4">
            <p className="text-xs font-bold uppercase text-muted-foreground">Project Cost</p>
            <p className="mt-1.5 text-2xl font-black text-foreground">
              {formatCompactINR(finance.projectCost || rec.investmentAmount)}
            </p>
          </div>

          <div className="rounded-2xl border border-border/80 bg-background p-4">
            <p className="text-xs font-bold uppercase text-muted-foreground">Your Contribution</p>
            <p className="mt-1.5 text-2xl font-black text-primary">
              {formatCompactINR(finance.margin)}
            </p>
          </div>

          <div className="col-span-2 lg:col-span-1 rounded-2xl border border-primary/30 bg-primary/10 p-4">
            <p className="text-xs font-bold uppercase text-primary">Potential Financing</p>
            <p className="mt-1.5 text-2xl font-black text-primary">
              {formatCompactINR(finance.loan || rec.fundingAmount)}
            </p>
          </div>
        </div>
      </div>

      {/* ==================================================
          FASTAPI CORE BUSINESS ANALYSIS SECTION (POST /api/business/analyze)
          ================================================== */}
      <div className="mt-10 rounded-3xl border border-primary/40 bg-card/95 backdrop-blur-md p-6 sm:p-8 shadow-soft">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border/80 pb-4">
          <div>
            <span className="inline-flex items-center gap-1.5 rounded-full border border-primary/30 bg-primary/10 px-3 py-1 text-xs font-extrabold text-primary">
              <Sparkles className="size-3.5" />
              FastAPI Core Endpoint
            </span>
            <h3 className="mt-2 font-display text-2xl font-extrabold text-foreground">
              Business Analysis (`POST /api/business/analyze`)
            </h3>
          </div>

          <button
            type="button"
            onClick={fetchAnalysis}
            disabled={analysisLoading}
            className="inline-flex items-center gap-2 rounded-full border border-border bg-background px-4 py-2 text-xs font-bold text-foreground hover:bg-muted disabled:opacity-50"
          >
            <RefreshCw className={cn('size-3.5', analysisLoading && 'animate-spin')} />
            Refresh Analysis
          </button>
        </div>

        {analysisLoading ? (
          <div className="py-12 flex flex-col items-center justify-center text-center">
            <RefreshCw className="size-8 animate-spin text-primary mb-3" />
            <p className="text-sm font-semibold text-muted-foreground">
              Executing business analysis query on FastAPI backend...
            </p>
          </div>
        ) : analysisError ? (
          <div className="mt-6 rounded-2xl border border-destructive/30 bg-destructive/10 p-6 text-center">
            <AlertTriangle className="mx-auto size-8 text-destructive mb-2" />
            <h4 className="font-bold text-foreground text-base">Analysis Request Failed</h4>
            <p className="mt-1 text-xs text-muted-foreground">{analysisError}</p>
            <button
              type="button"
              onClick={fetchAnalysis}
              className="mt-4 rounded-full bg-primary px-4 py-2 text-xs font-bold text-white shadow-soft"
            >
              Retry
            </button>
          </div>
        ) : analysis ? (
          <div className="mt-6 space-y-6">
            {/* Top 6 Result Blocks Grid */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {/* 1. BUSINESS BLOCK */}
              <div className="rounded-2xl border border-border bg-background p-5">
                <span className="text-[10px] font-extrabold uppercase tracking-wider text-muted-foreground">
                  1. BUSINESS DETAILS
                </span>
                <h4 className="mt-2 font-extrabold text-lg text-foreground">
                  {analysis.business.category}
                </h4>
                <p className="mt-1 text-xs text-muted-foreground">
                  {[
                    analysis.business.location.village,
                    analysis.business.location.district,
                    analysis.business.location.state,
                  ]
                    .filter(Boolean)
                    .join(', ')}
                </p>
                <div className="mt-4 grid grid-cols-2 gap-2 text-xs border-t border-border/60 pt-3">
                  <div>
                    <span className="text-muted-foreground block">Cost:</span>
                    <span className="font-bold text-foreground">{formatINR(analysis.business.project_cost)}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground block">Margin:</span>
                    <span className="font-bold text-primary">{formatINR(analysis.business.margin_capital)}</span>
                  </div>
                </div>
              </div>

              {/* 2. MARKET BLOCK */}
              <div className="rounded-2xl border border-border bg-background p-5">
                <span className="text-[10px] font-extrabold uppercase tracking-wider text-muted-foreground">
                  2. MARKET INTELLIGENCE
                </span>
                {analysis.market.status === 'insufficient_data' ? (
                  <div className="mt-3 rounded-xl border border-amber-500/30 bg-amber-500/10 p-3 text-xs text-amber-700 dark:text-amber-300">
                    <Info className="size-4 shrink-0 mb-1 text-amber-600" />
                    <span>Market intelligence data is not available yet.</span>
                  </div>
                ) : (
                  <p className="mt-3 text-xs text-foreground">{analysis.market.message}</p>
                )}
              </div>

              {/* 3. OPPORTUNITY BLOCK */}
              <div className="rounded-2xl border border-border bg-background p-5">
                <span className="text-[10px] font-extrabold uppercase tracking-wider text-muted-foreground">
                  3. OPPORTUNITY RATING
                </span>
                {analysis.opportunity.score === null ? (
                  <div className="mt-3 rounded-xl border border-border bg-card p-3 text-xs text-muted-foreground">
                    <span className="font-bold text-foreground block mb-1">Status: {analysis.opportunity.status}</span>
                    <p>{analysis.opportunity.message}</p>
                  </div>
                ) : (
                  <div className="mt-2 text-2xl font-black text-primary">
                    {analysis.opportunity.score}% Score
                  </div>
                )}
              </div>

              {/* 4. FINANCE BLOCK */}
              <div className="rounded-2xl border border-border bg-background p-5">
                <span className="text-[10px] font-extrabold uppercase tracking-wider text-muted-foreground">
                  4. FINANCIAL STRUCTURE
                </span>
                <div className="mt-3 space-y-1.5 text-xs">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Loan Amount:</span>
                    <span className="font-bold text-primary">{formatINR(analysis.finance.loan_amount)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Margin Share:</span>
                    <span className="font-bold text-foreground">{analysis.finance.margin_percentage}%</span>
                  </div>
                  {analysis.finance.approx_monthly_payment && (
                    <div className="flex justify-between border-t border-border/60 pt-1.5">
                      <span className="text-muted-foreground">Est. Monthly EMI:</span>
                      <span className="font-extrabold text-foreground">{formatINR(analysis.finance.approx_monthly_payment)}</span>
                    </div>
                  )}
                </div>
              </div>

              {/* 5. SCHEME BLOCK */}
              <div className="rounded-2xl border border-border bg-background p-5">
                <span className="text-[10px] font-extrabold uppercase tracking-wider text-muted-foreground">
                  5. SCHEME MATCHING
                </span>
                {analysis.scheme.status === 'matched' && analysis.scheme.recommended_scheme ? (
                  <div className="mt-2">
                    <span className="inline-flex rounded-full bg-primary/10 px-2.5 py-0.5 text-[10px] font-extrabold text-primary border border-primary/30">
                      {analysis.scheme.recommended_scheme.match_score}% Match
                    </span>
                    <h5 className="mt-1 font-bold text-sm text-foreground line-clamp-1">
                      {analysis.scheme.recommended_scheme.name}
                    </h5>
                    <p className="mt-1 text-[11px] text-muted-foreground line-clamp-2">
                      {analysis.scheme.recommended_scheme.description}
                    </p>
                  </div>
                ) : (
                  <div className="mt-3 text-xs text-muted-foreground">
                    No matching government scheme found in database.
                  </div>
                )}
              </div>

              {/* 6. SWOT BLOCK */}
              <div className="rounded-2xl border border-border bg-background p-5">
                <span className="text-[10px] font-extrabold uppercase tracking-wider text-muted-foreground">
                  6. PRELIMINARY SWOT
                </span>
                <div className="mt-2 space-y-2 text-xs">
                  {analysis.swot.strengths.length > 0 && (
                    <div>
                      <span className="font-bold text-success block">Strengths:</span>
                      <ul className="list-disc list-inside text-muted-foreground">
                        {analysis.swot.strengths.map((s, idx) => (
                          <li key={idx}>{s}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {analysis.swot.weaknesses.length > 0 && (
                    <div>
                      <span className="font-bold text-amber-600 dark:text-amber-400 block">Weaknesses:</span>
                      <ul className="list-disc list-inside text-muted-foreground">
                        {analysis.swot.weaknesses.map((w, idx) => (
                          <li key={idx}>{w}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        ) : null}
      </div>

      {/* Business Health Radar Metrics */}
      <div className="mt-8">
        <h3 className="font-display text-xl font-extrabold text-foreground">
          Business Health Scorecard
        </h3>
        <p className="text-xs text-muted-foreground">
          Real-time viability indicators derived from regional micro-data.
        </p>

        <div className="mt-4 grid grid-cols-2 gap-4 lg:grid-cols-4">
          <HealthMetric title="DEMAND" value={92} label="High local demand" color="bg-primary" />
          <HealthMetric title="RESOURCES" value={91} label="Suitable land & water" color="bg-charcoal" />
          <HealthMetric title="FUNDING" value={88} label="Eligible for PMEGP" color="bg-primary" />
          <HealthMetric title="COMPETITION" value={71} label="Moderate competition" color="bg-muted" />
        </div>
      </div>

      {/* Business Journey & Document Checklist */}
      <div className="mt-10 grid gap-6 lg:grid-cols-2">
        {/* Journey Timeline */}
        <Card className="rounded-3xl border-border shadow-soft">
          <CardHeader>
            <div className="flex items-center gap-2">
              <Clock className="size-5 text-primary" />
              <CardTitle className="text-xl">Your Business Journey</CardTitle>
            </div>
            <p className="text-xs text-muted-foreground">
              Step-by-step roadmap to launcher readiness.
            </p>
          </CardHeader>
          <CardContent className="space-y-4">
            {JOURNEY_STEPS.map((step) => (
              <div key={step.id} className="flex items-start gap-3 text-sm">
                <span
                  className={cn(
                    'grid size-7 shrink-0 place-items-center rounded-full text-xs font-extrabold mt-0.5',
                    step.status === 'completed'
                      ? 'bg-primary text-white'
                      : step.status === 'current'
                        ? 'bg-primary/20 text-primary border border-primary/40'
                        : 'bg-muted text-muted-foreground',
                  )}
                >
                  {step.status === 'completed' ? <CheckCircle2 className="size-4" /> : step.id}
                </span>
                <div>
                  <h4 className="font-bold text-foreground leading-snug">{step.title}</h4>
                  <p className="text-xs text-muted-foreground">{step.subtitle}</p>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Required Documents Checklist */}
        <Card className="rounded-3xl border-border shadow-soft">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <FileCheck className="size-5 text-primary" />
                <CardTitle className="text-xl">Document Checklist</CardTitle>
              </div>
              <span className="text-xs font-bold text-primary bg-primary/10 px-3 py-1 rounded-full">
                {documents.filter((d) => d.isDone).length} of {documents.length} ready
              </span>
            </div>
            <p className="text-xs text-muted-foreground">
              Click items to toggle completion state as you prepare your loan file.
            </p>
          </CardHeader>
          <CardContent className="space-y-3">
            {documents.map((doc) => (
              <div
                key={doc.id}
                onClick={() => toggleDocument(doc.id)}
                className={cn(
                  'flex items-center justify-between p-3.5 rounded-2xl border cursor-pointer transition-all',
                  doc.isDone
                    ? 'bg-primary/10 border-primary/30 text-foreground'
                    : 'bg-background border-border hover:border-primary/40',
                )}
              >
                <div className="flex items-center gap-3">
                  <span
                    className={cn(
                      'grid size-6 place-items-center rounded-lg border',
                      doc.isDone
                        ? 'bg-primary text-white border-primary'
                        : 'border-muted-foreground',
                    )}
                  >
                    {doc.isDone && <CheckCircle2 className="size-4" />}
                  </span>
                  <div>
                    <h5 className="font-bold text-xs">{doc.title}</h5>
                    <p className="text-[11px] text-muted-foreground">{doc.description}</p>
                  </div>
                </div>
                <span
                  className={cn(
                    'text-[10px] font-extrabold uppercase px-2.5 py-1 rounded-full',
                    doc.isDone ? 'bg-primary text-white' : 'bg-muted text-muted-foreground',
                  )}
                >
                  {doc.isDone ? 'READY' : 'PENDING'}
                </span>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      {/* Quick Navigation Cards */}
      <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {QUICK_ACTIONS.map((a) => {
          const Icon = a.icon
          return (
            <Link
              key={a.href}
              href={a.href}
              className="group flex items-center gap-3 rounded-2xl border border-border bg-card p-4 shadow-soft transition-transform hover:-translate-y-1"
            >
              <span className={cn('grid size-11 place-items-center rounded-xl', a.tone)}>
                <Icon className="size-5" />
              </span>
              <span className="flex-1 font-bold text-sm text-foreground">{a.label}</span>
              <ArrowUpRight className="size-4 text-muted-foreground transition-colors group-hover:text-primary" />
            </Link>
          )
        })}
      </div>
    </div>
  )
}

function HealthMetric({
  title,
  value,
  label,
  color,
}: {
  title: string
  value: number
  label: string
  color: string
}) {
  return (
    <div className="rounded-2xl border border-border bg-card p-4 shadow-soft">
      <div className="flex items-center justify-between text-xs font-bold uppercase tracking-wider text-muted-foreground">
        <span>{title}</span>
        <span className="text-foreground font-black">{value}%</span>
      </div>
      <div className="mt-2.5 h-2 w-full rounded-full bg-muted overflow-hidden">
        <div className={cn('h-full rounded-full', color)} style={{ width: `${value}%` }} />
      </div>
    </div>
  )
}
