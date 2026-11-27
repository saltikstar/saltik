"""Capture repeatable browser evidence for the Elite Dental Tilda migration."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from playwright.sync_api import sync_playwright


WIDTHS = (320, 360, 375, 390, 430, 768, 1024, 1280, 1366, 1440, 1580, 1600, 1920, 2560)
SECTIONS = (
    ("header", "#edc-site-header"),
    ("hero", "#edc-gnathology-hero"),
    ("promos", "#edc-promos"),
    ("benefits", ".edv-why"),
    ("services", ".edv-services"),
    ("gnathology", ".edgn-section--treat"),
    ("braces", ".edo-section"),
    ("before-after", "#edc-before-after"),
    ("implantation", ".edx-implant"),
    ("implant-process", "#edc-implant-process"),
    ("surgery", "#edc-surgery"),
    ("quiz", "#edc-quiz"),
    ("cases", "#edc-cases"),
    ("about", "#edc-about-editorial"),
    ("team", "#edc-team-editorial"),
    ("doctors", "#edc-doctors"),
    ("reviews", "#edc-reviews"),
    ("contacts", "#edc-contacts"),
)


def capture(url: str, output: Path, widths: tuple[int, ...], sections: bool) -> None:
    output.mkdir(parents=True, exist_ok=True)
    report: dict[str, object] = {"url": url, "widths": {}, "browser": "/usr/bin/chromium", "dpr": 1}
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=True, executable_path="/usr/bin/chromium", args=["--no-sandbox"]
        )
        context = browser.new_context(
            viewport={"width": widths[0], "height": 900},
            device_scale_factor=1,
            ignore_https_errors=True,
            reduced_motion="reduce",
        )
        page = context.new_page()
        errors: list[str] = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        for width in widths:
            errors.clear()
            page.set_viewport_size({"width": width, "height": 900})
            page.goto(url, wait_until="domcontentloaded", timeout=60_000)
            page.evaluate("document.fonts.ready")
            page.evaluate(
                """async () => {
                  for (const img of document.images) img.loading = 'eager';
                  await Promise.all(Array.from(document.images, img => {
                    if (img.complete) return Promise.resolve();
                    return new Promise(resolve => {
                      img.addEventListener('load', resolve, {once:true});
                      img.addEventListener('error', resolve, {once:true});
                    });
                  }));
                  for (let y = 0; y < document.documentElement.scrollHeight; y += 700) {
                    scrollTo(0, y);
                    await new Promise(resolve => setTimeout(resolve, 8));
                  }
                  scrollTo(0, 0);
                }"""
            )
            page.wait_for_timeout(250)
            measurements = page.evaluate(
                """sections => {
                  const out = {};
                  for (const [name, selector] of sections) {
                    const el = document.querySelector(selector);
                    if (!el) { out[name] = null; continue; }
                    const r = el.getBoundingClientRect();
                    const c = getComputedStyle(el);
                    out[name] = {x:r.x,y:r.y + scrollY,width:r.width,height:r.height,
                      display:c.display,position:c.position,background:c.backgroundColor,
                      fontFamily:c.fontFamily,fontSize:c.fontSize};
                  }
                  return {sections:out,scrollWidth:document.documentElement.scrollWidth,
                    scrollHeight:document.documentElement.scrollHeight,
                    brokenImages:Array.from(document.images).filter(i => i.getAttribute('src') &&
                      (!i.complete || i.naturalWidth === 0)).map(i => i.src),
                    title:document.title};
                }""",
                SECTIONS,
            )
            measurements["pageErrors"] = list(errors)
            report["widths"][str(width)] = measurements
            page.screenshot(path=str(output / f"full-{width}.png"), full_page=True, animations="disabled")
            if sections:
                section_dir = output / f"sections-{width}"
                section_dir.mkdir(exist_ok=True)
                for name, selector in SECTIONS:
                    locator = page.locator(selector).first
                    if locator.count() and locator.is_visible():
                        locator.screenshot(path=str(section_dir / f"{name}.png"), animations="disabled")
        context.close()
        browser.close()
    (output / "measurements.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--widths", default=",".join(map(str, WIDTHS)))
    parser.add_argument("--sections", action="store_true")
    args = parser.parse_args()
    capture(args.url, args.output, tuple(int(x) for x in args.widths.split(",")), args.sections)
