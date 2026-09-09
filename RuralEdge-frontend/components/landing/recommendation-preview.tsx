'use client'

import Link from 'next/link'
import { Sparkles, TrendingUp, BadgeIndianRupee, ShieldCheck, Building2 } from 'lucide-react'
import { Reveal } from '@/components/reveal'

export function RecommendationPreview() {
  return (
    <section className="mx-auto max-w-7xl px-4 py-16 sm:px-6">
      <Reveal className="mx-auto max-w-2xl text-center">
        <p className="text-xs font-semibold tracking-[0.16em] text-primary uppercase">
          AI Recommendation Preview
        </p>
        <h2 className="mt-3 font-display text-3xl font-extrabold tracking-tight text-foreground sm:text-4xl">
          See what an AI recommendation looks like
        </h2>
        <p className="mt-3 text-base text-muted-foreground">
          Real market viability score, exact financing breakdown, and government subsidy match.
        </p>
      </Reveal>

      <Reveal delay={0.15} className="mt-10">
        <div className="mx-auto max-w-4xl overflow-hidden rounded-3xl border border-primary/30 bg-card p-6 sm:p-8 shadow-lift relative">
          <div className="absolute top-0 right-0 h-40 w-40 bg-radial from-primary/15 to-transparent blur-2xl pointer-events-none" />

          {/* Top header pill & match score */}
          <div className="flex flex-wrap items-center justify-between gap-4 border-b border-border/80 pb-6">
            <div className="flex items-center gap-3">
              <span className="grid size-12 place-items-center rounded-2xl bg-charcoal text-2xl shadow-soft">
                🐄
              </span>
              <div>
                <span className="inline-flex items-center gap-1.5 text-xs font-bold text-primary uppercase tracking-wider">
                  Top Matched Business
                </span>
                <h3 className="text-2xl font-extrabold text-foreground">
                  Dairy Farming & Milk Enterprise
                </h3>
              </div>
            </div>

            <div className="flex items-center gap-2 rounded-2xl bg-primary/10 border border-primary/30 px-4 py-2">
              <Sparkles className="size-5 text-primary animate-pulse" />
              <span className="text-xl font-black text-primary">87% Business Match</span>
            </div>
          </div>

          {/* 4 Metric cards */}
          <div className="mt-6 grid grid-cols-2 gap-4 lg:grid-cols-4">
            <div className="rounded-2xl border border-border/70 bg-background/80 p-4">
              <div className="flex items-center justify-between text-xs font-bold text-muted-foreground uppercase tracking-wider">
                <span>Demand</span>
                <TrendingUp className="size-4 text-primary" />
              </div>
              <div className="mt-2 text-2xl font-black text-foreground">92%</div>
              <p className="text-xs text-muted-foreground mt-1">High local demand</p>
            </div>

            <div className="rounded-2xl border border-border/70 bg-background/80 p-4">
              <div className="flex items-center justify-between text-xs font-bold text-muted-foreground uppercase tracking-wider">
                <span>Investment</span>
                <BadgeIndianRupee className="size-4 text-sand" />
              </div>
              <div className="mt-2 text-2xl font-black text-foreground">₹8.5L</div>
              <p className="text-xs text-muted-foreground mt-1">Estimated starting cost</p>
            </div>

            <div className="rounded-2xl border border-border/70 bg-background/80 p-4">
              <div className="flex items-center justify-between text-xs font-bold text-muted-foreground uppercase tracking-wider">
                <span>Funding</span>
                <ShieldCheck className="size-4 text-primary" />
              </div>
              <div className="mt-2 text-2xl font-black text-primary">₹7.65L</div>
              <p className="text-xs text-muted-foreground mt-1">Potential financing</p>
            </div>

            <div className="rounded-2xl border border-border/70 bg-background/80 p-4">
              <div className="flex items-center justify-between text-xs font-bold text-muted-foreground uppercase tracking-wider">
                <span>Competition</span>
                <Building2 className="size-4 text-muted" />
              </div>
              <div className="mt-2 text-2xl font-black text-foreground">Moderate</div>
              <p className="text-xs text-muted-foreground mt-1">3 suppliers in 5km</p>
            </div>
          </div>

          {/* Footer CTA */}
          <div className="mt-8 flex flex-col sm:flex-row items-center justify-between gap-4 rounded-2xl bg-primary/10 border border-primary/20 p-4">
            <p className="text-sm font-semibold text-foreground text-center sm:text-left">
              Want to see recommendations for your own village & starting capital?
            </p>
            <Link
              href="/assessment"
              className="inline-flex items-center gap-2 rounded-full bg-primary px-5 py-2.5 text-sm font-bold text-white shadow-soft transition-transform hover:scale-105 hover:bg-primary-hover shrink-0"
            >
              Analyze Your Opportunity →
            </Link>
          </div>
        </div>
      </Reveal>
    </section>
  )
}
