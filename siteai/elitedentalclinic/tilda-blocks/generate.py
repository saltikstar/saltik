"""Extract the approved index.html into independent T123 records without retyping it."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "index.html"
MANIFEST = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
OUT = ROOT / "generated"
OUT.mkdir(exist_ok=True)

raw = SOURCE.read_bytes()
blob = hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()
if blob != MANIFEST["sourceBlob"]:
    raise ValueError(f"Reference changed: expected {MANIFEST['sourceBlob']}, got {blob}")

source = raw.decode("utf-8")
head = re.search(r"<head>(.*?)</head>", source, re.S).group(1)
body = re.search(r"<body[^>]*>(.*?)</body>", source, re.S).group(1)


def extract(tag: str, *, element_id: str | None = None, class_name: str | None = None) -> str:
    """Return an element's exact source markup, without reserializing HTML."""
    if (element_id is None) == (class_name is None):
        raise ValueError("Specify exactly one selector")
    for match in re.finditer(rf"<{tag}\b[^>]*>", body, re.I):
        token = match.group()
        if element_id and not re.search(rf'\bid="{re.escape(element_id)}"', token):
            continue
        if class_name and not re.search(rf'\bclass="[^"]*\b{re.escape(class_name)}\b', token):
            continue
        depth = 0
        for close in re.finditer(rf"</?{tag}\b[^>]*>", body[match.start():], re.I):
            depth += -1 if close.group().startswith("</") else 1
            if depth == 0:
                return body[match.start():match.start() + close.end()]
        break
    raise ValueError(f"Missing {tag} {element_id or class_name}")


def strip_scripts(fragment: str) -> str:
    return re.sub(r"<script\b[^>]*>.*?</script>", "", fragment, flags=re.S | re.I)


GNATHOLOGY_CLONES = (
    "edc-braces-root",
    "edc-before-after-root",
    "edc-implantation-root",
    "edc-implant-process-root",
    "edc-surgery-root",
)


def expand_parent_selectors(text: str) -> str:
    # :is() preserves the ID specificity and order of original CSS selectors.
    text = text.replace("#edc-next", ":is(#edc-next,#edc-services-root)")
    text = text.replace(
        "#edc-gnathology-next",
        ":is(#edc-gnathology-next," + ",".join("#" + root for root in GNATHOLOGY_CLONES) + ")",
    )
    return text


def gnathology_wrapper(root_id: str, content: str) -> str:
    return (
        f'<section id="{root_id}" aria-label="Раздел гнатологии">'
        f'<div class="edgn-wrap">{strip_scripts(content)}</div></section>'
    )


sections = [
    ("01-header.html", extract("a", class_name="edc-skip-link") + "\n" + extract("header", element_id="edc-site-header")),
    ("02-hero.html", '<div id="edc-main" tabindex="-1"></div>' + extract("section", element_id="edc-gnathology-hero")),
    ("03-promos.html", strip_scripts(extract("section", element_id="edc-promos"))),
    ("04-benefits.html", '<div id="edc-next">' + extract("section", class_name="edv-why") + "</div>"),
    ("05-services.html", '<div id="edc-services-root">' + extract("section", class_name="edv-services") + "</div>"),
    ("06-gnathology.html", gnathology_wrapper("edc-gnathology-next", extract("section", class_name="edgn-section--treat"))),
    ("07-braces.html", gnathology_wrapper("edc-braces-root", extract("section", class_name="edo-section"))),
    ("08-before-after.html", gnathology_wrapper("edc-before-after-root", extract("section", element_id="edc-before-after"))),
    ("09-implantation.html", gnathology_wrapper("edc-implantation-root", extract("section", class_name="edx-implant"))),
    ("10-implant-process.html", gnathology_wrapper("edc-implant-process-root", extract("section", element_id="edc-implant-process"))),
    ("11-surgery.html", gnathology_wrapper("edc-surgery-root", extract("section", element_id="edc-surgery"))),
    ("12-quiz.html", strip_scripts(extract("section", element_id="edc-quiz"))),
    ("13-cases.html", strip_scripts(extract("section", element_id="edc-cases"))),
    ("14-about.html", strip_scripts(extract("section", element_id="edc-about-editorial"))),
    ("15-team.html", strip_scripts(extract("section", element_id="edc-team-editorial"))),
    ("16-doctors.html", strip_scripts(extract("section", element_id="edc-doctors"))),
    ("17-reviews.html", strip_scripts(extract("section", element_id="edc-reviews"))),
    ("18-contacts.html", strip_scripts(extract("section", element_id="edc-contacts"))),
    ("19-booking.html", strip_scripts(extract("dialog", element_id="edc-booking"))),
]

