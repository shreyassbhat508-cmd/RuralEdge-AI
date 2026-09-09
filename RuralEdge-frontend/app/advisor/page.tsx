import { AppShell } from '@/components/app-shell'
import { AdvisorView } from '@/components/advisor/advisor-view'

export default function AdvisorPage() {
  return (
    <AppShell footer={false}>
      <AdvisorView />
    </AppShell>
  )
}
