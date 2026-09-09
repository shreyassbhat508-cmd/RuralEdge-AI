import Link from 'next/link'
import {
  MapPinned,
  Calculator,
  Landmark,
  MessageCircle,
  Languages,
  LayoutDashboard,
  ArrowUpRight,
  Wallet,
  Trees,
  BadgePercent,
  Sparkles,
} from 'lucide-react'
import { Reveal } from '@/components/reveal'
import { Business3DBadge } from '@/components/three/business-3d-badge'
import { cn } from '@/lib/utils'

const SITUATIONS = [
  {
    icon: Wallet,
    title: '₹2L starting budget',
    action: 'Find suitable businesses',
    badge: 'Capital Fit',
    color: 'bg-primary/10 text-primary border-primary/20 dark:text-primary',
    href: '/assessment',
  },
  {
    icon: Trees,
    title: 'Limited land',
    action: 'Explore low-land opportunities',
    badge: 'Space Efficient',
    color: 'bg-muted/15 text-muted border-muted/30 dark:text-muted',
    href: '/assessment',
  },
  {
    icon: BadgePercent,
    title: 'Need financing',
    action: 'Find matching schemes',
    badge: 'Up to 90% Loan',
    color: 'bg-charcoal/10 text-charcoal border-charcoal/20 dark:text-foreground',
    href: '/schemes',
  },
  {
    icon: Sparkles,
    title: 'Not sure what to start',
    action: 'Let AI recommend →',
    badge: 'Smart AI Match',
    color: 'bg-primary text-white border-primary',
    href: '/assessment',
    highlight: true,
  },
]

const FEATURES = [
  {
    href: '/market',
    icon: MapPinned,
    title: 'Local Market Intelligence',
    body: 'See competitors, suppliers, customers and demand within your 5 km radius — mapped clearly, with an opportunity score and SWOT.',
    className: 'md:col-span-2 md:row-span-2',
    tone: 'bg-charcoal text-white',
    big: true,
    badgeType: 'dairy' as const,
  },
  {
    href: '/finance',
    icon: Calculator,
    title: 'Financial Planning',
    body: 'Know your project cost, safe loan amount and monthly EMI — with a plain-language repayment plan.',
    className: '',
    tone: 'bg-card',
    badgeType: 'retail' as const,
  },
  {
    href: '/schemes',
    icon: Landmark,
    title: 'Government Support',
    body: 'Discover the schemes and subsidies you actually qualify for.',
    className: '',
    tone: 'bg-card',
    badgeType: 'farming' as const,
  },
  {
    href: '/advisor',
    icon: MessageCircle,
    title: 'AI Business Advisor',
    body: 'Ask anything — “Can I afford this loan?” — and get honest, practical answers.',
    className: 'md:col-span-2',
    tone: 'bg-primary text-white',
    badgeType: 'textiles' as const,
  },
  {
    href: '/dashboard',
    icon: LayoutDashboard,
    title: 'Business Health Dashboard',
    body: 'One clear score for how your business is doing, updated as things change.',
    className: '',
    tone: 'bg-card',
    badgeType: 'food' as const,
  },
  {
    href: '/#languages',
    icon: Languages,
    title: '7 Indian Languages',
    body: 'Use RuralEdge comfortably in the language you think in.',
    className: '',
    tone: 'bg-sand/30',
    badgeType: 'handicrafts' as const,
  },
]

