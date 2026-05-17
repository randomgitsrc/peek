# PeekView Frontend v3

Vue 3 + Vite + TypeScript SPA for PeekView with Shiki code highlighting, Markdown rendering, and Mermaid diagrams.

## Features

- **Code Viewer**: Shiki syntax highlighting, line numbers, wrap mode, URL hash linking
- **Markdown**: GitHub-style rendering with TOC navigation, code block copy
- **Mermaid**: Diagram rendering with fullscreen, code/diagram toggle, resize
- **Responsive**: Desktop 3-column layout, mobile drawer navigation + bottom bar
- **Themes**: Dark/light mode with system preference detection, FOUC prevention
- **Auth**: JWT login/register, private entries, owner actions (visibility toggle, delete)
- **API Keys**: Management page at `/settings/apikeys` (create, revoke, copy)
- **All/Mine Tabs**: Filter entries by ownership

## Development

```bash
npm install
npm run dev          # http://localhost:5173 (proxies API to :8080)
```

## Build

```bash
npm run build        # Output to dist/, auto-copies to backend/peekview/static/
```

## Testing

```bash
npm run test         # Vitest unit tests
npm run test:e2e     # Playwright E2E tests (requires debug server)
```

## Important Notes

- Router file is `src/router.ts` (NOT `src/router/index.ts`)
- Adding routes: always modify `src/router.ts`, then rebuild
- After frontend changes, run `npm run build` to update backend static files