styles = re.findall(r"<style\b[^>]*>.*?</style>", head, re.S | re.I)
scripts = re.findall(r"<script\b[^>]*>.*?</script>", body, re.S | re.I)
if len(styles) != 45 or len(scripts) != 10:
    raise ValueError(f"Unexpected source: {len(styles)} styles, {len(scripts)} body scripts")

meta = re.findall(r"<(?:meta|link)\b[^>]*>", head, re.I)
seo = [tag for tag in meta if re.search(r'name="description"|rel="canonical"|property="og:|name="twitter:', tag)]
seo += re.findall(r'<script type="application/ld\+json"[^>]*>.*?</script>', head, re.S | re.I)

all_files = [
    ("00-global.html", expand_parent_selectors("\n".join(styles)) +
     '\n<style id="edc-tilda-320-overflow-fix">@media(max-width:320px){#edc-promos .edcp-arrows{transform:translateX(-14px)}}</style>'),
    *sections,
    ("20-scripts.html", expand_parent_selectors("\n".join(scripts))),
    ("head-seo.html", "\n".join(seo)),
]
for stale in OUT.glob("*.html"):
    stale.unlink()
for name, content in all_files:
    (OUT / name).write_text(content + "\n", encoding="utf-8")

page_markup = "\n".join(content for _, content in sections)
ids = re.findall(r'\bid="([^"]+)"', page_markup)
if len(ids) != len(set(ids)):
    raise ValueError("Duplicate IDs: " + str([x for x in ids if ids.count(x) > 1]))
source_images = re.findall(r'<img\b[^>]*\bsrc="([^"]*)"', body, re.S | re.I)
generated_images = re.findall(r'<img\b[^>]*\bsrc="([^"]*)"', page_markup, re.S | re.I)
if sorted(source_images) != sorted(generated_images):
    raise ValueError("An image source was dropped or changed")
if not set(re.findall(r'href="#([^"]+)"', page_markup)) <= set(ids):
    raise ValueError("A same-page anchor has no destination")

# Keep the local source paths in generated/ for reference comparisons. The
# upload-ready copies use permanent Tilda CDN URLs for every local image.
asset_map = json.loads((ROOT / "tilda-assets.json").read_text(encoding="utf-8"))
record_map = json.loads((ROOT / "tilda-records.json").read_text(encoding="utf-8"))
referenced_assets = set(re.findall(r'(?<![\w/])assets/[\w.-]+', "\n".join(content for _, content in all_files)))
if referenced_assets != set(asset_map):
    raise ValueError(f"Asset map mismatch: missing {referenced_assets - set(asset_map)}, extra {set(asset_map) - referenced_assets}")
tilda_out = OUT / "tilda"
tilda_out.mkdir(exist_ok=True)
for stale in tilda_out.glob("*.html"):
    stale.unlink()
