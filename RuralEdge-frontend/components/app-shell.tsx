import { SiteNavbar } from '@/components/site-navbar'
import { SiteFooter } from '@/components/site-footer'
import { BottomNav } from '@/components/bottom-nav'

export function AppShell({
  children,
  footer = true,
}: {
  children: React.ReactNode
  footer?: boolean
}) {
  return (
    <div className="flex min-h-dvh flex-col">
      <SiteNavbar />
      <main className="flex-1 pb-20 lg:pb-0">{children}</main>
      {footer && <SiteFooter />}
      <BottomNav />
    </div>
  )
}


export function DemoNote({ children }: { children?: React.ReactNode }) {
  return (
    <span className="inline-flex items-center gap-1.5 rounded-full bg-gold/20 px-2.5 py-1 text-[11px] font-semibold text-[oklch(0.5_0.09_70)]">
      <span className="size-1.5 rounded-full bg-gold" />
      {children ?? 'Illustrative demo data'}
    </span>
  )
}
