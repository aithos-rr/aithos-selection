# shadcn/ui Patterns 2026 — Reference

> Output Fase A research RQ5 → reference per Phase 5 methodology (`/web-builder` Components + routes). Top 10 component patterns + setup Tailwind v4 + theme.

## Setup standard

### Init progetto

```bash
cd <project_path>
npx --yes shadcn@latest init
# Auto-detect Tailwind v4 (se installato)
# Asks: TS yes, style "new-york" (default 2026), base color "neutral", CSS vars yes
```

Output:
- `components.json` — config shadcn (style, base color, paths)
- `lib/utils.ts` — `cn()` helper (clsx + tailwind-merge)
- `tailwind.config.ts` (se Tailwind <v4) o CSS-based config v4
- `app/globals.css` — CSS variables theme

### Add components

```bash
# Single
npx --yes shadcn@latest add button

# Batch
npx --yes shadcn@latest add button card input form dialog sheet dropdown-menu toast skeleton
```

## Theme baseline

**2026 default**: `new-york` style + `neutral` base color (era `slate` in v0).

Custom theme via CSS variables in `app/globals.css`:

```css
@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 0 0% 3.9%;
    --primary: 0 0% 9%;
    --primary-foreground: 0 0% 98%;
    /* ... */
  }
  .dark {
    --background: 0 0% 3.9%;
    --foreground: 0 0% 98%;
    /* ... */
  }
}
```

Filippo prefer: `neutral` o `zinc` (depende preference).

## Top 10 component patterns

### 1. auth-form (login/signup)

**Use case**: SaaS, internal tool

```tsx
// app/(auth)/sign-in/[[...sign-in]]/page.tsx
import { SignIn } from "@clerk/nextjs";

export default function SignInPage() {
  return (
    <div className="flex min-h-screen items-center justify-center px-4">
      <div className="w-full max-w-md">
        <SignIn appearance={{ elements: { card: "shadow-lg" } }} />
      </div>
    </div>
  );
}
```

**Note**: Per audience consumer, prefer Clerk `<SignIn>` pre-built (full Clerk UI). Per custom design, use shadcn `Card` + `Form` + `Input`.

### 2. dashboard-layout (sidebar + header)

**Use case**: SaaS, internal tool

```tsx
// app/(dashboard)/layout.tsx
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/app-sidebar";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <SidebarProvider>
      <AppSidebar />
      <main className="flex-1">
        <header className="flex h-14 items-center border-b px-4">
          <SidebarTrigger />
          <h1 className="ml-4 font-semibold">Dashboard</h1>
        </header>
        <div className="p-6">{children}</div>
      </main>
    </SidebarProvider>
  );
}
```

Components needed: `sidebar`, `sidebar-trigger`, `separator`.

### 3. pricing-page

**Use case**: SaaS landing, marketing

```tsx
// app/pricing/page.tsx
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Check } from "lucide-react";

const tiers = [
  { name: "Free", price: 0, features: ["10 progetti", "Community support"] },
  { name: "Pro", price: 29, features: ["Unlimited", "Priority support", "Custom domain"], featured: true },
  { name: "Team", price: 99, features: ["Tutto Pro", "5 user seats", "SSO"] },
];

export default function Pricing() {
  return (
    <div className="grid gap-6 md:grid-cols-3">
      {tiers.map((tier) => (
        <Card key={tier.name} className={tier.featured ? "border-primary" : ""}>
          <CardHeader>
            <CardTitle>{tier.name}</CardTitle>
            <p className="text-3xl font-bold">€{tier.price}<span className="text-sm font-normal">/mese</span></p>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {tier.features.map((f) => (
                <li key={f} className="flex items-center gap-2"><Check className="h-4 w-4" />{f}</li>
              ))}
            </ul>
          </CardContent>
          <CardFooter>
            <Button className="w-full">{tier.featured ? "Inizia subito" : "Scegli"}</Button>
          </CardFooter>
        </Card>
      ))}
    </div>
  );
}
```

