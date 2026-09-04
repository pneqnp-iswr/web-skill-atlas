---
name: qrafig-site
description: Work on the QRAFIG public marketing site — a separate Next.js 16 / React 19 / Tailwind 4 repository that shares nothing with the platform but brand values. Covers the App Router static export, locale negotiation in proxy.ts (renamed from middleware.ts in Next 16), type-checked dictionaries where a missing translation fails the build, the typed Route union, brand tokens copied by value from the desktop theme, pricing arithmetic held in the repository, the content truth check, and the Cloudflare Pages headers and redirects. Use only for site work — never load platform, POS, finance or database skills for it.
when_to_use: The marketing site: pages, copy, translations, pricing configurator, metadata and SEO, motion and scroll scenes, accessibility, styling tokens, build and deployment. Repository pneqnp-iswr/Site-QRAFIG.
---

# The QRAFIG site

**A separate repository** (`pneqnp-iswr/Site-QRAFIG`, package name `qrafig-site`). It shares **nothing**
with the platform except brand values: no import across the boundary, no shared build, no reference to
any `.csproj`, and **no API call to the platform**.

> Routing note: a site task loads **this skill and nothing else**. Do not pull in POS, Finance,
> SQLite, EF Core, WPF or any other QRAFIG platform skill.

## Read first

- `package.json`, `next.config.ts`, `tsconfig.json`, `eslint.config.mjs` — the versions and the
  rendering mode, every time.
- `AGENTS.md` — including its generated `nextjs-agent-rules` block.
- `node_modules/next/dist/docs/` — the installed Next.js documentation, which is authoritative.
- `README.md` and `ARCHITECTURE.md` — useful, and known to lag the tree; verify against files.
- `src/i18n/config.ts`, `src/lib/site.ts`, `src/content/`, `src/app/globals.css`, `src/proxy.ts`.
- `scripts/check-content.mjs`, `public/_headers`, `public/_redirects`,
  `.github/workflows/static-export-check.yml`.

## Verify the stack from the repository, every time

Read `package.json` and `next.config.ts` before writing code. At the time of writing:
Next.js 16, React 19, Tailwind CSS 4 (`@tailwindcss/postcss`), TypeScript 5 `strict`, `motion` for
animation, ESLint 9 with `eslint-config-next`, `wrangler` and `@opennextjs/cloudflare` present as
dependencies, and `next.config.ts` set to **`output: "export"`** with `images.unoptimized`.

**This is not the Next.js in your training data.** The repository's `AGENTS.md` carries a generated
block saying so, and it is right: read the relevant guide under
**`node_modules/next/dist/docs/`** (resolved from the repo root) before writing code, and heed
deprecation notices.

That generated block is **written and re-added by `next dev`** — it regenerates from
`node_modules/next/dist/server/lib/generate-agent-files.js`. Removing it from a diff only re-creates
the uncommitted change; commit it with your work. **Do not delete it.** `CLAUDE.md` is a one-line
`@AGENTS.md` include — keep it that way.

## Known documentation divergences — trust the tree

- `README.md` and `ARCHITECTURE.md` say locale negotiation lives in `src/middleware.ts`. **The file is
  `src/proxy.ts`** — Next.js 16 renamed it. Verify against the tree, not the prose.
- With `output: "export"` there is **no server at run time**, so `proxy.ts` does not execute in the
  deployed build; the bare-URL redirect is served by **`public/_redirects`** (`/ /ru 302`) on
  Cloudflare Pages. Keep the two consistent — the local `next dev` behaviour and the deployed
  behaviour come from different files.
- `@opennextjs/cloudflare` is a dependency but no script uses it, and the CI workflow builds the
  static export. Do not assume an OpenNext deployment path exists until a script or workflow says so.
- `npm start` (`next start`) is not meaningful for a static export; serve `out/` instead.

## The rules that will fail your build if you break them

**Copy lives in `src/i18n/dictionaries/<locale>/`.** `ru/` defines the shape; each `az/` and `en/`
part file is declared `satisfies Dictionary["…"]`, so a key added to one language and forgotten in
another **fails the build**, pointing at the page missing it. Locales are `ru`, `az`, `en`, default
`ru`; adding `kk` or `uz` is one directory plus an entry in `src/i18n/config.ts` and
`dictionaries/index.ts`.

**Every address is typed.** `Route` in `src/lib/site.ts` is a union of the addresses the site actually
serves, built from the module and pack catalogues. `path(locale, "/platform/pso")` does not compile.

**Colours are never literals.** Every surface, border, text and accent value is a token in
`src/app/globals.css`, copied **by value** from the desktop application's `Theme/Tokens.Dark.xaml`.
Change a token and the site, the product mocks and the charts move together. Never inline a hex.

