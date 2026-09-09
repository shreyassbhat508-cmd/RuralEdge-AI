'use client'

import { useState } from 'react'
import Link from 'next/link'
import { MapPin, Navigation, TrendingUp, Users, ShieldAlert, Award, ArrowRight, CheckCircle2, Coins, FileCheck, Lightbulb, Landmark } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { RevenueTrendChart } from '@/components/charts/revenue-trend-chart'
import { CostBreakdownChart } from '@/components/charts/cost-breakdown-chart'
import { BreakEvenChart } from '@/components/charts/break-even-chart'
import { MARKET_MARKERS, MARKET_REACH, OPPORTUNITY_RADAR, SWOT, RISKS, PRICING, OPERATING, buildBreakEven, formatINR, formatCompactINR } from '@/lib/data'
import { useBusiness } from '@/components/business-context'
import { cn } from '@/lib/utils'

const TABS = [
  'Overview',
  'Market Demand',
  'Investment',
  'Operating Costs',
  'Expected Revenue',
  'Risks',
  'Resources Required',
  'Government Schemes',
  'Next Steps',
] as const

export function MarketView() {
  const { profile, activeRecommendation, finance, documents } = useBusiness()
  const [activeTab, setActiveTab] = useState<typeof TABS[number]>('Overview')
  const [activeCategory, setActiveCategory] = useState<string>('all')

  const filteredMarkers = activeCategory === 'all'
    ? MARKET_MARKERS
    : MARKET_MARKERS.filter((m) => m.category === activeCategory)

  const breakEven = buildBreakEven(
    OPERATING.initialInvestment,
    OPERATING.monthlyRevenue,
    OPERATING.monthlyCost,
  )

  const rec = activeRecommendation

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
      {/* Top Banner */}
      <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between border-b border-border/80 pb-6">
        <div>
          <span className="inline-flex items-center gap-1.5 rounded-full border border-primary/30 bg-primary/10 px-3.5 py-1.5 text-xs font-bold text-primary">
            <MapPin className="size-4 text-primary" />
            Detailed Business Plan Profile
          </span>
          <h1 className="mt-3 font-display text-3xl font-extrabold tracking-tight md:text-4xl text-foreground">
            {rec.title}
          </h1>
          <p className="mt-1 text-base text-muted-foreground">
            Complete operational and financial plan for {profile.village}, {profile.district}, {profile.state}.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="rounded-2xl bg-primary/10 border border-primary/30 px-4 py-2 text-right">
            <span className="text-xs font-bold text-muted-foreground uppercase block">Viability Rating</span>
            <span className="text-xl font-black text-primary">{rec.matchScore}% Match</span>
          </div>
        </div>
      </div>

      {/* Navigation Section Tabs */}
      <div className="mt-6 flex items-center gap-2 overflow-x-auto pb-2 border-b border-border">
        {TABS.map((tab) => (
          <button
            key={tab}
            type="button"
            onClick={() => setActiveTab(tab)}
            className={cn(
              'rounded-full px-4 py-2 text-xs font-bold whitespace-nowrap transition-all',
              activeTab === tab
                ? 'bg-primary text-white shadow-soft'
                : 'border border-border bg-card text-muted-foreground hover:bg-muted hover:text-foreground',
            )}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Dynamic Tab Content */}
      <div className="mt-8">
        {/* OVERVIEW TAB */}
        {activeTab === 'Overview' && (
          <div className="space-y-6">
            <div className="grid gap-6 lg:grid-cols-3">
              <Card className="lg:col-span-2 rounded-3xl border-border shadow-soft">
                <CardHeader>
                  <CardTitle className="text-xl font-extrabold">Executive Summary</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4 text-sm text-foreground leading-relaxed">
                  <p>{rec.description}</p>
                  <div className="rounded-2xl border border-primary/20 bg-primary/8 p-4">
                    <span className="font-extrabold text-primary text-xs uppercase block mb-1">
                      Key Highlights & Profitability
                    </span>
                    <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 mt-2 text-xs">
                      {rec.keyHighlights.map((h, i) => (
                        <div key={i} className="rounded-xl border border-border bg-background p-2.5">
                          <span className="text-muted-foreground text-[10px] uppercase block">{h.label}</span>
                          <span className="font-extrabold text-foreground text-sm">{h.value}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="rounded-3xl border-border shadow-soft">
                <CardHeader>
                  <CardTitle className="text-lg font-bold">Why We Recommend This</CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-3 text-xs text-foreground">
                    {rec.whyWeRecommend.map((reason, idx) => (
                      <li key={idx} className="flex items-start gap-2.5">
                        <CheckCircle2 className="size-4 text-success shrink-0 mt-0.5" />
                        <span>{reason}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            </div>
          </div>
        )}

        {/* MARKET DEMAND TAB */}
        {activeTab === 'Market Demand' && (
          <div className="grid gap-6 lg:grid-cols-[1.4fr_1fr]">
            <Card className="rounded-3xl overflow-hidden border-border shadow-soft">
              <CardHeader className="flex flex-row items-center justify-between pb-4">
                <div>
                  <CardTitle className="text-lg">Local Ecosystem Map (5 km Radius)</CardTitle>
                  <p className="text-xs text-muted-foreground">Nearby competitors, suppliers, and customer clusters</p>
                </div>
                <div className="flex gap-1 rounded-full border border-border bg-secondary/50 p-1 text-xs">
                  {['all', 'competitor', 'supplier', 'customer'].map((cat) => (
                    <button
                      key={cat}
                      type="button"
                      onClick={() => setActiveCategory(cat)}
                      className={cn(
                        'rounded-full px-2.5 py-1 capitalize transition-colors',
                        activeCategory === cat ? 'bg-primary text-white font-bold' : 'text-muted-foreground',
                      )}
                    >
                      {cat}
                    </button>
                  ))}
                </div>
              </CardHeader>
              <CardContent>
                <div className="relative h-[360px] w-full overflow-hidden rounded-2xl border border-border bg-card/90">
                  <div className="absolute inset-0 bg-field-lines opacity-20" />
                  <div className="absolute inset-0 bg-contour opacity-30" />

                  <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 flex flex-col items-center gap-1 z-20">
                    <div className="relative size-8 grid place-items-center rounded-full bg-primary text-white font-bold shadow-lift ring-4 ring-primary/20">
                      <Navigation className="size-4 animate-pulse" />
                    </div>
                    <span className="rounded-full bg-card/90 px-2.5 py-0.5 text-[11px] font-extrabold text-foreground border border-border">
                      {profile.village} (You)
                    </span>
                  </div>

                  {filteredMarkers.map((marker) => {
                    const colors: Record<string, string> = {
                      competitor: 'bg-rose-500 text-white ring-rose-500/30',
                      supplier: 'bg-amber-500 text-white ring-amber-500/30',
                      market: 'bg-blue-500 text-white ring-blue-500/30',
                      customer: 'bg-primary text-white ring-primary/30',
                    }
                    return (
                      <div
                        key={marker.id}
                        style={{ left: `${marker.x}%`, top: `${marker.y}%` }}
                        className="absolute -translate-x-1/2 -translate-y-1/2 group z-10 cursor-pointer"
                      >
                        <div className={`size-4 rounded-full ${colors[marker.category]} ring-4 shadow-sm transition-transform group-hover:scale-125`} />
                      </div>
                    )
                  })}
                </div>
              </CardContent>
            </Card>

            <div className="space-y-6">
              <Card className="rounded-3xl border-border shadow-soft">
                <CardHeader>
                  <CardTitle className="text-lg">Target Customer Reach</CardTitle>
                </CardHeader>
                <CardContent className="grid grid-cols-3 gap-3 text-center">
                  <div className="rounded-2xl border border-border bg-background p-3">
                    <div className="font-display text-2xl font-black text-primary">{MARKET_REACH.households.toLocaleString()}</div>
                    <div className="text-[11px] font-medium text-muted-foreground">Households</div>
                  </div>
                  <div className="rounded-2xl border border-border bg-background p-3">
                    <div className="font-display text-2xl font-black text-primary">{MARKET_REACH.localShops}</div>
                    <div className="text-[11px] font-medium text-muted-foreground">Local Shops</div>
                  </div>
                  <div className="rounded-2xl border border-border bg-background p-3">
                    <div className="font-display text-2xl font-black text-primary">{MARKET_REACH.institutionalBuyers}</div>
                    <div className="text-[11px] font-medium text-muted-foreground">Institutions</div>
                  </div>
                </CardContent>
              </Card>

              <Card className="rounded-3xl border-border shadow-soft">
                <CardHeader>
                  <CardTitle className="text-lg">Opportunity Radar</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3 text-xs font-semibold">
                  {OPPORTUNITY_RADAR.map((item) => (
                    <div key={item.category} className="space-y-1">
                      <div className="flex justify-between">
                        <span>{item.category}</span>
                        <span className="text-primary">{item.level} ({item.score}%)</span>
                      </div>
                      <div className="h-2 w-full rounded-full bg-muted overflow-hidden">
                        <div className="h-full bg-primary rounded-full" style={{ width: `${item.score}%` }} />
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </div>
          </div>
        )}

        {/* INVESTMENT TAB */}
        {activeTab === 'Investment' && (
          <div className="grid gap-6 lg:grid-cols-2">
            <Card className="rounded-3xl border-border shadow-soft">
              <CardHeader>
                <CardTitle className="text-xl font-bold">Initial Investment Breakdown</CardTitle>
                <p className="text-xs text-muted-foreground">Estimated setup and asset creation capital</p>
              </CardHeader>
              <CardContent>
                <CostBreakdownChart />
              </CardContent>
            </Card>

            <Card className="rounded-3xl border-border shadow-soft">
              <CardHeader>
                <CardTitle className="text-xl font-bold">Financing & Subsidy Structure</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="rounded-2xl border border-primary/30 bg-primary/10 p-5">
                  <span className="text-xs font-bold uppercase text-primary block">Project Capital Allocation</span>
                  <div className="mt-3 grid grid-cols-2 gap-3 text-xs">
                    <div>
                      <span className="text-muted-foreground">Total Project Cost</span>
                      <p className="text-xl font-black text-foreground">{formatINR(finance.projectCost || rec.investmentAmount)}</p>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Your Contribution</span>
                      <p className="text-xl font-black text-primary">{formatINR(finance.margin)}</p>
                    </div>
                  </div>
                </div>
                <Link
                  href="/finance"
                  className="inline-flex items-center gap-2 text-xs font-extrabold text-primary hover:underline"
                >
                  Configure Loan & Repayment Calculator →
                </Link>
              </CardContent>
            </Card>
          </div>
        )}

        {/* OPERATING COSTS TAB */}
        {activeTab === 'Operating Costs' && (
          <div className="grid gap-6 lg:grid-cols-2">
            <Card className="rounded-3xl border-border shadow-soft">
              <CardHeader>
                <CardTitle className="text-xl font-bold">Monthly Expenditure Breakdown</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <CostRow label="Feed & Input Supplies" amount="₹34,000" pct="48%" />
                <CostRow label="Labour & Maintenance" amount="₹15,000" pct="21%" />
                <CostRow label="Transport & Fuel" amount="₹9,500" pct="13%" />
                <CostRow label="Utilities & Power" amount="₹6,000" pct="9%" />
                <CostRow label="Equipment Upkeep" amount="₹6,000" pct="9%" />
              </CardContent>
            </Card>

            <Card className="rounded-3xl border-border shadow-soft">
              <CardHeader>
                <CardTitle className="text-xl font-bold">Cost Optimization Strategy</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 text-xs text-foreground">
                <div className="rounded-2xl border border-border bg-background p-4">
                  <span className="font-bold text-primary block mb-1">Batch Buying Feed</span>
                  <p className="text-muted-foreground">Purchasing cattle feed in monthly bulk lots saves up to 8% on total feed costs.</p>
                </div>
                <div className="rounded-2xl border border-border bg-background p-4">
                  <span className="font-bold text-primary block mb-1">Shared Local Logistics</span>
                  <p className="text-muted-foreground">Grouping transport runs with neighboring milk producers reduces daily trip expenses.</p>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* EXPECTED REVENUE TAB */}
        {activeTab === 'Expected Revenue' && (
          <div className="grid gap-6 lg:grid-cols-2">
            <Card className="rounded-3xl border-border shadow-soft">
              <CardHeader>
                <CardTitle className="text-xl font-bold">Monthly Revenue Trend</CardTitle>
              </CardHeader>
              <CardContent>
                <RevenueTrendChart />
              </CardContent>
            </Card>

            <Card className="rounded-3xl border-border shadow-soft">
              <CardHeader>
                <CardTitle className="text-xl font-bold">Break-even Projection</CardTitle>
              </CardHeader>
              <CardContent>
                <BreakEvenChart data={breakEven} breakEvenMonth={OPERATING.breakEvenMonths} />
              </CardContent>
            </Card>
          </div>
        )}

        {/* RISKS TAB */}
        {activeTab === 'Risks' && (
          <Card className="rounded-3xl border-border shadow-soft">
            <CardHeader>
              <CardTitle className="text-xl font-bold">Risk Assessment & Action Plan</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {RISKS.map((r) => (
                <div key={r.id} className="rounded-2xl border border-border bg-background p-4 text-xs">
                  <div className="flex items-center justify-between font-bold mb-1">
                    <span className="text-foreground text-sm">{r.title}</span>
                    <span className="rounded-full bg-amber-500/10 text-amber-600 px-2.5 py-0.5">{r.level} Risk</span>
                  </div>
                  <p className="text-muted-foreground mb-2"><strong>Cause: </strong>{r.why}</p>
                  <p className="text-primary font-bold"><strong>Action Step: </strong>{r.action}</p>
                </div>
              ))}
            </CardContent>
          </Card>
        )}

        {/* RESOURCES REQUIRED TAB */}
        {activeTab === 'Resources Required' && (
          <Card className="rounded-3xl border-border shadow-soft">
            <CardHeader>
              <CardTitle className="text-xl font-bold">Required Infrastructure & Equipment</CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-2 gap-4 sm:grid-cols-3 text-xs">
              <ResourceBox title="Land Plot" detail="Minimum 0.5 acre for shed & fodder" />
              <ResourceBox title="Cattle Shed" detail="Ventilated shelter for 6-10 cows" />
              <ResourceBox title="Water Source" detail="Borewell or continuous water connection" />
              <ResourceBox title="Milking Machines" detail="Automated 2-bucket vacuum pump" />
              <ResourceBox title="Milk Chiller" detail="200L stainless steel cooling unit" />
              <ResourceBox title="Transport Vehicle" detail="Two-wheeler or auto with insulated cans" />
            </CardContent>
          </Card>
        )}

        {/* GOVERNMENT SCHEMES TAB */}
        {activeTab === 'Government Schemes' && (
          <div className="space-y-4">
            <Card className="rounded-3xl border-primary/30 bg-primary/8 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <span className="text-xs font-bold text-primary uppercase">Top Scheme Match</span>
                  <h3 className="text-2xl font-extrabold text-foreground">PMEGP Subsidy & Term Loan</h3>
                </div>
                <Link
                  href="/schemes"
                  className="rounded-full bg-primary px-6 py-2.5 text-xs font-bold text-white shadow-soft"
                >
                  Explore All Schemes →
                </Link>
              </div>
            </Card>
          </div>
        )}

        {/* NEXT STEPS TAB */}
        {activeTab === 'Next Steps' && (
          <Card className="rounded-3xl border-border shadow-soft">
            <CardHeader>
              <CardTitle className="text-xl font-bold">Action Roadmap</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center gap-3 rounded-2xl border border-border p-4">
                <span className="grid size-8 place-items-center rounded-full bg-primary text-white font-bold text-xs">1</span>
                <div>
                  <h5 className="font-bold text-sm">Complete Document Checklist</h5>
                  <p className="text-xs text-muted-foreground">Gather bank statement & land lease agreement.</p>
                </div>
              </div>
              <div className="flex items-center gap-3 rounded-2xl border border-border p-4">
                <span className="grid size-8 place-items-center rounded-full bg-primary text-white font-bold text-xs">2</span>
                <div>
                  <h5 className="font-bold text-sm">Submit PMEGP Application</h5>
                  <p className="text-xs text-muted-foreground">Apply online at KVIC portal or visit local DIC office.</p>
                </div>
              </div>
              <div className="flex items-center gap-3 rounded-2xl border border-border p-4">
                <span className="grid size-8 place-items-center rounded-full bg-primary text-white font-bold text-xs">3</span>
                <div>
                  <h5 className="font-bold text-sm">Procure Equipment & Livestock</h5>
                  <p className="text-xs text-muted-foreground">Setup cattle shed and procure initial batch of cows.</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}

function CostRow({ label, amount, pct }: { label: string; amount: string; pct: string }) {
  return (
    <div className="flex items-center justify-between rounded-xl border border-border bg-background p-3 text-xs font-semibold">
      <span className="text-foreground">{label}</span>
      <div className="flex items-center gap-3">
        <span className="text-primary font-bold">{amount}</span>
        <span className="text-muted-foreground text-[11px]">{pct}</span>
      </div>
    </div>
  )
}

function ResourceBox({ title, detail }: { title: string; detail: string }) {
  return (
    <div className="rounded-2xl border border-border bg-card p-4">
      <h5 className="font-extrabold text-foreground text-sm">{title}</h5>
      <p className="mt-1 text-xs text-muted-foreground">{detail}</p>
    </div>
  )
}