export function Features() {
  return (
    <section id="features" className="relative border-y border-border bg-secondary/30 bg-field-lines py-20">
      <div className="crop-divider absolute top-0 left-0 right-0" />

      <div className="mx-auto max-w-7xl px-4 sm:px-6">
        {/* Built For Your Situation Section */}
        <Reveal className="mx-auto max-w-2xl text-center">
          <p className="text-xs font-semibold tracking-[0.16em] text-primary uppercase">
            Tailored Advisory
          </p>
          <h2 className="mt-3 font-display text-3xl font-extrabold tracking-tight text-foreground text-balance md:text-4xl">
            Built for your specific situation
          </h2>
          <p className="mt-3 text-base text-muted-foreground">
            No matter your starting budget, available land, or financing needs — RuralEdge adapts to you.
          </p>
        </Reveal>

        <div className="mt-10 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {SITUATIONS.map((sit, i) => {
            const Icon = sit.icon
            return (
              <Reveal key={sit.title} delay={i * 0.08}>
                <Link
                  href={sit.href}
                  className={cn(
                    'group relative flex flex-col justify-between rounded-2xl border p-6 shadow-soft transition-all duration-300 hover:-translate-y-1 hover:shadow-lift',
                    sit.highlight
                      ? 'bg-primary text-white border-primary'
                      : 'bg-card text-card-foreground border-border hover:border-primary/40',
                  )}
                >
                  <div>
                    <div className="flex items-center justify-between">
                      <span
                        className={cn(
                          'grid size-10 place-items-center rounded-xl border',
                          sit.highlight
                            ? 'bg-white/15 text-white border-white/20'
                            : sit.color,
                        )}
                      >
                        <Icon className="size-5" />
                      </span>
                      <span
                        className={cn(
                          'rounded-full px-2.5 py-1 text-[11px] font-bold tracking-wide uppercase',
                          sit.highlight
                            ? 'bg-white/20 text-white'
                            : 'bg-muted text-muted-foreground',
                        )}
                      >
                        {sit.badge}
                      </span>
                    </div>

                    <h3 className="mt-4 font-display text-lg font-bold">
                      {sit.title}
                    </h3>
                  </div>

                  <div className="mt-6 flex items-center gap-1 text-sm font-semibold text-primary group-hover:underline">
                    <span>{sit.action}</span>
                    <ArrowUpRight className="size-4 transition-transform group-hover:translate-x-0.5" />
                  </div>
                </Link>
              </Reveal>
            )
          })}
        </div>

        {/* Platform Capabilities Grid */}
        <div className="mt-24">
          <Reveal className="mx-auto max-w-2xl text-center">
            <p className="text-xs font-semibold tracking-[0.16em] text-primary uppercase">
              One platform, six tools
            </p>
            <h2 className="mt-3 font-display text-3xl font-extrabold tracking-tight text-foreground text-balance md:text-4xl">
              Everything a rural entrepreneur needs to decide with confidence
            </h2>
          </Reveal>

          <div className="mt-12 grid auto-rows-[minmax(190px,auto)] gap-5 md:grid-cols-4">
            {FEATURES.map((f, i) => {
              const Icon = f.icon
              const dark = f.tone.includes('text-white') || f.tone.includes('text-primary-foreground')
              return (
                <Reveal key={f.title} delay={i * 0.06} className={cn(f.className)}>
                  <Link
                    href={f.href}
                    className={cn(
                      'group flex h-full flex-col justify-between rounded-2xl border border-border/80 p-6 shadow-soft transition-all duration-300 hover:-translate-y-1 hover:shadow-lift',
                      f.tone,
                    )}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3">
                        <span
                          className={cn(
                            'grid size-11 place-items-center rounded-xl',
                            dark ? 'bg-white/15' : 'bg-primary/10 text-primary',
                          )}
                        >
                          <Icon className="size-5.5" />
                        </span>
                        <Business3DBadge type={f.badgeType} size="sm" />
                      </div>
                      <ArrowUpRight
                        className={cn(
                          'size-5 transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5',
                          dark ? 'text-white' : 'text-primary',
                        )}
                      />
                    </div>

                    <div>
                      <h3
                        className={cn(
                          'mt-5 font-display font-bold tracking-tight',
                          f.big ? 'text-2xl' : 'text-lg',
                        )}
                      >
                        {f.title}
                      </h3>
                      <p
                        className={cn(
                          'mt-2 text-sm leading-relaxed',
                          dark ? 'text-white/85' : 'text-muted-foreground',
                        )}
                      >
                        {f.body}
                      </p>
                    </div>
                  </Link>
                </Reveal>
              )
            })}
          </div>
        </div>
      </div>
    </section>
  )
}

