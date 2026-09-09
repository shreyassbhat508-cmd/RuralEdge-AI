import { Quote } from 'lucide-react'
import { Reveal } from '@/components/reveal'
import { Business3DBadge } from '@/components/three/business-3d-badge'

const STORIES = [
  {
    quote:
      'I finally understood how much loan I could actually repay. RuralEdge showed me the EMI in Kannada, in words I use every day.',
    name: 'Lakshmi B.',
    role: 'Dairy owner · Ramanagara, KA',
    type: 'dairy' as const,
    tone: 'bg-card',
    avatarBg: 'bg-primary',
    initials: 'LB',
  },
  {
    quote:
      'It told me there were already four kirana stores nearby, but almost no one selling fresh curd. That one insight changed my whole plan.',
    name: 'Suresh P.',
    role: 'Food processing · Nashik, MH',
    type: 'food' as const,
    tone: 'bg-charcoal text-white',
    avatarBg: 'bg-sand text-charcoal',
    initials: 'SP',
  },
  {
    quote:
      'I did not know a government scheme covered half my equipment cost. The AI advisor found it for me in minutes.',
    name: 'Anita D.',
    role: 'Handicrafts & Loom · Bhagalpur, BR',
    type: 'textiles' as const,
    tone: 'bg-card',
    avatarBg: 'bg-primary',
    initials: 'AD',
  },
]

export function Stories() {
  return (
    <section className="relative border-y border-border bg-secondary/20 py-20">
      <div className="crop-divider absolute top-0 left-0 right-0" />

      <div className="mx-auto max-w-7xl px-4 sm:px-6">
        <Reveal className="mx-auto max-w-2xl text-center">
          <p className="text-xs font-semibold tracking-[0.16em] text-primary uppercase">
            Entrepreneur stories
          </p>
          <h2 className="mt-3 font-display text-3xl font-extrabold tracking-tight text-foreground text-balance md:text-4xl">
            Decisions made with clarity, not guesswork
          </h2>
          <p className="mt-3 text-sm text-muted-foreground">
            Illustrative stories representing the rural micro-entrepreneurs RuralEdge empowers.
          </p>
        </Reveal>

        <div className="mt-14 grid gap-6 md:grid-cols-3">
          {STORIES.map((s, i) => {
            const dark = s.tone.includes('text-white') || s.tone.includes('text-primary-foreground')
            return (
              <Reveal key={s.name} delay={i * 0.1}>
                <figure
                  className={`flex h-full flex-col justify-between rounded-2xl border border-border/80 p-7 shadow-soft transition-transform duration-300 hover:-translate-y-1 ${s.tone}`}
                >
                  <div>
                    <div className="flex items-center justify-between">
                      <Quote
                        className={`size-8 ${dark ? 'text-white/40' : 'text-primary/30'}`}
                      />
                      <Business3DBadge type={s.type} size="sm" />
                    </div>
                    <blockquote
                      className={`mt-4 text-base leading-relaxed ${dark ? 'text-white/90' : 'text-foreground'}`}
                    >
                      &ldquo;{s.quote}&rdquo;
                    </blockquote>
                  </div>

                  <figcaption className="mt-6 flex items-center gap-3 border-t border-border/40 pt-4">
                    <div
                      className={`grid size-10 place-items-center rounded-full font-bold shadow-sm ${s.avatarBg}`}
                    >
                      {s.initials}
                    </div>
                    <div>
                      <p className="font-bold leading-tight">{s.name}</p>
                      <p
                        className={`text-xs ${dark ? 'text-white/75' : 'text-muted-foreground'}`}
                      >
                        {s.role}
                      </p>
                    </div>
                  </figcaption>
                </figure>
              </Reveal>
            )
          })}
        </div>
      </div>
    </section>
  )
}
