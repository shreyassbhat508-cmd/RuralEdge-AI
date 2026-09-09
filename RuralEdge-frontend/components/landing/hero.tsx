'use client'

import Link from 'next/link'
import { motion } from 'framer-motion'
import {
  Sparkles,
  TrendingUp,
  Building2,
  BadgeIndianRupee,
  ShieldCheck,
  Landmark,
  Calculator,
  Bot
} from 'lucide-react'

const container = {
  hidden: {},
  show: { transition: { staggerChildren: 0.09, delayChildren: 0.1 } },
}

const item = {
  hidden: { opacity: 0, y: 16 },
  show: { opacity: 1, y: 0, transition: { duration: 0.6, ease: [0.22, 1, 0.36, 1] as const } },
}

export function Hero() {
  return (
    <section className="relative w-full min-h-[90vh] flex flex-col justify-center overflow-hidden bg-transparent">
      {/* Background is now handled globally by GlobalBackground */}
      
      {/* Dark/Transparent Overlay for text readability */}
      <div className="absolute inset-0 z-0 bg-gradient-to-r from-charcoal/90 via-charcoal/60 to-transparent" />
      <div className="absolute inset-0 z-0 bg-charcoal/20" />

      <div className="relative z-10 w-full mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8 lg:py-24 flex-1 flex flex-col justify-center">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
          
          {/* Left Content Area */}
          <motion.div
            variants={container}
            initial="hidden"
            animate="show"
            className="lg:col-span-7 xl:col-span-6 flex flex-col justify-center"
          >
            <motion.div variants={item}>
              <span className="inline-flex items-center gap-2 rounded-full border border-primary/40 bg-charcoal/40 px-4 py-1.5 text-xs font-semibold text-background shadow-sm backdrop-blur-md">
                <Sparkles className="size-3.5 text-primary animate-pulse" />
                Smart Finance for Rural India
              </span>
            </motion.div>

            <motion.h1
              variants={item}
              className="mt-6 font-display text-5xl font-extrabold leading-[1.1] tracking-tight text-white text-balance sm:text-6xl lg:text-7xl"
            >
              Grow your business.{' '}
              <span className="text-primary">
                Secure your future.
              </span>
            </motion.h1>

            <motion.p
              variants={item}
              className="mt-6 max-w-xl text-lg leading-relaxed text-background/80 text-pretty font-medium"
            >
              Helping rural entrepreneurs and farmers make smarter business and financial decisions with tailored local insights and government scheme matching.
            </motion.p>

            <motion.div variants={item} className="mt-10 flex flex-wrap items-center gap-4">
              <Link
                href="/assessment"
                className="group inline-flex items-center gap-2 rounded-full bg-primary px-7 py-4 text-base font-bold text-white shadow-lift transition-all hover:-translate-y-0.5 hover:bg-primary-hover hover:shadow-lg"
              >
                Check Your Eligibility →
              </Link>
              <Link
                href="/advisor"
                className="inline-flex items-center gap-2 rounded-full border border-background/30 bg-charcoal/40 px-7 py-4 text-base font-bold text-white backdrop-blur-md transition-all hover:bg-charcoal/60 hover:border-background/50"
              >
                <Bot className="size-5 text-primary" />
                Ask RuralEdge
              </Link>
            </motion.div>
          </motion.div>

          {/* Right Area - Left empty to let the background photograph shine through */}
          <div className="hidden lg:block lg:col-span-5 xl:col-span-6" />
        </div>
      </div>

      {/* Floating Information Cards Overlapping the Bottom */}
      <div className="relative z-20 w-full mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 mt-auto pb-12 lg:pb-0 lg:-mb-16">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
          {[
            {
              title: 'Loan Eligibility',
              desc: 'Check your limits instantly',
              icon: BadgeIndianRupee,
              delay: 0.2
            },
            {
              title: 'Scheme Match',
              desc: 'Find govt. subsidies',
              icon: Landmark,
              delay: 0.3
            },
            {
              title: 'Repayment Estimate',
              desc: 'Calculate exact EMIs',
              icon: TrendingUp,
              delay: 0.4
            },
            {
              title: 'Business Viability',
              desc: 'Data-driven rural insights',
              icon: Building2,
              delay: 0.5
            },
          ].map((card, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: card.delay, duration: 0.6 }}
              className="group flex flex-col gap-3 rounded-3xl border border-border/60 bg-background/95 p-6 shadow-lift backdrop-blur-xl transition-all hover:-translate-y-1 hover:border-primary/40"
            >
              <div className="flex size-12 items-center justify-center rounded-2xl bg-primary/10 text-primary transition-colors group-hover:bg-primary group-hover:text-white">
                <card.icon className="size-6" />
              </div>
              <div>
                <h3 className="font-display text-lg font-bold text-charcoal">{card.title}</h3>
                <p className="mt-1 text-sm font-medium text-muted-foreground">{card.desc}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Stat / Trust Strip */}
      <div className="relative z-10 w-full border-t border-border/10 bg-charcoal/80 backdrop-blur-md mt-12 lg:mt-24">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex flex-wrap items-center justify-center gap-8 md:justify-between text-background/70 text-sm font-semibold">
            <div className="flex items-center gap-2">
              <Landmark className="size-4 text-primary" />
              <span>Government Schemes</span>
            </div>
            <div className="hidden md:block w-1.5 h-1.5 rounded-full bg-background/30" />
            <div className="flex items-center gap-2">
              <Calculator className="size-4 text-primary" />
              <span>Loan Calculator</span>
            </div>
            <div className="hidden md:block w-1.5 h-1.5 rounded-full bg-background/30" />
            <div className="flex items-center gap-2">
              <TrendingUp className="size-4 text-primary" />
              <span>Business Insights</span>
            </div>
            <div className="hidden md:block w-1.5 h-1.5 rounded-full bg-background/30" />
            <div className="flex items-center gap-2">
              <ShieldCheck className="size-4 text-primary" />
              <span>Rural-focused guidance</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
