# Auth Integration 2026 — Reference

> Output Fase A research RQ3 → reference per skill `auth-database-setup`. Setup Clerk (default) + WorkOS (enterprise) + custom adapter pattern.

## Clerk (default)

### Setup Next.js 15 App Router

```bash
npm install @clerk/nextjs
```

### Provider setup

```typescript
// app/layout.tsx
import { ClerkProvider } from "@clerk/nextjs";
import { itIT } from "@clerk/localizations";  // localizzazione italiana

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <ClerkProvider localization={itIT}>
      <html lang="it"><body>{children}</body></html>
    </ClerkProvider>
  );
}
```

### Middleware (route protection)

```typescript
// middleware.ts
import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";

const isProtectedRoute = createRouteMatcher([
  "/dashboard(.*)",
  "/api(.*)",
  "/settings(.*)",
]);

export default clerkMiddleware(async (auth, req) => {
  if (isProtectedRoute(req)) {
    await auth.protect();
  }
});

export const config = {
  matcher: [
    "/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|png|webp|svg|ico|map)).*)",
    "/(api|trpc)(.*)",
  ],
};
```

### Sign-in / Sign-up pages

```typescript
// app/(auth)/sign-in/[[...sign-in]]/page.tsx
import { SignIn } from "@clerk/nextjs";

export default function SignInPage() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <SignIn />
    </div>
  );
}
```

Routes Clerk default:
- `/sign-in` — sign-in page
- `/sign-up` — sign-up page
- `/user-profile` — user settings

### Server Components access user

```typescript
import { auth, currentUser } from "@clerk/nextjs/server";

export default async function DashboardPage() {
  const { userId } = await auth();
  if (!userId) return null;  // middleware già redirect, ma safety net

  const user = await currentUser();
  return <div>Hello {user?.firstName}</div>;
}
```

### Client Components access user

```typescript
"use client";
import { useUser, UserButton, SignedIn, SignedOut, SignInButton } from "@clerk/nextjs";

export function Header() {
  const { user, isLoaded } = useUser();
  return (
    <header>
      <SignedIn>
        <UserButton />
      </SignedIn>
      <SignedOut>
        <SignInButton mode="modal" />
      </SignedOut>
    </header>
  );
}
```

### Convex integration (`ConvexProviderWithClerk`)

```typescript
// app/ConvexClientProvider.tsx
"use client";
import { ConvexReactClient } from "convex/react";
import { ConvexProviderWithClerk } from "convex/react-clerk";
import { ClerkProvider, useAuth } from "@clerk/nextjs";

const convex = new ConvexReactClient(process.env.NEXT_PUBLIC_CONVEX_URL!);

export function ConvexClientProvider({ children }: { children: React.ReactNode }) {
  return (
    <ClerkProvider publishableKey={process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY!}>
      <ConvexProviderWithClerk client={convex} useAuth={useAuth}>
        {children}
      </ConvexProviderWithClerk>
    </ClerkProvider>
  );
}
```

### Webhook user sync (Clerk → Convex)

Per persistere user in Convex `users` table al signup:

```typescript
// app/api/webhook/clerk/route.ts
import { Webhook } from "svix";
import { headers } from "next/headers";
import { internal } from "@/convex/_generated/api";
import { ConvexHttpClient } from "convex/browser";

const convex = new ConvexHttpClient(process.env.NEXT_PUBLIC_CONVEX_URL!);

export async function POST(req: Request) {
  const wh = new Webhook(process.env.CLERK_WEBHOOK_SECRET!);
  const headerPayload = await headers();
  const svixHeaders = {
    "svix-id": headerPayload.get("svix-id")!,
    "svix-timestamp": headerPayload.get("svix-timestamp")!,
    "svix-signature": headerPayload.get("svix-signature")!,
  };

  const body = await req.text();
  const evt = wh.verify(body, svixHeaders) as any;

  if (evt.type === "user.created") {
    await convex.mutation(internal.users.upsertFromClerk, {
      clerkId: evt.data.id,
      email: evt.data.email_addresses[0]?.email_address,
      name: `${evt.data.first_name ?? ""} ${evt.data.last_name ?? ""}`.trim() || undefined,
      imageUrl: evt.data.image_url,
    });
  }

  return new Response("ok");
}
```

