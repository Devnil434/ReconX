import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

interface MetricProps {
  title: string;
  value: string;
}

function Metric({ title, value }: MetricProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
      </CardContent>
    </Card>
  );
}

export default function Home() {
  return (
    <main className="min-h-screen bg-background p-8">
      <div className="mx-auto max-w-7xl space-y-8">
        <div>
          <Badge>RECOVERRECON</Badge>

          <h1 className="mt-4 text-4xl font-bold tracking-tight">
            Reconciliation Control Center
          </h1>

          <p className="mt-2 text-muted-foreground">
            Autonomous payment reconciliation and investigation.
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-4">
          <Metric
            title="Transactions"
            value="0"
          />

          <Metric
            title="Match Rate"
            value="0%"
          />

          <Metric
            title="Exceptions"
            value="0"
          />

          <Metric
            title="Auto Resolved"
            value="0%"
          />
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Investigation Queue</CardTitle>
          </CardHeader>

          <CardContent>
            <p className="text-sm text-muted-foreground">
              No investigations yet.
            </p>
          </CardContent>
        </Card>
      </div>
    </main>
  );
}