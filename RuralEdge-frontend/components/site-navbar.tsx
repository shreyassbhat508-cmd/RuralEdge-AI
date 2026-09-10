'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Menu, X, User, Sun, Moon, LogOut, Settings, Briefcase, LogIn, UserPlus } from 'lucide-react'
import { useState, useRef, useEffect } from 'react'
import { GramLogo } from '@/components/gram-logo'
import { LanguageSelector } from '@/components/language-selector'
import { useTheme } from '@/components/theme-provider'
import { useAuth } from '@/components/auth-context'
import { cn } from '@/lib/utils'

export const NAV_LINKS = [
  { href: '/schemes', label: 'Schemes' },
  { href: '/finance', label: 'Loan Calculator' },
  { href: '/market', label: 'My Business Plan' },
  { href: '/dashboard', label: 'Dashboard' },
]

export function SiteNavbar() {
  const pathname = usePathname()
  const [open, setOpen] = useState(false)
  const [profileOpen, setProfileOpen] = useState(false)
  const profileRef = useRef<HTMLDivElement>(null)
  const { theme, toggleTheme } = useTheme()
  const { user, signOut } = useAuth()

  useEffect(() => {
    const handleOutsideClick = (e: MouseEvent) => {
      if (profileRef.current && !profileRef.current.contains(e.target as Node)) {
        setProfileOpen(false)
      }
    }
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setProfileOpen(false)
    }

    if (profileOpen) {
      document.addEventListener('mousedown', handleOutsideClick)
      document.addEventListener('keydown', handleEscape)
    }
    return () => {
      document.removeEventListener('mousedown', handleOutsideClick)
      document.removeEventListener('keydown', handleEscape)
    }
  }, [profileOpen])

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
              <Sun className="size-4.5 text-gray-200 animate-in fade-in zoom-in spin-in-90 duration-300" />
            ) : (
              <Moon className="size-4.5 text-charcoal animate-in fade-in zoom-in spin-in-90 duration-300" />
            )}
          </button>

          <LanguageSelector />

          <div className="relative hidden sm:block" ref={profileRef}>
            <button
              type="button"
              aria-label="Profile"
              aria-expanded={profileOpen}
              onClick={() => setProfileOpen((v) => !v)}
              className={cn(
                "grid size-10 place-items-center rounded-full border border-border bg-card text-charcoal dark:text-foreground transition-colors hover:bg-muted",
                profileOpen && "bg-muted"
              )}
            >
              <User className="size-4.5" />
            </button>

            {profileOpen && (
              <div className="absolute right-0 mt-2 w-48 rounded-xl border border-border bg-card p-1.5 shadow-lg animate-in fade-in zoom-in-95 duration-200 z-50">
                <div className="px-2 py-1.5 text-sm font-medium border-b border-border mb-1 text-foreground">
                  My Account
                </div>
                {user ? (
                  <>
                    <Link
                      href="/profile"
                      onClick={() => setProfileOpen(false)}
                      className="flex items-center gap-2 rounded-lg px-2 py-1.5 text-sm text-foreground transition-colors hover:bg-primary/10 hover:text-primary"
                    >
                      <User className="size-4" />
                      Profile
                    </Link>
                    <Link
                      href="/market"
                      onClick={() => setProfileOpen(false)}
                      className="flex items-center gap-2 rounded-lg px-2 py-1.5 text-sm text-foreground transition-colors hover:bg-primary/10 hover:text-primary"
                    >
                      <Briefcase className="size-4" />
                      My Business Profile
                    </Link>
                    <Link
                      href="/settings"
                      onClick={() => setProfileOpen(false)}
                      className="flex items-center gap-2 rounded-lg px-2 py-1.5 text-sm text-foreground transition-colors hover:bg-primary/10 hover:text-primary"
                    >
                      <Settings className="size-4" />
                      Settings
                    </Link>
                    <div className="my-1 h-px bg-border" />
                    <button
                      type="button"
                      onClick={() => {
                        signOut()
                        setProfileOpen(false)
                      }}
                      className="flex w-full items-center gap-2 rounded-lg px-2 py-1.5 text-sm text-red-600 transition-colors hover:bg-red-50 dark:hover:bg-red-950/50"
                    >
                      <LogOut className="size-4" />
                      Logout
                    </button>
                  </>
                ) : (
                  <>
                    <Link
                      href="/signin"
                      onClick={() => setProfileOpen(false)}
                      className="flex items-center gap-2 rounded-lg px-2 py-1.5 text-sm text-foreground transition-colors hover:bg-primary/10 hover:text-primary"
                    >
                      <LogIn className="size-4" />
                      Sign In
                    </Link>
                    <Link
                      href="/signup"
                      onClick={() => setProfileOpen(false)}
                      className="flex items-center gap-2 rounded-lg px-2 py-1.5 text-sm text-foreground transition-colors hover:bg-primary/10 hover:text-primary"
                    >
                      <UserPlus className="size-4" />
                      Sign Up
                    </Link>
                  </>
                )}
              </div>
            )}
          </div>

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
                    <Sun className="size-3.5 text-gray-200" /> Light Mode
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
