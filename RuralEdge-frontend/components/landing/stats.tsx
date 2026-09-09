import { CountUp } from '@/components/count-up'
import { Reveal } from '@/components/reveal'

const STATS = [
  { value: 63, suffix: '%', label: 'of India lives in rural areas' },
  { value: 7, suffix: '', label: 'Indian languages supported' },
  { value: 40, suffix: '+', label: 'government schemes mapped' },
  { value: 5, suffix: 'km', label: 'local market radius analysed' },
]

export function Stats() {
  return (
    <section className="border-y border-border bg-card">
      <div className="mx-auto grid max-w-7xl grid-cols-2 gap-6 px-4 py-10 sm:px-6 md:grid-cols-4 md:py-12">
        {STATS.map((s, i) => (
          <Reveal
            key={s.label}
            delay={i * 0.08}
            className="text-center md:text-left"
          >
            <p className="font-display text-4xl font-extrabold text-primary md:text-5xl">
              <CountUp value={s.value} />
              {s.suffix}
            </p>
            <p className="mt-1.5 text-sm leading-snug text-muted-foreground">
              {s.label}
            </p>
          </Reveal>
        ))}
      </div>
    </section>
  )
}