**Module states are not aspirational.** `src/content/modules.ts` marks each module `live`, `building`
or `planned` **from `docs/implementation-status.md` in the platform repository**, and the module pages,
the platform page, the mega menu and the comparison table all read that one record. Before changing a
state, read the platform ledger's completion criteria and the `## SITE-SYNC FACTS — <MODULE>` block —
those blocks exist to be copied from, and they are data rather than copy: no adjectives, no claims
beyond what the ledger proves.

**Prices are not fetched, and not rounded.** `src/content/pricing.ts` holds the same **minor-unit**
amounts the platform's `PlanService` seeds, for `AZN` and `USD`. `RUB` is a listing price that exists
**only in this file so far** and must be added to the platform seed before roubles can be charged.
Yearly is ten months for twelve on the subscription; recurring add-ons are billed twelve times, and the
configurator shows both lines separately rather than blending them.

**Numerals agree with their nouns** — `src/lib/plural.ts` and the `[one, few, many]` form in each
dictionary. A slider reading "1 точек" is a slider nobody trusts with their money.

**The legal documents are drafts** while `registration.entity` in `src/lib/site.ts` is `null`: the four
legal pages carry a visible notice, render registration details as marked tokens rather than invented
values, and are served `noindex` and left out of the sitemap. Filling in `registration` turns all of
that off at once.

## Rendering model

Every page is a **Server Component** and every route is statically generated for all three locales via
`generateStaticParams`. Copy is read on the server and passed down as props — there is **no i18n
runtime, no context provider, and no dictionary in the client bundle** beyond the strings a client
component is handed. Client components exist only where there is genuine interaction: the header, the
route progress bar, the scroll scenes, the price configurator and calculator, the FAQ accordions, and
the contact and notify forms.

Deliberately **not** used: a smooth-scroll hijacker (Lenis/Locomotive), WebGL, a component library, or
an icon package. Each costs more in bytes, input latency and accessibility than it returns.

## Verification

```bash
npm ci
npx tsc --noEmit            # dictionaries agree, routes exist, props line up
npx eslint .                # zero warnings expected
node scripts/check-content.mjs   # the content truth check
npm run build               # the static export
test -d out && test -f out/ru.html && test -f out/_headers && test -f out/_redirects
```

`scripts/check-content.mjs` is a **content truth check**: it transpiles and loads the content modules
and asserts things prose cannot enforce — that the release channel stays `private-alpha`, that the
yearly plan price is exactly ten monthly charges, that `az` renders `html lang="az-AZ"`, that the
contact forms keep their honeypot, timing guard and aggregate rate limit, and that abuse protection
**does not retain or key on visitor IP addresses**. Run it after any content, pricing or form change.

The GitHub workflow `static-export-check.yml` runs `npm ci` and `npm run build` on Node 22 and verifies
the export artefacts.

After a large change, also crawl the sitemap and confirm every internal link answers 200, and confirm
no currency symbol or untranslated string leaked into the wrong locale. Both are about fifty lines of
`fetch` against `npm run dev`; neither needs a test framework.

## Deployment surface

`public/_headers` carries the Cloudflare Pages response headers, including a strict CSP
(`default-src 'self'`, no external origins), `Referrer-Policy`, `X-Content-Type-Options`,
`X-Frame-Options: DENY`, a `Permissions-Policy`, and immutable caching for `/_next/static/*`.
`public/_redirects` carries `/ /ru 302`. **Adding an external script, font or image source means
changing the CSP** — check it whenever you add a third-party anything. Fonts are `next/font/google`,
self-hosted, so there are zero external requests today; keep it that way.

Environment: `NEXT_PUBLIC_SITE_URL` (canonical origin for metadata, `hreflang` and the sitemap;
defaults to `https://qrafig.com`) and `CONTACT_ENDPOINT`. With `CONTACT_ENDPOINT` unset the forms say
the form is not wired up and hand the visitor a pre-written email **in their own language** — they
never show a tick for a message that went nowhere. Preserve that.

## Do not

- Do not claim a module is shipped ahead of `docs/implementation-status.md`.
- Do not invent a price, a rate or a registration detail.
- Do not inline a colour, or add a token to only one place.
- Do not add a locale without completing its dictionary.
- Do not delete or hand-edit the generated `nextjs-agent-rules` block in `AGENTS.md`.
- Do not add an external script, font or analytics origin without updating the CSP.
- Do not add a runtime dependency on the platform API.
- Do not write from training memory about Next.js — read `node_modules/next/dist/docs/`.
- Do not fix a documentation/tree divergence by changing the code to match the prose.

## Related skills

None from the platform. Reference this skill alone for site work.
External Next.js / React / Cloudflare skills: `docs/ai/sources.md`.