for name, content in all_files:
    if name == "head-seo.html":
        continue  # Tilda owns the core SEO tags; use head-page.html below.
    content = re.sub(
        r'https://raw\.githubusercontent\.com/[^" ]+/assets/gnathologist-hero-v38\.webp',
        asset_map['assets/gnathologist-hero-v38.webp'],
        content,
    )
    for local_path, cdn_url in asset_map.items():
        content = content.replace(local_path, cdn_url)
    # The standalone approved page does not load a TildaSans font face, so it
    # renders with Arial. Tilda loads TildaSans project-wide; keep the approved
    # rendered typography by making that fallback explicit in upload copies.
    content = content.replace("TildaSans", "Arial")
    if name == "00-global.html":
        # Tilda resets paragraph margins; the standalone quiz relies on the
        # browser's 1em default for these two paragraphs.
        content += ('\n<style id="edc-tilda-quiz-margin-fix">'
                    '#edc-quiz .edq-copy p,#edc-quiz p.edq-small{margin-block:1em}'
                    '</style>')
        # Sticky descendants are constrained by their T123 record wrapper.
        # The wrapper must stick for the approved header to stay visible.
        content += (f'\n<style id="edc-tilda-sticky-header-fix">'
                    f'#rec{record_map["01-header.html"]}'
                    '{position:sticky;top:0;z-index:100000}'
                    '</style>')
    if name == "20-scripts.html":
        # Restore the source's main landmark around independent T123 records
        # at runtime. Every record still contains balanced, editable markup.
        content = (
            '<script id="edc-tilda-main-landmark">(function(){'
            'var root=document.getElementById("allrecords"),'
            f'first=document.getElementById("rec{record_map["02-hero.html"]}"),'
            f'last=document.getElementById("rec{record_map["18-contacts.html"]}"),'
            'old=document.getElementById("edc-main");'
            'if(!root||!first||!last||!old||first.parentElement!==root||last.parentElement!==root)return;'
            'var main=document.createElement("main");main.id="edc-main";main.tabIndex=-1;'
            'first.before(main);var node=first;while(node){var next=node.nextElementSibling;'
            'main.append(node);if(node===last)break;node=next}old.remove()'
            '})();</script>\n' + content
        )
    if re.search(r'(?<![\w/])assets/[\w.-]+', content):
        raise ValueError(f"Unmapped local image in {name}")
    (tilda_out / name).write_text(content + "\n", encoding="utf-8")

# Tilda generates title, description, canonical and core Open Graph tags from
# page settings. Only put the remaining metadata and source JSON-LD in HEAD.
supplemental_meta = [
    tag for tag in seo
    if re.search(r'property="og:(?:locale|site_name|image:alt|image:type)"|name="twitter:', tag)
]
structured_data = re.findall(r'<script type="application/ld\+json"[^>]*>.*?</script>', head, re.S | re.I)
page_head = '\n'.join([
    '<meta http-equiv="content-language" content="ru-KZ">',
    '<script id="edc-page-language">document.documentElement.lang="ru-KZ";</script>',
    *supplemental_meta,
    *structured_data,
])
page_head = re.sub(
    r'https://raw\.githubusercontent\.com/[^" ]+/assets/gnathologist-hero-v38\.webp',
    asset_map['assets/gnathologist-hero-v38.webp'],
    page_head,
)
(tilda_out / 'head-page.html').write_text(page_head + '\n', encoding='utf-8')

# Assemble a local page without Tilda wrappers to isolate splitting differences.
preview_head = re.sub(r"<style\b[^>]*>.*?</style>", "", head, flags=re.S | re.I)
preview = (
    '<!doctype html><html lang="ru-KZ"><head>' + preview_head + "\n" + all_files[0][1]
    + '</head><body><div id="edc-modular-main">' + page_markup
    + '</div>' + all_files[-2][1] + '</body></html>'
)
# The preview is two folders below the source assets; transfer files retain original paths.
preview = re.sub(r"(?<![\w/])assets/", "../../assets/", preview)
(OUT / "preview.html").write_text(preview, encoding="utf-8")
print(f"Generated {len(all_files)} transfer files and a local preview; source blob {blob}")
