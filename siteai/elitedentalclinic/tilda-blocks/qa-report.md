# Elite Dental Clinic — Tilda integration QA

Reference: `../index.html` at commit `6a7de21f6e8da40fda18cda010f51d875afc14f8` (blob `70027309b8180a38440a9c7ef70637ecb8dca9cc`). The current `main` has the same index blob.

Test page: [https://elitedentalclinic.kz/elite-t123-test-20261127](https://elitedentalclinic.kz/elite-t123-test-20261127), project `18871146`, page `423958103`. It has `noindex,nofollow`, disables the project's header, and does not replace the home page. Its 21 ordered T123 record IDs are in `tilda-records.json`. The production page `101021436` still has its pre-work changed/published timestamps (`1795542724` / `1795542742`).

## Visual and content checks

- Chromium / Playwright, device pixel ratio 1, reduced motion, same 14 widths: 320, 360, 375, 390, 430, 768, 1024, 1280, 1366, 1440, 1580, 1600, 1920, 2560 px.
- Full-page and 18 section screenshots: 266 PNGs for the reference and 266 for the final Tilda page. Local evidence: `/workspace/scratch/elite-tilda-audit/reference/` and `/workspace/scratch/elite-tilda-audit/tilda-final/`. Eight enhanced difference PNGs: `/workspace/scratch/elite-tilda-audit/diffs/`.
- Every section's x/y/width/height matches the reference at all 14 widths. No broken visible images, JavaScript page errors, or horizontal overflow. The approved source has 13 px overflow at 320 px; the Tilda page removes it with a 320 px only arrow offset.
- At 390 and 1440 px, the header and quiz screenshots are pixel-identical; hero average RGB difference is 0.438 and 0.400 levels respectively (on a 0–255 scale), due to CDN recompression. Text and image alt attributes match in all 18 sections; heading sequences match (H1: 1, H2: 17, H3: 42).
- All 25 uploaded local WebP images return HTTP 200 and retain their pixel dimensions. Tilda recompressed 24 of them; one is byte-identical. Existing remote images already use Tilda CDN.

## Function and SEO checks

- `functional_audit.py` passed the same 24 checks on source and Tilda at 390 and 1600 px: navigation and unique IDs, sticky header, burger and Escape, booking phone and consent validation, carousels, modals, gnathology choices, before/after range, five quiz steps, all 12 doctor profiles, contact links and map. WhatsApp navigations were intercepted before the service; no message was sent. Reports: `/workspace/scratch/elite-tilda-audit/functional-source.json` and `functional-tilda-final.json`.
- Published HEAD has one each of title, description, canonical, OG tags and JSON-LD; `robots` is `noindex,nofollow`. The test URL is absent from both the custom domain and Tilda sitemap. The source title/description and Dentist, WebSite, WebPage, OfferCatalog graph are present. `schema_audit.py` validated JSON syntax, Schema.org types/properties and cross references against the official current Schema.org vocabulary: 0 errors. Report: `/workspace/scratch/elite-tilda-audit/schema-validation.json`. The public Schema.org validator returned HTTP 429; a third-party CLI had a packaging error, so neither was used as evidence.
- Lighthouse 13.6.0 on the published test page: mobile **64 performance / 97 accessibility / 100 best practices / 61 SEO**; desktop **62 / 97 / 100 / 61**. JSON reports are in `/workspace/scratch/elite-tilda-audit/`. SEO is intentionally reduced by `noindex` and the canonical pointing to the production home page; color contrast is an inherited source design issue. Desktop and mobile scores can vary between runs.
- Playwright WebKit could not launch because this execution host lacks GTK 4 and other system libraries. Safari-specific behavior remains unverified.

## Tilda compatibility adjustments

The upload copies use Arial because the standalone source has no TildaSans font file and renders the Arial fallback, while the Tilda project loads TildaSans. Tilda resets two quiz paragraph margins; the upload CSS restores their browser-default spacing. The T123 wrapper for the header is pinned for sticky behavior. A short upload script moves independent content records under one semantic `<main>` at runtime. These changes preserve tested layout coordinates and leave each section independently editable.

The current page is for review. No production page was edited or published.
