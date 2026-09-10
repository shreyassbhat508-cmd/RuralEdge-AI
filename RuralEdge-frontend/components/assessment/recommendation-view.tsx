'use client'

import Link from 'next/link'
import { motion } from 'framer-motion'
import {
  Sparkles,
  CheckCircle2,
  TrendingUp,
  BadgeIndianRupee,
  ShieldCheck,
  Building2,
  ChevronRight,
} from 'lucide-react'
import { useBusiness } from '@/components/business-context'
import {
  MAIN_RECOMMENDATION,
  ALTERNATIVE_RECOMMENDATIONS,
  formatCompactINR,
  formatINR,
} from '@/lib/data'
import { cn } from '@/lib/utils'

export function RecommendationView({ onComplete }: { onComplete?: () => void }) {
  const { activeRecommendation, setActiveRecommendation, onboarding, businessAnalysis } = useBusiness()

  const current = activeRecommendation || MAIN_RECOMMENDATION

  const isMarketUnavailable = businessAnalysis?.market?.status === 'unavailable'
  const competitorCount = businessAnalysis?.market?.competitor_count

  const competitionText = isMarketUnavailable
    ? 'Market data temporarily unavailable'
    : competitorCount !== null && competitorCount !== undefined
      ? `${competitorCount} competitors within ${businessAnalysis?.market?.radius_km || 10}km`
      : 'Local analysis completed'

  const competitionLevel = isMarketUnavailable
    ? 'Unavailable'
    : competitorCount !== null && competitorCount !== undefined
      ? competitorCount > 5
        ? 'High'
        : competitorCount > 2
          ? 'Moderate'
          : 'Low'
      : current.competitionLevel

  return (
    <div className="mx-auto w-full max-w-4xl px-4 py-8 sm:px-6">
      {/* Top Banner Header */}
      <div className="text-center">
        <span className="inline-flex items-center gap-2 rounded-full border border-primary/30 bg-primary/10 px-4 py-1.5 text-xs font-bold text-primary">
          <Sparkles className="size-4 text-primary animate-pulse" />
          RuralEdge AI Feasibility Result
        </span>
        <h1 className="mt-4 font-display text-3xl font-extrabold tracking-tight text-foreground sm:text-4xl">
          Your best opportunity
        </h1>
        <p className="mt-2 text-base text-muted-foreground">
          Calculated for {onboarding.village || 'Hosahalli'}, {onboarding.district || 'Ramanagara'} with starting budget of {formatINR(onboarding.budget || 200000)}.
        </p>
      </div>

      {/* Main Recommendation Card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mt-8 overflow-hidden rounded-3xl border border-primary/30 bg-card p-6 sm:p-8 shadow-lift relative"
      >
        <div className="absolute top-0 right-0 h-48 w-48 bg-radial from-primary/15 to-transparent blur-3xl pointer-events-none" />

        {/* Card Title & Viability Score */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border/80 pb-6">
          <div className="flex items-center gap-4">
            <div className="grid size-14 place-items-center rounded-2xl bg-charcoal text-3xl shadow-soft">
              🐄
            </div>
            <div>
              <span className="text-xs font-bold uppercase tracking-wider text-primary">
                {current.category}
              </span>
              <h2 className="text-2xl font-extrabold text-foreground sm:text-3xl">
                {current.title}
              </h2>
            </div>
          </div>

          <div className="flex items-center gap-2 self-start sm:self-auto rounded-2xl bg-primary/10 border border-primary/30 px-4 py-2.5">
            <Sparkles className="size-5 text-primary" />
            <div>
              <span className="text-2xl font-black text-primary">
                {current.matchScore}%
              </span>
              <span className="ml-1 text-xs font-bold text-primary uppercase">
                Feasibility Index
              </span>
            </div>
          </div>
        </div>

        <p className="mt-4 text-sm leading-relaxed text-muted-foreground">
          {current.description}
        </p>

        {/* 4 Large Metric Cards */}
        <div className="mt-6 grid grid-cols-2 gap-4 lg:grid-cols-4">
          {/* DEMAND METRIC */}
          <div className="rounded-2xl border border-border/80 bg-background p-4 relative overflow-hidden">
            <div className="flex items-center justify-between text-xs font-bold uppercase tracking-wider text-muted-foreground">
              <span>DEMAND</span>
              <TrendingUp className="size-4 text-primary" />
            </div>
            <div className="mt-3 flex items-baseline gap-2">
              <span className="text-3xl font-black text-foreground">
                {current.demandScore}%
              </span>
            </div>
            <p className="mt-1 text-xs font-semibold text-primary">
              {current.demandLabel}
            </p>
            <div className="mt-3 h-1.5 w-full rounded-full bg-muted overflow-hidden">
              <div
                className="h-full bg-primary rounded-full"
                style={{ width: `${current.demandScore}%` }}
              />
            </div>
          </div>

          {/* INVESTMENT METRIC */}
          <div className="rounded-2xl border border-border/80 bg-background p-4 relative overflow-hidden">
            <div className="flex items-center justify-between text-xs font-bold uppercase tracking-wider text-muted-foreground">
              <span>INVESTMENT</span>
              <BadgeIndianRupee className="size-4 text-sand" />
            </div>
            <div className="mt-3">
              <span className="text-3xl font-black text-foreground">
                {formatCompactINR(current.investmentAmount)}
              </span>
            </div>
            <p className="mt-1 text-xs text-muted-foreground">
              Estimated project cost
            </p>
            <div className="mt-3 h-1.5 w-full rounded-full bg-muted overflow-hidden">
              <div className="h-full bg-sand rounded-full w-full" />
            </div>
          </div>

          {/* FUNDING METRIC */}
          <div className="rounded-2xl border border-border/80 bg-background p-4 relative overflow-hidden">
            <div className="flex items-center justify-between text-xs font-bold uppercase tracking-wider text-muted-foreground">
              <span>FUNDING</span>
              <ShieldCheck className="size-4 text-primary" />
            </div>
            <div className="mt-3">
              <span className="text-3xl font-black text-primary">
                {formatCompactINR(current.fundingAmount)}
              </span>
            </div>
            <p className="mt-1 text-xs text-muted-foreground">
              Potential scheme loan
            </p>
            <div className="mt-3 h-1.5 w-full rounded-full bg-muted overflow-hidden">
              <div className="h-full bg-primary rounded-full w-[90%]" />
            </div>
          </div>

          {/* COMPETITION METRIC */}
          <div className="rounded-2xl border border-border/80 bg-background p-4 relative overflow-hidden">
            <div className="flex items-center justify-between text-xs font-bold uppercase tracking-wider text-muted-foreground">
              <span>COMPETITION</span>
              <Building2 className="size-4 text-muted" />
            </div>
            <div className="mt-3">
              <span className="text-2xl font-black text-foreground">
                {competitionLevel}
              </span>
            </div>
            <p className="mt-1 text-xs text-muted-foreground truncate" title={competitionText}>
              {competitionText}
            </p>
            <div className="mt-3 h-1.5 w-full rounded-full bg-muted overflow-hidden">
              <div className="h-full bg-muted rounded-full w-[50%]" />
            </div>
          </div>
        </div>

        {/* Why We Recommend This */}
        <div className="mt-8 border-t border-border/80 pt-6">
          <h3 className="text-lg font-bold text-foreground">
            Feasibility & Scheme Signals
          </h3>
          <ul className="mt-3 grid gap-2.5 sm:grid-cols-2">
            {current.whyWeRecommend.map((reason, idx) => (
              <li key={idx} className="flex items-start gap-2.5 text-sm text-foreground">
                <CheckCircle2 className="size-5 shrink-0 text-success mt-0.5" />
                <span className="font-medium">{reason}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Primary CTA */}
        <div className="mt-8 flex flex-col sm:flex-row items-center justify-between gap-4 border-t border-border/80 pt-6">
          <div className="text-xs text-muted-foreground">
            Backend analysis includes market intelligence, scheme matching & loan schedule.
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

      {/* Alternative Opportunities Section */}
      <div className="mt-12">
        <h3 className="font-display text-xl font-extrabold text-foreground">
          Other opportunities for you
        </h3>
        <p className="text-sm text-muted-foreground">
          Additional viable business models tailored to your resources.
        </p>

        <div className="mt-5 grid gap-4 sm:grid-cols-3">
          {ALTERNATIVE_RECOMMENDATIONS.map((alt) => (
            <div
              key={alt.title}
              onClick={() => setActiveRecommendation(alt)}
              className={cn(
                'group cursor-pointer rounded-2xl border p-5 transition-all hover:-translate-y-1 hover:shadow-soft',
                current.title === alt.title
                  ? 'border-primary bg-primary/8 ring-2 ring-primary/30'
                  : 'border-border bg-card hover:border-primary/40',
              )}
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-primary uppercase">
                  {alt.category}
                </span>
                <span className="rounded-full bg-primary/10 border border-primary/30 px-2.5 py-0.5 text-xs font-extrabold text-primary">
                  {alt.matchScore}% match
                </span>
              </div>

              <h4 className="mt-3 font-bold text-base text-foreground leading-snug">
                {alt.title}
              </h4>
              <p className="mt-1 text-xs text-muted-foreground line-clamp-2">
                {alt.description}
              </p>

              <div className="mt-4 flex items-center justify-between text-xs border-t border-border/60 pt-3">
                <div>
                  <span className="text-muted-foreground">Investment: </span>
                  <span className="font-bold text-foreground">
                    {formatCompactINR(alt.investmentAmount)}
                  </span>
                </div>
                <ChevronRight className="size-4 text-primary transition-transform group-hover:translate-x-1" />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
