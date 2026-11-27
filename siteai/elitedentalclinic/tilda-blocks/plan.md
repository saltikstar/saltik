# Elite Dental Clinic — Tilda migration plan

Source: `../index.html` at commit `6a7de21f6e8da40fda18cda010f51d875afc14f8`, Git blob `70027309b8180a38440a9c7ef70637ecb8dca9cc`. The current `main` has the same blob. No historical standalone block is a design source.

## Source audit

- Local HTTP reference: `http://127.0.0.1:8765/index.html`.
- Browser: Chromium via Playwright, DPR 1, reduced motion, fonts and images loaded. Screenshots and geometry at 320, 360, 375, 390, 430, 768, 1024, 1280, 1366, 1440, 1580, 1600, 1920, 2560 px: `/workspace/scratch/elite-tilda-audit/reference/`.
- Source: 18 visible content sections, one booking dialog, 45 head style tags, 10 body scripts, 90 image elements (85 distinct `src` values), 24 local asset files, two forms that prepare WhatsApp drafts rather than submitting to a backend.
- Source itself has 13 px horizontal overflow at 320 px, caused by the promotions arrows. The Tilda upload copy shifts those arrows left 14 px only at 320 px; section geometry stays unchanged and horizontal overflow is 0.
- Original `index.html` has `noindex,nofollow`; the test page must also be noindex. Production home page is Tilda page 101021436 and must not be modified.

## Target

Project: 18871146, existing custom domain `elitedentalclinic.kz`. Use a new test page with a distinct alias, no search indexing and `noheader` so project header page 305064603 is not duplicated. Do not set it as the project home page. Do not change project-wide head code, fonts, footer or analytics: the project already has TildaSans, GTM and a Yandex Metrika ID. Publish only the noindex test page after the first parity gate; never publish the production page.

Mode: separate T123 (`tplid=131`) for each meaningful section, plus invisible T123 blocks for global styles and common scripts. `edit_record` on an existing T123 confirms that its `code` field accepts HTML code. Read this field on every newly created block before writing with `update_record`.

## Block order

| # | File | Source element | Notes |
|---:|---|---|---|
| 0 | 00-global.html | original head styles | Preserve order; duplicate parent selectors through `:is()` for split sections. |
| 1 | 01-header.html | skip link + `#edc-site-header` | Tilda wrapper may require sticky positioning adjustment only after geometry checks. |
| 2 | 02-hero.html | `#edc-gnathology-hero` | Keep `#edc-main` skip target once. |
| 3 | 03-promos.html | `#edc-promos` | Carousel and modal. |
| 4 | 04-benefits.html | `#edc-next .edv-why` | Retain `#edc-next` on this block's wrapper. |
| 5 | 05-services.html | `#edc-next .edv-services` | New wrapper `#edc-services-root`; same ID specificity in CSS. |
| 6 | 06-gnathology.html | `.edgn-section--treat` | Retain `#edc-gnathology-next` on this block's wrapper. |
| 7 | 07-braces.html | `.edo-section` | New unique wrapper, original shared CSS variables. |
| 8 | 08-before-after.html | `#edc-before-after` | New unique wrapper; original child ID retained. |
| 9 | 09-implantation.html | `.edx-implant` | New unique wrapper. |
| 10 | 10-implant-process.html | `#edc-implant-process` | New unique wrapper. |
| 11 | 11-surgery.html | `#edc-surgery` | New unique wrapper. |
| 12 | 12-quiz.html | `#edc-quiz` | WhatsApp draft only. |
| 13 | 13-cases.html | `#edc-cases` | Gallery and modal. |
| 14 | 14-about.html | `#edc-about-editorial` | Keep all five training photos. |
| 15 | 15-team.html | `#edc-team-editorial` | Team photo. |
| 16 | 16-doctors.html | `#edc-doctors` | Twelve doctor profiles and carousel. |
| 17 | 17-reviews.html | `#edc-reviews` | Carousel and modal. |
| 18 | 18-contacts.html | `#edc-contacts` | Map, address and telephone. |
| 19 | 19-booking.html | `#edc-booking` | Dialog with form; WhatsApp draft only. |
| 20 | 20-scripts.html | original body scripts | Preserve their order and IDs, after all markup. |
| head | head-seo.html | source meta and JSON-LD | Tilda page settings own title/description/noindex; avoid duplicate automatically generated tags. |

No HTML tag may open in one T123 and close in another. `#edc-next` and `#edc-gnathology-next` occur once each; cloned wrappers get new IDs, with their original CSS selectors expanded using `:is()` (same specificity). All other original IDs occur once. CSS and JS must remain in source order. No standard Tilda block spacing.

## Behaviour inventory

| Area | Trigger and state | Check |
|---|---|---|
| Header | sticky scroll, desktop nav, burger, skip link, anchors | geometry, mouse, touch, keyboard |
| Promotions | prev/next/dots, open/close modal, Escape | cards, focus, modal image |
| Before/after | carousel, range slider | mouse drag and touch |
| Gnathology | radio-based interactive scheme | all choices, keyboard |
| Surgery | image modal, arrows, Escape | photos and focus |
| Quiz | step selection, back/next, draft message | no real submission |
| Cases | carousel, modal and controls | photos and focus |
| Doctors | carousel and card links | all twelve profiles |
| Reviews | carousel and modal | screenshots and focus |
| Booking | dialog, phone validation, agreement, WhatsApp draft | do not send to clinic |
| Motion | reveal effects and reduced-motion state | consistent scroll and first load |
| Contact | 2GIS map, telephone and WhatsApp links | link targets and resource availability |

## Files and head

Upload original images to the project's Tilda CDN and replace relative image references with returned CDN URLs before putting code on the test page. Keep a source URL to CDN URL map. Tilda's CDN recompressed 24 of 25 WebP files but retained all dimensions; this is a known visual difference. No original video, font file or backend API is present. The approved standalone source renders Arial because it does not load TildaSans; the Tilda upload copy explicitly uses Arial because the project loads TildaSans. Keep the source meta title, description, heading structure, alt text, ru-KZ language and schema data. For the test page, keep noindex; do not duplicate Tilda's title, description or canonical tags. The existing project GTM is not changed.

Tilda test page: `423958103`, [published preview](https://elitedentalclinic.kz/elite-t123-test-20261127), 21 T123 records in `tilda-records.json`. The header record itself is sticky because a sticky descendant is constrained by its T123 wrapper. Tilda also resets paragraph margins in the quiz; upload CSS restores the source margins. The upload script creates a single `<main>` landmark around the independent content records without splitting markup between blocks.

## Gates

1. Generate all 22 files and assemble them locally with original assets; verify unique IDs, source text/image parity and HTML balance.
2. Compare local modular page with the reference at all 14 widths, including section geometry, computed styles and screenshots. Fix differences before upload.
3. Create the separate noindex Tilda page; upload header, hero and shared styles first. Check their saved code and Tilda rendering before other sections.
4. Continue the remaining sections only after the first parity gate. Check all interactions, SEO, resources, no horizontal scroll and console. Keep production untouched.
