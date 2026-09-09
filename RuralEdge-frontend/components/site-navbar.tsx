'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Menu, X, User, Sun, Moon } from 'lucide-react'
import { useState } from 'react'
import { GramLogo } from '@/components/gram-logo'
import { LanguageSelector } from '@/components/language-selector'
import { useTheme } from '@/components/theme-provider'
import { cn } from '@/lib/utils'

export const NAV_LINKS = [
  { href: '/advisor', label: 'Chatbot' },
  { href: '/schemes', label: 'Schemes' },
  { href: '/finance', label: 'Loan Calculator' },
  { href: '/market', label: 'My Business Plan' },
  { href: '/dashboard', label: 'Dashboard' },
]

export function SiteNavbar() {
  const pathname = usePathname()
  const [open, setOpen] = useState(false)
  const { theme, toggleTheme } = useTheme()

  const isActive = (href: string) =>
    href === '/' ? pathname === '/' : pathname.startsWith(href)

  return (
    <header className="sticky top-0 z-40 border-b border-border/80 bg-background/85 backdrop-blur-md transition-colors duration-300">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between gap-4 px-4 sm:px-6">
        <Link href="/" className="shrink-0">
          <GramLogo />
        </Link>

        <nav className="hidden items-center gap-1 lg:flex">
          {NAV_LINKS.map((l) => (
            <Link
              key={l.href}
              href={l.href}
              className={cn(
                'rounded-full px-3.5 py-2 text-sm font-medium transition-colors',
                isActive(l.href)
                  ? 'bg-primary/10 text-primary font-semibold'
                  : 'text-muted-foreground hover:bg-muted hover:text-foreground',
              )}
            >
              {l.label}
            </Link>
          ))}
        </nav>

        <div className="flex items-center gap-2">
          {/* Theme Toggle Button */}
          <button
            type="button"
            onClick={toggleTheme}
            aria-label={theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme'}
            title={theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme'}
            className="grid size-10 place-items-center rounded-full border border-border bg-card text-foreground transition-all hover:bg-muted hover:scale-105 active:scale-95"
          >
            {theme === 'dark' ? (
              <Sun className="size-4.5 text-sand animate-in fade-in zoom-in spin-in-90 duration-300" />
            ) : (
              <Moon className="size-4.5 text-charcoal animate-in fade-in zoom-in spin-in-90 duration-300" />
            )}
          </button>

          <LanguageSelector />

          <button
            type="button"
            aria-label="Profile"
            className="hidden size-10 place-items-center rounded-full border border-border bg-card text-charcoal dark:text-sand transition-colors hover:bg-muted sm:grid"
          >
            <User className="size-4.5" />
          </button>

          <Link
            href="/advisor"
            className="hidden rounded-full bg-primary px-4 py-2.5 text-sm font-semibold text-white shadow-soft transition-transform hover:-translate-y-0.5 hover:bg-primary-hover md:inline-flex"
          >
            Ask RuralEdge Chatbot
          </Link>

          <button
            type="button"
            aria-label="Open menu"
            aria-expanded={open}
            onClick={() => setOpen((v) => !v)}
            className="grid size-10 place-items-center rounded-full border border-border bg-card lg:hidden"
          >
            {open ? <X className="size-5" /> : <Menu className="size-5" />}
          </button>
        </div>
      </div>

      {open && (
        <div className="border-t border-border bg-background lg:hidden">
          <nav className="mx-auto flex max-w-7xl flex-col gap-1 px-4 py-3 sm:px-6">
            {NAV_LINKS.map((l) => (
              <Link
                key={l.href}
                href={l.href}
                onClick={() => setOpen(false)}
                className={cn(
                  'rounded-xl px-4 py-3 text-base font-medium',
                  isActive(l.href)
                    ? 'bg-primary/10 text-primary font-semibold'
                    : 'text-foreground hover:bg-muted',
                )}
              >
                {l.label}
              </Link>
            ))}
            <div className="flex items-center justify-between px-4 py-2 my-1 rounded-xl bg-card border border-border">
              <span className="text-sm font-medium text-foreground">Theme</span>
              <button
                type="button"
                onClick={toggleTheme}
                className="inline-flex items-center gap-2 rounded-full border border-border px-3 py-1.5 text-xs font-semibold bg-background"
              >
                {theme === 'dark' ? (
                  <>
                    <Sun className="size-3.5 text-sand" /> Light Mode
                  </>
                ) : (
                  <>
                    <Moon className="size-3.5 text-charcoal" /> Dark Mode
                  </>
                )}
              </button>
            </div>
            <Link
              href="/assessment"
              onClick={() => setOpen(false)}
              className="mt-2 rounded-xl bg-primary px-4 py-3 text-center text-base font-semibold text-white hover:bg-primary-hover"
            >
              Start Business Assessment
            </Link>
          </nav>
        </div>
      )}
    </header>
  )
}
