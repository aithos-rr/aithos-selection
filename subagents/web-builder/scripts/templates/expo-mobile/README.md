# expo-mobile — Stub v1 (v2 scope)

Template Expo + Convex per app mobile native iOS/Android. **NON ancora pienamente implementato** in v1 di `/web-builder`.

## Stato v1: PLACEHOLDER

Audience Learnn (founder/marketer/freelancer non-dev) ha use case mobile native <5%. Per v1 abbiamo deciso di non includere full Expo template per evitare friction (richiede Xcode/Android Studio, simulator/device, app store account).

## Workaround MVP mobile

### Opzione 1 — una piattaforma no-code mobile-first responsive

Usa una piattaforma no-code per creare web app mobile-friendly (responsive). Ottimo per MVP che non richiede native features.

```bash
# Genera scaffold solo backend + CLAUDE.md
/web-builder
# Q1: Mobile app
# Q3: una piattaforma no-code mobile-via-web
```

### Opzione 2 — PWA con Next.js

Aggiungi service worker + manifest a un progetto Next.js per PWA installabile da mobile browser:

```bash
/web-builder
# Q1: SaaS micro
# Aggiungi: next-pwa package post-scaffold
```

## Roadmap v2

In v2 di `/web-builder` (Q3 2026 stimato):

- Scaffold Expo + Convex completo
- Native auth Clerk Expo
- EAS Build setup automatico
- Push notifications via Convex Action
- App store deploy automation (TestFlight + Google Play)

## Reference

- [`tech-stack-2026/SKILL.md`](file://~/.claude/skills/tech-stack-2026/SKILL.md) sezione Expo
- [docs.expo.dev](https://docs.expo.dev) — Expo docs ufficiali
- [docs.convex.dev/quickstarts/react-native](https://docs.convex.dev/quickstarts/react-native) — Convex + Expo

## Per ora

Se Filippo o utente seleziona Q1=Mobile, lo scaffolder mostra questo README + suggerisce Opzione 1 o 2 sopra. Non genera scaffold Expo completo.
