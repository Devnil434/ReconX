# ReconX Control Center Dashboard

This is the Next.js frontend application for **ReconX**, providing a premium real-time command center for monitoring payment reconciliation, ledger health, system workers, and AI investigation details.

---

## Key Features

1. **Reconciliation Control Center (`/dashboard`)**:
   - **4 KPI Cards**: Real-time stats showing total transactions, match rate, active exceptions count, and false auto-resolution rate.
   - **Engine Health Progress Bars**: Dynamic bars indicating matched rate vs exceptions vs AI accuracy.
   - **Case Stream**: Live vertical timeline of incoming exception cases with custom severity badges.
   - **Autonomous Case Board**: A 3-lane kanban (Auto-Resolve, Human Review, Blocked) showing case assignment status at a glance.
   - **Explainability Drawer ("Why?" Drawer)**: Slides in from the right to explain root causes, confidence levels, ranked hypotheses, verified/unverified evidence checks, and execution logs.
   - **One-Click Playback**: Allows triggers for synthetic demo scenarios (`Fee Mismatch`, `Missing Bank`, `Duplicate Settlement`, `Unknown Discrepancy`, `AI Failure`).

2. **System Health (`/system`)**:
   - Live checks for the database, API server, Redis queue depths (`reconciliation`, `investigation`, `actions`, `dead_letter`), active workers count, and AI cost metrics. Auto-refreshes every 15 seconds.

3. **Performance Report (`/benchmark`)**:
   - High-fidelity metrics summarizing engine benchmarks against 100k transaction datasets: sub-ms median latencies, AI evaluations, error taxonomies, and false auto-resolution ratios.

---

## Technology Stack

- **Framework**: Next.js 16 (App Router)
- **Styling**: Tailwind CSS 4, custom dark-mode variables, animations (`fade-up`, `drawer-enter`, `status-pulse`)
- **Icons**: Lucide React
- **API Client**: Axios

---

## Development Setup

### 1. Configure environment
Create `.env.local` inside this directory:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 2. Install dependencies & start
```bash
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) to view the Control Center.

---

## Build Checklist
To compile for production:
```bash
npm run build
```
The application builds with zero TypeScript errors or lint issues.
