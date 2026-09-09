'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  Home,
  LayoutDashboard,
  Search,
  Landmark,
  Calculator,
  MessageCircle,
} from 'lucide-react'
import { cn } from '@/lib/utils'

const ITEMS = [
  { href: '/advisor', label: 'Chatbot', icon: MessageCircle },
  { href: '/schemes', label: 'Schemes', icon: Landmark },
  { href: '/finance', label: 'Calculator', icon: Calculator },
  { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
]


export function BottomNav() {
  const pathname = usePathname()
  const isActive = (href: string) =>
    href === '/' ? pathname === '/' : pathname.startsWith(href)

  return (
    <nav className="fixed inset-x-0 bottom-0 z-40 border-t border-border bg-background/95 backdrop-blur-md lg:hidden">
      <ul className="mx-auto flex max-w-lg items-stretch justify-between px-2">
        {ITEMS.map((item) => {
          const Icon = item.icon
          const active = isActive(item.href)
          return (
            <li key={item.href} className="flex-1">
              <Link
                href={item.href}
                className={cn(
                  'flex flex-col items-center gap-1 py-2.5 text-[11px] font-medium transition-colors',
                  active ? 'text-primary font-semibold' : 'text-muted-foreground',
                )}
              >
                <span
                  className={cn(
                    'grid size-9 place-items-center rounded-full transition-colors',
                    active && 'bg-primary/12',
                  )}
                >
                  <Icon className="size-5" />
                </span>
                {item.label}
              </Link>
            </li>
          )
        })}
      </ul>
    </nav>
  )
}
