---

name: web-dev-ops
description: >
  Operate web development projects end-to-end: audit local development sites for
  structure, content, and expansion opportunities; deploy paired static
  editorial publications and interactive SPAs under a single domain umbrella.
  Covers port discovery, browser inspection, source analysis, GitHub Pages
  static export, Vite subpath deployment, and SPA client-side routing fixes.
  version: 1.0.0 author: Hermes Agent license: MIT metadata: tags: [web-dev,
  localhost, audit, deployment, github-pages, static-export, spa, vite, nextjs]
  tier: task-specific domain: software-development color: blue prerequisites:
  commands: [lsof, ps, grep, curl]
metadata:
  tags: [web, audit, dev-server, e2e]
  tier: task-specific
  domain: product
when_to_apply: >
  When operating a web dev project end-to-end: audit dev sites and validate.
---
# Web Development Operations

## Identity

A web-dev operator who both inspects and deploys. Capable of tracing a local dev server to its source, auditing rendered output and generation pipelines, and shipping paired static + interactive artifacts to production.

## When to Use

- User provides a `localhost:PORT` or `127.0.0.1:PORT` and wants an audit
- Evaluating a generative art project, editorial site, tool, or prototype running locally
- Deploying a static content site AND a separate interactive app under the same domain
- Fixing SPA 404 errors on GitHub Pages after direct URL access
- Building a Next.js static export that embeds a pre-built Vite/React app

## When NOT to Use

- Production/public websites without a local dev server → use `web_extract` or browser tools
- Complex authentication flows → use `browser-automation-patterns`
- Pure API endpoints → use curl/HTTP tools
- Large-scale CDN or cloud deployment → use infrastructure-specific skills

## Local Development Site Audit

### Core Mission

Produce comprehensive audit reports covering:
1. Runtime architecture (what's serving, where's the source)
2. Content structure (sections, navigation, assets)
3. Design quality (typography, layout, visual hierarchy)
4. Technical system (build tools, generation pipeline, output formats)
5. Expansion opportunities (ranked by effort/impact)

### Discovery Phase

1. Verify port is active: `lsof -i :PORT`
2. Identify process: PID, command name, arguments
3. Locate source directory: `lsof -p PID | grep cwd`
4. List source files: find HTML, JS, CSS, generators, config files
5. Identify server type: Python http.server, Node dev server, Vite, etc.

### Browser + Source Cross-Reference

- Navigate with `browser_navigate`, scroll all sections, extract images with `browser_get_images`
- Read main entry files (index.html, app.js) and generation scripts
- Check asset directories for scope (count files, note naming patterns)
- Look for configuration files (manifest.json, package.json)

### Deliverables

- Port-to-source trace showing how you located the codebase
- Asset inventory with counts and categories
- Architecture summary (generation pipeline + render method)
- Expansion roadmap with 4-7 concrete, ranked options
- Targeted questions to guide next phase

**Full details:** See `references/local-dev-audit/SKILL-archive.md`.

## Static Editorial + Interactive App Deployment

### Core Pattern

Two artifacts, one umbrella:

| Artifact | Purpose | Technology | Path |
|----------|---------|------------|------|
| **Editorial** | Static publication, long-form content | HTML/CSS or Next.js static | `/project/` |
| **Interactive App** | Dynamic tool, generator, explorer | React/Vite/Vue | `/project/app/` |

They link to each other but remain separate codebases. Do not merge them.

### GitHub Pages + Next.js Static Export

When using Next.js with `output: "export"`:

```typescript
const nextConfig = {
  output: "export",
  trailingSlash: true,
  images: { unoptimized: true },
};
```

**The `public/` directory trick:**

Build the Vite app with the correct `base` path, then copy `dist/*` into `nextjs-site/public/project/app/`. Next.js build copies these to `out/project/app/`.

### SPA Client-Side Routing Fix

React apps with client-side routing fail on direct URL access because GitHub Pages returns 404. The solution uses two pieces:

1. **Root redirect script** in `not-found.tsx` or `404.html` — detects `/project/app/` prefix, redirects to `/?_p=/route`
2. **SPA redirect handler** in React app — reads `_p` param and navigates to the real route

**Full details:** See `references/static-interactive-app/SKILL-archive.md` and `references/static-interactive-app/spa-github-pages-routing.md`.

## Pitfalls

- **Always locate source first** — Use `lsof -i :PORT` to find PID, then `lsof -p PID` to find CWD.
- **Cross-reference browser + filesystem** — Browser shows rendered state; filesystem shows generation logic.
- **Do not merge editorial and app** — Ask: "Is this a publication or a platform?" If both, use the paired pattern.
- **Vite base path** — Must match the subfolder in `public/`. Wrong base = 404 or blank page.
- **GitHub Pages delay** — Changes to `public/` require full rebuild and 30-60s propagation.
- **Forgetting SPA routing** — Direct links to `/app/pattern/xyz` will 404 without the redirect script.
- **Wrong file location** — Files must go in `public/project/app/`, NOT repo root.
- **Next.js `out/` vs root sync** — With `output: "export"`, built pages land in `out/`. If the deploy workflow serves from repo root, you must copy `out/blog/*` to `blog/` and sync `feed.xml`/`sitemap.xml` or routes 404. See `references/nextjs-static-export-root-sync.md`.

## Directory Structure

```
~/.hermes/skills/software-development/web-dev-ops/
├── SKILL.md
└── references/
    ├── local-dev-audit/
    │   ├── SKILL-archive.md
    │   └── live-site-infrastructure-reconnaissance.md
    └── static-interactive-app/
        ├── SKILL-archive.md
        ├── spa-github-pages-routing.md
        └── tartanism-deployment-example.md
```

## References

- `references/local-dev-audit/SKILL-archive.md` — Full archived skill: port discovery, browser inspection, source analysis, generative art / editorial / tool patterns
- `references/local-dev-audit/live-site-infrastructure-reconnaissance.md` — Production website audit via DNS, HTTP, and sitemap analysis
- `references/static-interactive-app/SKILL-archive.md` — Full archived skill: paired artifact deployment, Next.js static export, Vite subpath config, build workflow
- `references/static-interactive-app/spa-github-pages-routing.md` — Client-side routing fix for SPAs on GitHub Pages
- `references/static-interactive-app/tartanism-deployment-example.md` — Complete case study (Tartanism, May 2026)
