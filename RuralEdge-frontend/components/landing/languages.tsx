import { Reveal } from '@/components/reveal'
import { LANGUAGES } from '@/lib/data'

const GREETINGS: Record<string, string> = {
  en: 'Grow your business',
  hi: 'अपना व्यवसाय बढ़ाएँ',
  kn: 'ನಿಮ್ಮ ವ್ಯಾಪಾರ ಬೆಳೆಸಿ',
  ta: 'உங்கள் தொழிலை வளர்க்கவும்',
  te: 'మీ వ్యాపారాన్ని పెంచుకోండి',
  mr: 'तुमचा व्यवसाय वाढवा',
  bn: 'আপনার ব্যবসা বাড়ান',
}

export function LanguagesSection() {
  return (
    <section
      id="languages"
      className="mx-auto max-w-7xl px-4 py-20 sm:px-6"
    >
      <div className="grid items-center gap-10 lg:grid-cols-2">
        <Reveal>
          <p className="text-xs font-semibold tracking-[0.16em] text-primary uppercase">
            Made for Bharat
          </p>
          <h2 className="mt-3 font-display text-3xl font-extrabold tracking-tight text-balance md:text-4xl">
            In the language you think, dream and count in
          </h2>
          <p className="mt-4 text-lg leading-relaxed text-muted-foreground text-pretty">
            Financial words are hard enough in your mother tongue. RuralEdge
            speaks seven Indian languages and explains every term in plain,
            everyday words — so nothing gets lost in translation.
          </p>
          <p className="mt-4 text-sm font-medium text-charcoal dark:text-background">
            English · हिंदी · ಕನ್ನಡ · தமிழ் · తెలుగు · मराठी · বাংলা
          </p>
        </Reveal>

        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
          {LANGUAGES.map((l, i) => (
            <Reveal key={l.code} delay={i * 0.05}>
              <div className="rounded-2xl border border-border bg-card p-5 shadow-soft">
                <p className="text-xs font-semibold tracking-wide text-muted-foreground uppercase">
                  {l.label}
                </p>
                <p className="mt-2 font-display text-lg font-bold text-primary">
                  {l.native}
                </p>
                <p className="mt-1 text-sm leading-snug text-foreground">
                  {GREETINGS[l.code]}
                </p>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  )
}
