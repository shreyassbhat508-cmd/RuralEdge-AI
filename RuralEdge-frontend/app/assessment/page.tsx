import { AppShell } from '@/components/app-shell'
import { AssessmentFlow } from '@/components/assessment/assessment-flow'

export default function AssessmentPage() {
  return (
    <AppShell footer={false}>
      <div className="bg-contour">
        <AssessmentFlow />
      </div>
    </AppShell>
  )
}
