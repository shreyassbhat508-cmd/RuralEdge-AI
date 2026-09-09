import Link from 'next/link'
import { ArrowRight } from 'lucide-react'
import { Reveal } from '@/components/reveal'

export function CtaBand() {
  return (
    <section id="about" className="mx-auto max-w-7xl px-4 py-20 sm:px-6">
      <Reveal>
        <div className="relative overflow-hidden rounded-3xl bg-charcoal px-6 py-14 text-center shadow-lift sm:px-12 md:py-20">
          <div className="bg-field-lines absolute inset-0 opacity-30" aria-hidden />
          <div className="relative mx-auto max-w-2xl">
            <h2 className="font-display text-3xl font-extrabold tracking-tight text-balance text-background dark:text-[#F5F7F5] md:text-4xl">
              Your next business decision deserves real clarity
            </h2>
            <p className="mt-4 text-lg leading-relaxed text-background/80 dark:text-[#B8C0CC] text-pretty">
              Start a free assessment and get your business health score, an
              affordable financing plan and the schemes you qualify for — in
              minutes.
            </p>
            <div className="mt-8 flex flex-wrap justify-center gap-3">
              <Link
                href="/assessment"
                className="group inline-flex items-center gap-2 rounded-full bg-primary px-6 py-3.5 text-base font-semibold text-white shadow-soft transition-transform hover:-translate-y-0.5 hover:bg-primary-hover"
              >
                Start Business Assessment
                <ArrowRight className="size-4.5 transition-transform group-hover:translate-x-1" />
              </Link>
              <Link
                href="/advisor"
                className="inline-flex items-center gap-2 rounded-full border border-sand/30 px-6 py-3.5 text-base font-semibold text-background dark:text-[#D5DCE5] transition-colors hover:bg-white/10"
              >
                Ask the AI Advisor
              </Link>
            </div>
          </div>
        </div>
      </Reveal>
    </section>
  )
}
