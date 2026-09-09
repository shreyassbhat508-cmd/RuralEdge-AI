import { AppShell } from '@/components/app-shell'
import { LandingPage } from '@/components/landing/landing-page'

export default function HomePage() {
  return (
    <AppShell footer={true}>
      <LandingPage />
    </AppShell>
  )
}
