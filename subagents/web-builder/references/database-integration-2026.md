# Database Integration 2026 — Reference

> Output Fase A research RQ2 → reference per skill `auth-database-setup`. Pattern setup completo Convex (default) + Supabase override.

## Convex (default `tech-stack-2026`)

### Setup minimo Next.js 15

```bash
# Inside project_path
npm install convex
npx --yes convex dev
# Browser OAuth: prima volta apre browser, login Convex
# Genera convex/ folder + .env.local con NEXT_PUBLIC_CONVEX_URL
```

### File structure post-setup

```
project/
├── convex/
│   ├── _generated/          # auto-generated, NOT edit, NOT commit di solito
│   ├── schema.ts            # database schema
│   ├── auth.config.ts       # auth provider config (se Clerk)
│   ├── <entity>.ts          # queries + mutations per entity
│   └── tsconfig.json        # convex-specific TS config
├── app/
│   └── ConvexClientProvider.tsx
└── .env.local               # NEXT_PUBLIC_CONVEX_URL
```

### Schema example

```typescript
// convex/schema.ts
import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  users: defineTable({
    clerkId: v.string(),
    email: v.string(),
    name: v.optional(v.string()),
    imageUrl: v.optional(v.string()),
  }).index("byClerkId", ["clerkId"]),

  items: defineTable({
    userId: v.id("users"),
    title: v.string(),
    description: v.optional(v.string()),
    completed: v.boolean(),
    dueAt: v.optional(v.number()),  // unix timestamp
  })
    .index("byUser", ["userId"])
    .index("byUserCompleted", ["userId", "completed"]),
});
```

### Query example

```typescript
// convex/items.ts
import { query, mutation } from "./_generated/server";
import { v } from "convex/values";

export const list = query({
  args: { userId: v.id("users") },
  handler: async (ctx, { userId }) => {
    return await ctx.db
      .query("items")
      .withIndex("byUser", (q) => q.eq("userId", userId))
      .collect();
  },
});

export const create = mutation({
  args: { userId: v.id("users"), title: v.string() },
  handler: async (ctx, { userId, title }) => {
    return await ctx.db.insert("items", { userId, title, completed: false });
  },
});
```

### Frontend usage (Next.js)

```typescript
"use client";
import { useQuery, useMutation } from "convex/react";
import { api } from "@/convex/_generated/api";

export function ItemsList({ userId }: { userId: string }) {
  const items = useQuery(api.items.list, { userId });
  const create = useMutation(api.items.create);

  if (items === undefined) return <div>Loading...</div>;

  return (
    <ul>
      {items.map((item) => (
        <li key={item._id}>{item.title}</li>
      ))}
    </ul>
  );
}
```

### Clerk integration (`auth.config.ts`)

```typescript
// convex/auth.config.ts
export default {
  providers: [
    {
      domain: process.env.CLERK_JWT_ISSUER_DOMAIN,
      applicationID: "convex",
    },
  ],
};
```

Then in app: wrap with `<ConvexProviderWithClerk>` (vedi skill `auth-database-setup`).

### Production deploy

```bash
# In CI/CD or pre Vercel deploy
npx convex deploy --cmd "npm run build"
# Output: production deployment URL → set come NEXT_PUBLIC_CONVEX_URL su Vercel
```

### Convex CLI commands

| Command | Use |
|---|---|
| `npx convex dev` | Start dev deployment, sync functions |
| `npx convex dev --once` | Init + deploy + exit (per script) |
| `npx convex deploy` | Production deploy |
| `npx convex logs` | View logs |
| `npx convex run <fn> <args>` | Test function from CLI |
| `npx convex import` | Import data (JSON Lines) |
| `npx convex export` | Export DB |

### Pattern reattivo

Cambi al DB triggerano automaticamente re-render UI (`useQuery` re-runs):
- Sub-50ms latency
- No setup pub/sub manuale
- No polling

### Convex Components for Payments

`tech-stack-2026` riferenza componenti Convex pre-costruiti per Stripe/Polar/Autumn:

```bash
npm install @convex-dev/aggregate @convex-dev/cron
# E specifici componenti payments
```