### Env vars

```
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_xxx
CLERK_SECRET_KEY=sk_test_xxx
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
CLERK_WEBHOOK_SECRET=whsec_xxx          # se webhook user sync
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/dashboard
```

### Pricing 2026

- **Free**: 10k MAU
- **Pro**: $25/mo + $0.02/MAU oltre 10k
- **Add-on**: SSO Enterprise, multi-tenant orgs

## WorkOS (enterprise SSO)

### Setup AuthKit

```bash
npm install @workos-inc/authkit-nextjs
```

### Provider setup

```typescript
// middleware.ts
import { authkitMiddleware } from "@workos-inc/authkit-nextjs";

export default authkitMiddleware({
  middlewareAuth: {
    enabled: true,
    unauthenticatedPaths: ["/", "/sign-in"],
  },
});
```

```typescript
// app/sign-in/page.tsx
import { getSignInUrl } from "@workos-inc/authkit-nextjs";

export default async function SignIn() {
  const url = await getSignInUrl();
  return <a href={url}>Sign in</a>;
}
```

### Env vars

```
WORKOS_API_KEY=sk_xxx
WORKOS_CLIENT_ID=client_xxx
WORKOS_COOKIE_PASSWORD=                 # 32+ char random
NEXT_PUBLIC_WORKOS_REDIRECT_URI=https://app.example.com/callback
```

### Quando usarlo

- B2B con AD/Okta/Google Workspace
- SAML/SCIM directory sync requirement
- Compliance enterprise (SOC2, HIPAA)

### Pricing

- Per-organization usage
- Audience B2B grande, NOT consumer

## NextAuth.js / Auth.js v5 (custom adapter pattern)

### Setup minimo

```bash
npm install next-auth@beta
```

```typescript
// auth.ts
import NextAuth from "next-auth";
import GitHub from "next-auth/providers/github";
import Google from "next-auth/providers/google";

export const { handlers, signIn, signOut, auth } = NextAuth({
  providers: [GitHub, Google],
});
```

```typescript
// app/api/auth/[...nextauth]/route.ts
export { GET, POST } from "@/auth";
```

### Quando usarlo

- Budget zero
- Custom flows (es. magic link senza Clerk)
- Data residency requirement
- Già fatto in progetti precedenti

## Custom adapter (Q5 = "Già ho provider")

Pattern: scaffold base + lascia integrazione utente.

```typescript
// lib/auth/custom-adapter.ts
export async function getCurrentUser(req: Request): Promise<User | null> {
  // TODO: implement based on your auth provider
  // Examples:
  // - Auth0: verify JWT from Authorization header via auth0 SDK
  // - Firebase Auth: verify Firebase ID token
  // - Custom: validate session cookie via DB lookup
  throw new Error("Not implemented — implement custom auth here");
}
```

## Decisione matrix

| Use case | Provider | Reason |
|---|---|---|
| Consumer SaaS / internal tool | **Clerk** ⭐ | Best DX, free 10k MAU, native Convex |
| Enterprise SSO required | WorkOS | SAML/SCIM, AD/Okta integration |
| Budget zero + custom flows | NextAuth.js | Free, full control |
| Già su Supabase | Supabase Auth | Bundled, RLS native |
| Magic link only | NextAuth.js | Custom email provider |

## Anti-patterns

- **JWT manuale custom**: anti-pattern (security fragile, maintenance costante). Use Clerk.
- **Auth in localStorage**: vulnerabilità XSS. Use httpOnly cookies (Clerk default).
- **Password storing custom**: anti-pattern. Use provider che gestisce hashing (Clerk, NextAuth).

## Sources

- [stack.convex.dev — Authentication Best Practices Convex+Clerk+Next.js](https://stack.convex.dev/authentication-best-practices-convex-clerk-and-nextjs)
- [Clerk — Complete Authentication Guide for Next.js App Router](https://clerk.com/articles/complete-authentication-guide-for-nextjs-app-router)
- [WorkOS blog — Building auth in Next.js App Router 2026](https://workos.com/blog/nextjs-app-router-authentication-guide-2026)
