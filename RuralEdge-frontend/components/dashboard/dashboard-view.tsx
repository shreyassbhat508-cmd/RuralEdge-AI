'use client'

import Link from 'next/link'
import {
  ArrowUpRight,
  Calculator,
  Landmark,
  MapPinned,
  MessageCircle,
  Pencil,
  Clock,
  FileCheck,
  CheckCircle2,
  Sparkles,
} from 'lucide-react'
import { useBusiness } from '@/components/business-context'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  JOURNEY_STEPS,
  formatCompactINR,
} from '@/lib/data'
import { cn } from '@/lib/utils'

const QUICK_ACTIONS = [
  { href: '/market', icon: MapPinned, label: 'Market Intelligence', tone: 'text-primary bg-primary/10' },
  { href: '/finance', icon: Calculator, label: 'Financial Plan', tone: 'text-primary bg-primary/10' },
  { href: '/schemes', icon: Landmark, label: 'Government Support', tone: 'text-charcoal bg-sand/40 dark:text-foreground' },
  { href: '/advisor', icon: MessageCircle, label: 'Ask RuralEdge AI', tone: 'text-muted bg-muted/15' },
]

export function DashboardView() {
  const { profile, finance, documents, toggleDocument, activeRecommendation, onboarding, businessAnalysis } = useBusiness()

  const rec = activeRecommendation

  // Real backend metrics when available
  const matchScore = businessAnalysis?.opportunity?.score ?? rec.matchScore
  const projectCost = businessAnalysis?.finance?.project_cost ?? finance.projectCost ?? rec.investmentAmount
  const ownContribution = businessAnalysis?.finance?.own_contribution ?? finance.margin
  const loanAmount = businessAnalysis?.finance?.loan_amount ?? finance.loan ?? rec.fundingAmount

  const demandScore = businessAnalysis?.opportunity?.components?.market ?? 92
  const locationScore = businessAnalysis?.opportunity?.components?.location ?? 91
  const financialScore = businessAnalysis?.opportunity?.components?.financial ?? 88
  const competitionScore = businessAnalysis?.opportunity?.components?.competition ?? 71

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
            <span className="text-2xl font-black text-primary">{matchScore}%</span>
            <span className="text-xs font-bold text-primary uppercase">Feasibility Score</span>
          </div>
        </div>

        {/* Financial Summary */}
        <div className="mt-6 grid grid-cols-2 gap-4 lg:grid-cols-3">
          <div className="rounded-2xl border border-border/80 bg-background p-4">
            <p className="text-xs font-bold uppercase text-muted-foreground">Project Cost</p>
            <p className="mt-1.5 text-2xl font-black text-foreground">
              {formatCompactINR(projectCost)}
            </p>
          </div>

          <div className="rounded-2xl border border-border/80 bg-background p-4">
            <p className="text-xs font-bold uppercase text-muted-foreground">Your Contribution</p>
            <p className="mt-1.5 text-2xl font-black text-primary">
              {formatCompactINR(ownContribution)}
            </p>
          </div>

          <div className="col-span-2 lg:col-span-1 rounded-2xl border border-primary/30 bg-primary/10 p-4">
            <p className="text-xs font-bold uppercase text-primary">Potential Financing</p>
            <p className="mt-1.5 text-2xl font-black text-primary">
              {formatCompactINR(loanAmount)}
            </p>
          </div>
        </div>
      </div>

      {/* Business Health Radar Metrics */}
      <div className="mt-8">
        <h3 className="font-display text-xl font-extrabold text-foreground">
          Business Feasibility Scorecard
        </h3>
        <p className="text-xs text-muted-foreground">
          Real-time viability indicators computed by the RuralEdge backend engine.
        </p>

        <div className="mt-4 grid grid-cols-2 gap-4 lg:grid-cols-4">
          <HealthMetric title="DEMAND" value={demandScore} label="Market Demand" color="bg-primary" />
          <HealthMetric title="LOCATION" value={locationScore} label="Location Readiness" color="bg-charcoal" />
          <HealthMetric title="FINANCIAL" value={financialScore} label="Financial Viability" color="bg-primary" />
          <HealthMetric title="COMPETITION" value={competitionScore} label="Competition Score" color="bg-muted" />
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
