import Link from 'next/link'
import { GramLogo } from '@/components/gram-logo'

const COLS = [
  {
    title: 'Product',
    links: [
      { label: 'How it works', href: '/#how' },
      { label: 'Business Advisory', href: '/advisor' },
      { label: 'Finance', href: '/finance' },
      { label: 'Government Support', href: '/schemes' },
    ],
  },
  {
    title: 'Company',
    links: [
      { label: 'About', href: '/#about' },
      { label: 'Languages', href: '/#languages' },
      { label: 'Privacy', href: '/#privacy' },
      { label: 'Terms', href: '/#terms' },
    ],
  },
]

export function SiteFooter() {
  return (
    <footer className="border-t border-border bg-secondary/40">
      <div className="crop-divider" aria-hidden />
      <div className="mx-auto grid max-w-7xl gap-10 px-4 py-12 sm:px-6 md:grid-cols-[1.4fr_1fr_1fr]">
        <div className="max-w-sm">
          <GramLogo />
          <p className="mt-4 text-sm leading-relaxed text-muted-foreground">
            AI-powered business intelligence for rural entrepreneurs. Build the
            right business. Borrow with confidence.
          </p>
          <p className="mt-4 text-xs font-medium text-charcoal dark:text-background">
            Built for rural and semi-urban entrepreneurs.
          </p>
        </div>
        {COLS.map((col) => (
          <div key={col.title}>
            <h4 className="text-sm font-semibold text-foreground">
              {col.title}
            </h4>
            <ul className="mt-4 flex flex-col gap-2.5">
              {col.links.map((l) => (
                <li key={l.label}>
                  <Link
                    href={l.href}
                    className="text-sm text-muted-foreground transition-colors hover:text-primary"
                  >
                    {l.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
      <div className="border-t border-border/70">
        <div className="mx-auto flex max-w-7xl flex-col gap-2 px-4 py-5 text-xs text-muted-foreground sm:flex-row sm:items-center sm:justify-between sm:px-6">
          <p>© {new Date().getFullYear()} RuralEdge. A hackathon demo — figures are illustrative.</p>
          <p>Made in India for Bharat&apos;s entrepreneurs.</p>
        </div>
      </div>
    </footer>
  )
}