Vedi convex.dev/components per lista.

## Supabase (override SQL-friendly)

### Setup minimo Next.js 15

```bash
npm install @supabase/supabase-js @supabase/ssr
npx supabase init  # se vuoi local dev
```

### File structure

```
project/
├── lib/
│   └── supabase/
│       ├── client.ts      # browser client
│       ├── server.ts      # server client (cookie-based)
│       └── middleware.ts  # session refresh
├── supabase/
│   ├── config.toml         # local config (opzionale)
│   ├── migrations/         # SQL migrations
│   └── seed.sql           # seed data
└── .env.local              # NEXT_PUBLIC_SUPABASE_URL + keys
```

### Browser client

```typescript
// lib/supabase/client.ts
import { createBrowserClient } from "@supabase/ssr";

export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
  );
}
```

### Server client (App Router)

```typescript
// lib/supabase/server.ts
import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";

export async function createClient() {
  const cookieStore = await cookies();
  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll: () => cookieStore.getAll(),
        setAll: (cookiesToSet) => {
          cookiesToSet.forEach(({ name, value, options }) =>
            cookieStore.set(name, value, options),
          );
        },
      },
    },
  );
}
```

### Schema + RLS migration template

```sql
-- supabase/migrations/0001_init.sql
create table public.items (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users not null,
  title text not null,
  description text,
  completed boolean default false,
  due_at timestamptz,
  created_at timestamptz default now()
);

create index items_user_id_idx on public.items(user_id);

-- RLS
alter table public.items enable row level security;

create policy "users see own items"
  on public.items for select
  using (auth.uid() = user_id);

create policy "users insert own items"
  on public.items for insert
  with check (auth.uid() = user_id);

create policy "users update own items"
  on public.items for update
  using (auth.uid() = user_id);

create policy "users delete own items"
  on public.items for delete
  using (auth.uid() = user_id);
```

### Frontend query example

```typescript
"use client";
import { createClient } from "@/lib/supabase/client";

export async function loadItems() {
  const supabase = createClient();
  const { data, error } = await supabase
    .from("items")
    .select("*")
    .order("created_at", { ascending: false });
  if (error) throw error;
  return data;
}
```

### Realtime subscriptions

```typescript
const supabase = createClient();
const channel = supabase
  .channel("items-changes")
  .on("postgres_changes", { event: "*", schema: "public", table: "items" }, (payload) => {
    console.log("Change:", payload);
  })
  .subscribe();

// Cleanup
return () => { supabase.removeChannel(channel); };
```

## Comparison summary

| Feature | Convex | Supabase |
|---|---|---|
| Language | TypeScript-first | SQL + TS clients |
| Schema | Inferred from TS | SQL DDL migrations |
| Realtime | Built-in (sub-50ms) | Postgres changes channel |
| Auth integration | Clerk native (`ConvexProviderWithClerk`) | Built-in or hybrid Clerk |
| Hosting | Managed only | Managed or self-host |
| MCP server | ❌ (CLI fallback) | ❌ (no MCP yet) |
| Free tier | Generous (function calls) | 50k MAU, 500MB DB |
| Pricing model | Per function call | Per MAU + storage |
| Learning curve (non-dev) | Low (TS only) | Medium (SQL + RLS policies) |

## Decisione default + override

- **Default**: Convex (allineato `tech-stack-2026`, audience non-dev)
- **Override Supabase**: SQL legacy, RLS critical, self-host requirement, SQL knowledge esistente
- **No DB**: pure-static (landing senza signup, blog statico)
- **CMS-only**: Sanity/Contentful per editorial workflow strutturato

## Sources

- [docs.convex.dev — Convex Quickstart Next.js](https://docs.convex.dev/quickstart/nextjs)
- [stack.convex.dev — Convex vs Firebase/Supabase](https://stack.convex.dev/why-choose-convex-database-for-backend)
- [supabase.com/docs — Server-Side Auth Next.js](https://supabase.com/docs/guides/auth/server-side/nextjs)
- [bertomill medium — Convex vs Supabase 2026](https://bertomill.medium.com/convex-vs-supabase-which-backend-should-you-choose-in-2026-50d228c517de)
