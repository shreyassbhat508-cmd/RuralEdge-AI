import { MapPin, Coins, Cpu, CheckCircle2 } from 'lucide-react'
import { Reveal } from '@/components/reveal'

const STEPS = [
  {
    step: '01',
    icon: MapPin,
    title: 'Tell us about your location',
    body: 'Select your state, district, and village locality. We use local micro-market signals to understand demand.',
  },
  {
    step: '02',
    icon: Coins,
    title: 'Tell us about your resources',
    body: 'Specify your available starting budget, land, water access, livestock, equipment, or shop space.',
  },
  {
    step: '03',
    icon: Cpu,
    title: 'AI analyzes opportunities',
    body: 'RuralEdge evaluates regional market demand, competition density, cost viability, and matching credit schemes.',
  },
  {
    step: '04',
    icon: CheckCircle2,
    title: 'Get your business + funding plan',
    body: 'Receive your personalized viability rating, exact investment breakdown, subsidy match, and action roadmap.',
  },
]

export function HowItWorks() {
  return (
    <section id="how" className="mx-auto max-w-7xl px-4 py-20 sm:px-6">
      <Reveal className="mx-auto max-w-2xl text-center">
        <p className="text-xs font-semibold tracking-[0.16em] text-primary uppercase">
          How it works
        </p>
        <h2 className="mt-3 font-display text-3xl font-extrabold tracking-tight text-balance md:text-4xl">
          Four simple steps to your dream enterprise
        </h2>
        <p className="mt-4 text-lg text-muted-foreground text-pretty">
          From local inputs to bank-ready financial clarity in under 3 minutes.
        </p>
      </Reveal>

      <div className="mt-14 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {STEPS.map((s, i) => {
          const Icon = s.icon
          return (
            <Reveal key={s.title} delay={i * 0.1}>
              <div className="relative h-full rounded-2xl border border-border bg-card p-6 shadow-soft transition-transform hover:-translate-y-1 hover:border-primary/40">
                <span className="absolute right-5 top-5 font-display text-4xl font-extrabold text-primary/15">
                  {s.step}
                </span>
                <span className="grid size-12 place-items-center rounded-xl bg-primary/10 text-primary">
                  <Icon className="size-6" />
                </span>
                <h3 className="mt-5 text-lg font-bold text-foreground">{s.title}</h3>
                <p className="mt-2.5 text-xs leading-relaxed text-muted-foreground">
                  {s.body}
                </p>
              </div>
            </Reveal>
          )
        })}
      </div>
    </section>
  )
}