### 4. hero-section

**Use case**: landing top fold

```tsx
import { Button } from "@/components/ui/button";

export function Hero() {
  return (
    <section className="container mx-auto px-4 py-24 text-center">
      <h1 className="text-5xl font-bold tracking-tight md:text-7xl">
        Build faster, ship sooner
      </h1>
      <p className="mt-6 text-lg text-muted-foreground md:text-xl">
        Da idea a app deployata in 30 minuti. No code esperienza richiesta.
      </p>
      <div className="mt-10 flex justify-center gap-4">
        <Button size="lg">Inizia gratis</Button>
        <Button size="lg" variant="outline">Vedi demo</Button>
      </div>
    </section>
  );
}
```

### 5. data-table (TanStack Table integration)

**Use case**: internal tool, dashboard

Components: `data-table`, `command`, `dropdown-menu`, `pagination`.

Pattern: TanStack Table v8 + shadcn `Table` primitives + sort/filter/pagination integrato.

```tsx
// components/data-table.tsx
import { useReactTable, getCoreRowModel, ... } from "@tanstack/react-table";
import { Table, TableHeader, TableBody, TableRow, TableCell, TableHead } from "@/components/ui/table";

export function DataTable<T>({ data, columns }: { data: T[], columns: ColumnDef<T>[] }) {
  const table = useReactTable({ data, columns, getCoreRowModel: getCoreRowModel() });
  return (
    <Table>
      <TableHeader>{...}</TableHeader>
      <TableBody>{...}</TableBody>
    </Table>
  );
}
```

Riferimento avanzato: `Kiranism/next-shadcn-dashboard-starter` GitHub.

### 6. command-palette (Cmd+K)

**Use case**: internal tool con many actions

```tsx
import { Command, CommandInput, CommandList, CommandItem } from "@/components/ui/command";
import { Dialog, DialogContent } from "@/components/ui/dialog";

export function CommandMenu({ open, setOpen }) {
  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogContent className="p-0">
        <Command>
          <CommandInput placeholder="Search actions..." />
          <CommandList>
            <CommandItem onSelect={() => router.push("/dashboard")}>Dashboard</CommandItem>
            <CommandItem onSelect={() => router.push("/settings")}>Settings</CommandItem>
          </CommandList>
        </Command>
      </DialogContent>
    </Dialog>
  );
}
```

Bind shortcut: `useEffect` listen Cmd+K.

### 7. mode-toggle (light/dark/system)

```bash
npm install next-themes
```

```tsx
// components/theme-provider.tsx
"use client";
import { ThemeProvider as NextThemesProvider } from "next-themes";

export function ThemeProvider({ children, ...props }) {
  return <NextThemesProvider {...props}>{children}</NextThemesProvider>;
}
```

```tsx
// components/mode-toggle.tsx
import { useTheme } from "next-themes";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import { Moon, Sun } from "lucide-react";

export function ModeToggle() {
  const { setTheme } = useTheme();
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon"><Sun className="dark:hidden" /><Moon className="hidden dark:block" /></Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={() => setTheme("light")}>Light</DropdownMenuItem>
        <DropdownMenuItem onClick={() => setTheme("dark")}>Dark</DropdownMenuItem>
        <DropdownMenuItem onClick={() => setTheme("system")}>System</DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
```

### 8. sidebar-nav (collapsible)

```tsx
import { Sidebar, SidebarContent, SidebarMenu, SidebarMenuItem, SidebarMenuButton } from "@/components/ui/sidebar";
import { Home, Settings, BarChart } from "lucide-react";

const items = [
  { title: "Dashboard", url: "/dashboard", icon: Home },
  { title: "Analytics", url: "/analytics", icon: BarChart },
  { title: "Settings", url: "/settings", icon: Settings },
];

export function AppSidebar() {
  return (
    <Sidebar>
      <SidebarContent>
        <SidebarMenu>
          {items.map((item) => (
            <SidebarMenuItem key={item.title}>
              <SidebarMenuButton asChild>
                <a href={item.url}><item.icon /><span>{item.title}</span></a>
              </SidebarMenuButton>
            </SidebarMenuItem>
          ))}
        </SidebarMenu>
      </SidebarContent>
    </Sidebar>
  );
}
```

