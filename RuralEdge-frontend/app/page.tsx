import { AppShell } from '@/components/app-shell'
import { AdvisorView } from '@/components/advisor/advisor-view'

export default function HomePage() {
  return (
    <AppShell footer={false}>
      <AdvisorView />
    </AppShell>
  )
}
