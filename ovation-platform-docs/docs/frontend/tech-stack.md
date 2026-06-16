# Frontend Tech Stack

**Status:** `[COMPLETE]`
**Decision record:** [ADR-001 — Frontend Framework](../architecture/decisions/ADR-001-frontend-framework.md)

---

## Summary

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| Framework | Next.js | 14 (App Router) | Routing, SSR, layout system |
| Language | TypeScript | 5.x | Type safety across frontend |
| UI Components | shadcn/ui | Latest | Owned component library |
| Styling | Tailwind CSS | 3.x | Utility-first CSS |
| Data Tables | TanStack Table | v8 | Bid tables, sorting, filtering |
| Charts | Recharts | 2.x | Budget vs. actuals, variance |
| Client State | Zustand | 4.x | UI state, user preferences |
| Server State | TanStack Query | v5 | API data, caching, sync |
| Auth | NextAuth.js | 5.x | Azure AD SSO |
| Forms | React Hook Form | 7.x | Form state + validation |
| Validation | Zod | 3.x | Schema validation, type inference |
| Icons | Lucide React | Latest | Icon set |

---

## Why Each Choice

### Next.js 14 — App Router
The App Router's layout system maps perfectly to the application's UI structure: persistent sidebar + dynamic main content area. Server Components allow bid table data to be fetched on the server, reducing the loading state complexity for data-heavy views. File-based routing keeps the page structure readable.

We use the **App Router exclusively** — the Pages Router is not used in this project.

### TypeScript
All files are `.tsx` or `.ts`. No JavaScript files in the frontend. TypeScript catches contract mismatches between the frontend and .NET API early — especially important for financial data where a type error is a real money error.

### shadcn/ui + Tailwind CSS
shadcn/ui is not an installed library — it's a collection of components that we copy into `/components/ui` and own. This means we can modify any component without fighting a library's API. This matters for the bid tables, modals, and custom financial inputs that need pixel-precise behavior.

Tailwind classes are used exclusively — no external CSS files except for global resets.

### TanStack Table
The bid leveling table is the core UI of the entire application. It has:
- 50+ rows per budget level
- Expandable division → trade → line item hierarchy
- Inline editing on multiple cell types
- Column sorting and filtering
- Virtual scrolling for performance at scale

TanStack Table handles all of this. No other table library in the React ecosystem comes close for this use case.

### Recharts
Budget variance charts (L2 vs L3 by division) and project dashboard charts. Recharts has the best balance of simplicity, performance, and customizability for financial bar/line charts.

### Zustand
Client-side state that does not come from the API: sidebar collapse state, active filters, table column visibility, user preferences. Zustand's minimal API keeps state management from becoming a secondary concern.

### TanStack Query (React Query)
All server data — projects, budget levels, line items, bids — flows through React Query. It handles caching, background refetching, optimistic updates (instant UI response before the API confirms), and error states. No raw `useEffect` + `fetch` patterns.

### NextAuth.js
Handles the Azure AD OAuth 2.0 flow, session management, and JWT storage. The session is available in both Server Components and Client Components. See [auth.md](../../backend/auth.md) for the full auth architecture.

### Zod
All API responses are validated against Zod schemas at the boundary. If the API returns a field the frontend doesn't expect (or is missing a required one), it fails loudly in development and logs a warning in production. This prevents silent data corruption.

---

## Folder Structure

```
frontend/
├── app/                          ← Next.js App Router pages
│   ├── layout.tsx                ← Root layout (sidebar, auth check)
│   ├── page.tsx                  ← Redirect to /dashboard
│   ├── dashboard/
│   │   └── page.tsx              ← Project list + summary metrics
│   ├── projects/
│   │   └── [id]/
│   │       └── level/
│   │           └── [level]/
│   │               └── page.tsx  ← Bid leveling table
│   └── api/                      ← Next.js API routes (auth only)
│       └── auth/
│           └── [...nextauth]/
│               └── route.ts
│
├── components/
│   ├── ui/                       ← shadcn/ui components (owned)
│   │   ├── button.tsx
│   │   ├── dialog.tsx
│   │   ├── table.tsx
│   │   └── ...
│   ├── layout/
│   │   ├── Sidebar.tsx           ← Project navigation sidebar
│   │   ├── Header.tsx            ← Top bar, notifications, user menu
│   │   └── PageLayout.tsx        ← Wraps main content area
│   ├── budget/
│   │   ├── BidTable.tsx          ← Main bid leveling table
│   │   ├── DivisionRow.tsx       ← Expandable division row
│   │   ├── LineItemRow.tsx       ← Individual line item row
│   │   ├── BidPickerModal.tsx    ← Subcontractor bid selector
│   │   ├── MarkupPanel.tsx       ← Markup percentage controls
│   │   └── BudgetSummaryCards.tsx
│   ├── files/
│   │   ├── FileUploadZone.tsx    ← Drag and drop upload
│   │   ├── ColumnMapper.tsx      ← Manual field mapping UI
│   │   └── ParseProgressBar.tsx  ← SignalR progress indicator
│   └── charts/
│       ├── VarianceChart.tsx
│       └── DivisionBreakdown.tsx
│
├── lib/
│   ├── api.ts                    ← Typed API client (fetch wrapper)
│   ├── auth.ts                   ← NextAuth config
│   └── utils.ts                  ← cn() and other utilities
│
├── hooks/
│   ├── useCurrentUser.ts
│   ├── useBudgetLevel.ts
│   └── useFileUpload.ts
│
├── stores/
│   └── uiStore.ts                ← Zustand store
│
├── types/
│   ├── api.ts                    ← API response types (from OpenAPI)
│   ├── budget.ts                 ← Budget domain types
│   └── user.ts                   ← User + role types
│
└── styles/
    └── globals.css               ← Tailwind base + CSS variables
```

---

## Naming Conventions

| Thing | Convention | Example |
|---|---|---|
| Components | PascalCase | `BidTable.tsx` |
| Hooks | camelCase with `use` prefix | `useBudgetLevel.ts` |
| Utilities | camelCase | `formatCurrency.ts` |
| Types/interfaces | PascalCase | `BudgetLevelLineItem` |
| Constants | SCREAMING_SNAKE | `MAX_FILE_SIZE_MB` |
| API routes | kebab-case | `/api/budget-levels` |

---

## Environment Variables

All environment variables are prefixed with `NEXT_PUBLIC_` only if they need to be accessible in the browser. Secrets never use `NEXT_PUBLIC_`.

```env
# .env.local (never committed)
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=...
AZURE_AD_CLIENT_ID=...
AZURE_AD_CLIENT_SECRET=...
AZURE_AD_TENANT_ID=...
NEXT_PUBLIC_API_URL=http://localhost:5001
```

---

## Performance Targets

| Metric | Target |
|---|---|
| First Contentful Paint | < 1.5s |
| Time to Interactive | < 3s |
| Bid table render (50 rows) | < 100ms |
| File upload feedback | < 500ms (SignalR connected) |