### 9. empty-state

```tsx
import { Inbox } from "lucide-react";
import { Button } from "@/components/ui/button";

export function EmptyState({ title, description, ctaLabel, onCta }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <Inbox className="h-16 w-16 text-muted-foreground" />
      <h3 className="mt-4 text-lg font-medium">{title}</h3>
      <p className="mt-2 text-sm text-muted-foreground">{description}</p>
      {ctaLabel && <Button onClick={onCta} className="mt-6">{ctaLabel}</Button>}
    </div>
  );
}
```

### 10. loading-skeleton

```tsx
import { Skeleton } from "@/components/ui/skeleton";

export function ItemsSkeleton() {
  return (
    <div className="space-y-3">
      {[1, 2, 3].map((i) => (
        <div key={i} className="flex items-center space-x-4">
          <Skeleton className="h-12 w-12 rounded-full" />
          <div className="space-y-2 flex-1">
            <Skeleton className="h-4 w-[250px]" />
            <Skeleton className="h-4 w-[200px]" />
          </div>
        </div>
      ))}
    </div>
  );
}
```

## Component installation default per template

| Template | Components iniziali (init) |
|---|---|
| `nextjs-saas` | button, card, input, form, dialog, sheet, dropdown-menu, toast, skeleton, sidebar, data-table, command, separator |
| `nextjs-landing` | button, card, separator (minimal) |
| `astro-marketing` | button, card (limited shadcn-svelte / shadcn-astro support) |
| `next-internal-tool` | come `nextjs-saas` + sidebar + data-table |

## Accessibility

shadcn components built on Radix UI primitives = a11y compliant (ARIA, keyboard nav, focus management). NO custom override su a11y a meno che non sai cosa fai.

## Customization

- Colors: edit CSS variables in `globals.css`
- Border radius: `--radius` variable
- Font: edit `tailwind.config.ts` o `globals.css` `@font-face`
- Variants: edit single component `<Component>.tsx` (è codice tuo, non lib esterna)

## Riferimenti starter

- [shadcn-ui/ui — official](https://ui.shadcn.com/docs/installation/next)
- [Kiranism/next-shadcn-dashboard-starter](https://github.com/Kiranism/next-shadcn-dashboard-starter) — 6k+ stars, RBAC, kanban
- [arhamkhnz/next-shadcn-admin-dashboard](https://github.com/arhamkhnz/next-shadcn-admin-dashboard) — modern admin
- [get-convex/template-nextjs-clerk-shadcn](https://github.com/get-convex/template-nextjs-clerk-shadcn) — Convex + Clerk + shadcn

## Anti-patterns

- 🔴 **Don't fork shadcn lib**: i components sono già nel tuo repo dopo `add`, edit liberamente NO need to fork.
- 🔴 **Don't import from `@/components/ui` shadcn outside**: shadcn components pensati come "your code", NOT external library.
- 🟡 **Tailwind v3 vs v4 differences**: v4 has CSS-first config (no `tailwind.config.ts`), use `@import "tailwindcss"` in CSS.
- 🟢 **Composition over customization**: prefer compose components esistenti che customizzare uno solo per caso edge.

## Sources

- [ui.shadcn.com/docs/installation/next](https://ui.shadcn.com/docs/installation/next)
- [thefrontkit.com — Best shadcn Dashboard Templates 2026](https://thefrontkit.com/blogs/best-shadcn-dashboard-templates-2026)
- [adminlte.io — Build Admin Dashboard with shadcn 2026](https://adminlte.io/blog/build-admin-dashboard-shadcn-nextjs/)
