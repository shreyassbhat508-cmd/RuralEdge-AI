'use client'

import { useState } from 'react'
import { Landmark, Sparkles, CheckCircle2, ChevronRight, X, ExternalLink, HelpCircle, FileText } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useBusiness } from '@/components/business-context'
import { DETAILED_SCHEMES, formatCompactINR, formatINR, type DetailedScheme } from '@/lib/data'
import { cn } from '@/lib/utils'

export function SchemesView() {
  const { onboarding, profile } = useBusiness()
  const [selectedScheme, setSelectedScheme] = useState<DetailedScheme | null>(null)

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
            Based on your profile in {onboarding.village || 'Hosahalli'}, {onboarding.district || 'Ramanagara'}, we found schemes that may fit your business.
          </p>
        </div>

        <div className="inline-flex items-center gap-2 rounded-2xl bg-charcoal px-4 py-2 text-sm font-extrabold text-white shadow-soft shrink-0">
          <Sparkles className="size-4 text-sand" />
          <span>{DETAILED_SCHEMES.length} schemes found</span>
        </div>
      </div>

      {/* Scheme Cards Grid */}
      <div className="mt-8 grid gap-6 md:grid-cols-2">
        {DETAILED_SCHEMES.map((scheme) => (
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
                <span className="rounded-full bg-sand/40 px-3 py-1 text-xs font-bold text-charcoal dark:text-sand">
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
                  <p className="font-extrabold text-sm text-charcoal dark:text-sand">
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
                No collateral up to ₹10 Lakhs
              </span>
              <button
                type="button"
                onClick={() => setSelectedScheme(scheme)}
                className="inline-flex items-center gap-1.5 rounded-full bg-primary px-4 py-2 text-xs font-bold text-white shadow-soft transition-transform hover:scale-105 hover:bg-primary-hover"
              >
                View Scheme →
              </button>
            </div>
          </div>
        ))}
      </div>

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
                <h4 className="text-xs font-bold uppercase tracking-wider text-charcoal dark:text-sand mb-2">
                  Key Scheme Benefits
                </h4>
                <ul className="space-y-2 text-xs text-foreground">
                  {selectedScheme.keyBenefits.map((b, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <CheckCircle2 className="size-4 text-success shrink-0 mt-0.5" />
                      <span>{b}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="rounded-2xl border border-border bg-background p-4">
                <h4 className="text-xs font-bold uppercase tracking-wider text-charcoal dark:text-sand mb-2">
                  Required Application Documents
                </h4>
                <ul className="space-y-2 text-xs text-foreground">
                  {selectedScheme.requiredDocs.map((doc, idx) => (
                    <li key={idx} className="flex items-center gap-2">
                      <FileText className="size-4 text-primary shrink-0" />
                      <span>{doc}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="rounded-2xl bg-primary/10 border border-primary/30 p-4 text-xs">
                <span className="font-bold text-primary block mb-1">AI Recommendation Note</span>
                <p className="text-muted-foreground">
                  You can submit your application directly at your nearest district DIC or via national portal using your RuralEdge viability report.
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
                href="https://www.jansamarth.in"
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1.5 rounded-full bg-primary px-6 py-2.5 text-xs font-bold text-white shadow-soft hover:scale-105 hover:bg-primary-hover"
              >
                Apply via JanSamarth <ExternalLink className="size-3.5" />
              </a>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

