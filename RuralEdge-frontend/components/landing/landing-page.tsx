'use client'

import Link from 'next/link'
import { motion } from 'framer-motion'
import {
  Sparkles,
  Search,
  Calculator,
  LineChart,
  ShieldCheck,
  Bot,
  ArrowRight,
} from 'lucide-react'

export function LandingPage() {
  return (
    <div className="flex flex-col">
      {/* HERO SECTION */}
      <section className="relative w-full min-h-[90vh] flex flex-col justify-center overflow-hidden bg-transparent pt-16">
        {/* Dark/Transparent Overlay for text readability */}
        <div className="absolute inset-0 z-0 bg-gradient-to-r from-charcoal/90 via-charcoal/60 to-transparent" />
        <div className="absolute inset-0 z-0 bg-charcoal/20" />

        <div className="relative z-10 w-full mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8 flex-1 flex flex-col justify-center">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
            <div className="lg:col-span-8 xl:col-span-7 flex flex-col justify-center">
              <div>
                <span className="inline-flex items-center gap-2 rounded-full border border-primary/40 bg-charcoal/40 px-4 py-1.5 text-xs font-semibold text-background dark:text-[#D5DCE5] shadow-sm backdrop-blur-md">
                  <Sparkles className="size-3.5 text-primary animate-pulse" />
                  SMART ADVISORY FOR RURAL INDIA
                </span>
              </div>

              <h1 className="mt-6 font-display text-5xl font-extrabold leading-[1.1] tracking-tight text-white dark:text-[#F5F7F5] text-balance sm:text-6xl lg:text-7xl">
                Build Smarter.{' '}
                <span className="text-primary">
                  Grow Stronger.
                </span>
              </h1>

              <p className="mt-6 max-w-xl text-lg leading-relaxed text-background/80 dark:text-[#B8C0CC] text-pretty font-medium">
                RuralEdge helps farmers and rural entrepreneurs discover the right government schemes, understand financing options, and plan sustainable businesses.
              </p>

              <div className="mt-10 flex flex-wrap items-center gap-4">
                <Link
                  href="/advisor"
                  className="group inline-flex items-center gap-2 rounded-full bg-primary px-7 py-4 text-base font-bold text-white shadow-lift transition-all hover:-translate-y-0.5 hover:bg-primary-hover hover:shadow-lg"
                >
                  <Bot className="size-5" />
                  Ask RuralEdge
                </Link>
                <Link
                  href="/schemes"
                  className="inline-flex items-center gap-2 rounded-full border border-background/30 bg-charcoal/40 px-7 py-4 text-base font-bold text-white backdrop-blur-md transition-all hover:bg-charcoal/60 hover:border-background/50"
                >
                  Explore Schemes
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* LOWER SECTIONS WITH TRANSLUCENT OVERLAY */}
      <div className="relative z-20 w-full">
        {/* Theme-aware smooth gradient overlay */}
        <div className="absolute inset-0 pointer-events-none bg-gradient-to-b from-transparent via-[#F7F6F0]/85 to-[#F7F6F0]/95 dark:from-transparent dark:via-[#111613]/85 dark:to-[#111613]/95 via-[8%]" />
        
        {/* FEATURES SECTION */}
        <section className="relative z-10 w-full py-24">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="font-display text-3xl font-extrabold text-foreground sm:text-4xl">
              Everything you need to grow
            </h2>
            <p className="mt-4 text-lg text-muted-foreground">
              We simplify the process of starting and scaling your rural business.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              {
                title: 'Discover Government Schemes',
                desc: 'Find schemes and subsidies relevant to your business or farming activity.',
                icon: Search,
              },
              {
                title: 'Understand Financing',
                desc: 'Estimate loans, contributions, EMI and repayment requirements.',
                icon: Calculator,
              },
              {
                title: 'Plan Your Business',
                desc: 'Get practical guidance for starting and growing a rural business.',
                icon: LineChart,
              },
              {
                title: 'Check Eligibility',
                desc: 'Understand whether you may qualify for different financial support options.',
                icon: ShieldCheck,
              },
            ].map((feature, i) => (
              <div
                key={i}
                className="group flex flex-col gap-4 rounded-3xl border border-border bg-card p-6 shadow-soft transition-all hover:-translate-y-1 hover:border-primary/40 hover:shadow-lift"
              >
                <div className="flex size-12 items-center justify-center rounded-2xl bg-primary/10 text-primary transition-colors group-hover:bg-primary group-hover:text-white">
                  <feature.icon className="size-6" />
                </div>
                <div>
                  <h3 className="font-display text-xl font-bold text-foreground">{feature.title}</h3>
                  <p className="mt-2 text-sm font-medium text-muted-foreground leading-relaxed">{feature.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* HOW IT WORKS SECTION */}
      <section className="relative z-10 w-full py-24 border-y border-border/20">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="font-display text-3xl font-extrabold text-foreground sm:text-4xl">
              How RuralEdge Helps
            </h2>
            <p className="mt-4 text-lg text-muted-foreground">
              Your journey from idea to execution, simplified.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 relative">
            {/* Connecting Line (Desktop) */}
            <div className="hidden md:block absolute top-12 left-16 right-16 h-[2px] bg-border z-0" />

            {[
              {
                step: '01',
                title: 'Tell us about your idea',
                desc: 'Share what you want to build or grow through our smart chatbot.',
              },
              {
                step: '02',
                title: 'Get relevant schemes and financial guidance',
                desc: 'We match you with the right government subsidies and calculate exact requirements.',
              },
              {
                step: '03',
                title: 'Build your repayment/business plan',
                desc: 'Understand your EMIs and get a structured roadmap for your business.',
              },
            ].map((step, i) => (
              <div key={i} className="relative z-10 flex flex-col items-center text-center">
                <div className="flex size-24 items-center justify-center rounded-full border-8 border-background bg-primary text-white font-display text-2xl font-black shadow-soft mb-6">
                  {step.step}
                </div>
                <h3 className="font-display text-xl font-bold text-foreground mb-3">{step.title}</h3>
                <p className="text-muted-foreground font-medium">{step.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* BOTTOM CTA SECTION */}
      <section className="relative z-10 w-full py-24">
        <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="font-display text-4xl font-extrabold text-foreground sm:text-5xl mb-6">
            Have a business idea?
          </h2>
          <p className="text-xl text-muted-foreground mb-10">
            Let RuralEdge help you understand the numbers.
          </p>
          <Link
            href="/advisor"
            className="inline-flex items-center gap-2 rounded-full bg-primary px-8 py-4 text-lg font-bold text-white shadow-lift transition-all hover:-translate-y-1 hover:bg-primary-hover hover:shadow-xl"
          >
            <Bot className="size-6" />
            Ask RuralEdge
          </Link>
        </div>
      </section>
      </div>
    </div>
  )
}
