"""Exercise the approved interactions without contacting the clinic."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from playwright.sync_api import sync_playwright


SECTIONS = (
    "#edc-gnathology-hero", "#edc-promos", ".edv-why", ".edv-services",
    ".edgn-section--treat", ".edo-section", "#edc-before-after",
    ".edx-implant", "#edc-implant-process", "#edc-surgery", "#edc-quiz",
    "#edc-cases", "#edc-about-editorial", "#edc-team-editorial",
    "#edc-doctors", "#edc-reviews", "#edc-contacts",
)


def run(url: str) -> dict:
    result = {"url": url, "widths": {}}
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"])
        for width in (390, 1600):
            page = browser.new_page(
                viewport={"width": width, "height": 900},
                device_scale_factor=1, reduced_motion="reduce", ignore_https_errors=True,
            )
            errors: list[str] = []
            intercepted: list[str] = []
            page.on("pageerror", lambda error: errors.append(str(error)))

            def block_whatsapp(route):
                intercepted.append(route.request.url)
                route.fulfill(status=200, content_type="text/html", body="<html>WhatsApp draft intercepted</html>")

            page.route("https://wa.me/**", block_whatsapp)
            page.goto(url, wait_until="domcontentloaded", timeout=60_000)
            page.evaluate("document.fonts.ready")
            checks: dict[str, object] = {}

            checks["sections"] = sum(page.locator(selector).count() == 1 for selector in SECTIONS)
            assert checks["sections"] == len(SECTIONS)
            checks["anchors_and_ids"] = page.evaluate("""() => {
              const ids = Array.from(document.querySelectorAll('[id]'), e => e.id);
              return ids.length === new Set(ids).size &&
                Array.from(document.querySelectorAll('a[href^="#"]'))
                  .every(a => document.getElementById(decodeURIComponent(a.hash.slice(1))));
            }""")
            assert checks["anchors_and_ids"]

            if width == 390:
                burger = page.locator("#edc-site-header .edh-mobile")
                burger.locator("summary").click()
                assert burger.evaluate("e => e.open")
                page.keyboard.press("Escape")
                checks["burger_keyboard"] = not burger.evaluate("e => e.open")
                assert checks["burger_keyboard"]
            else:
                link = page.locator("#edc-site-header .edh-nav a[href='#edc-contacts']")
                link.click()
                checks["desktop_anchor"] = page.evaluate("location.hash") == "#edc-contacts"
                assert checks["desktop_anchor"]

            page.evaluate("scrollTo(0, 600)")
            checks["sticky_header"] = round(page.locator("#edc-site-header").bounding_box()["y"]) == 0
            assert checks["sticky_header"]

            page.locator(".edh-cta").click()
            booking = page.locator("#edc-booking")
            assert booking.evaluate("e => e.open")
            booking.locator("input[name=patient]").fill("Тест")
            booking.locator("input[name=phone]").fill("abc")
            booking.locator("input[name=consent]").check()
            booking.locator("button[type=submit]").click()
            checks["booking_phone_validation"] = booking.locator("input[name=phone]").evaluate("e => !e.validity.valid")
            assert checks["booking_phone_validation"]
            booking.locator("input[name=phone]").fill("+7 700 000 00 00")
            booking.locator("input[name=consent]").uncheck()
            booking.locator("button[type=submit]").click()
            checks["booking_consent"] = not intercepted and booking.evaluate("e => e.open")
            assert checks["booking_consent"]
            page.keyboard.press("Escape")
            checks["booking_escape"] = not booking.evaluate("e => e.open")
            assert checks["booking_escape"]

            def advance(track: str, button: str) -> bool:
                element = page.locator(track)
                before = element.evaluate("e => e.scrollLeft")
                page.locator(button).click()
                page.wait_for_timeout(150)
                return element.evaluate("e => e.scrollLeft") > before + 1

            checks["promos_carousel"] = advance("#edc-promos .edcp-track", "#edc-promos [data-edcp-next]")
            assert checks["promos_carousel"]
            page.locator("#edc-promos .edcp-open").first.click()
            dialog = page.locator("#edc-promos .edcp-modal")
            assert dialog.evaluate("e => e.open")
            page.locator("#edc-promos [data-edcp-modal-next]").click()
            checks["promos_modal"] = page.locator("#edc-promos .edcp-modal-count").inner_text().startswith("2 / ")
            page.keyboard.press("Escape")
            assert checks["promos_modal"] and not dialog.evaluate("e => e.open")

            page.locator("#edc-gnathology-next label.edg-option-m").click()
            checks["gnathology_choices"] = page.locator("#edg-m").is_checked()
            assert checks["gnathology_choices"]

            range_input = page.locator("#edc-before-after .edba-range").first
            range_input.evaluate("e => {e.value='75';e.dispatchEvent(new Event('input',{bubbles:true}))}")
            checks["before_after_range"] = range_input.evaluate("e => e.parentElement.style.getPropertyValue('--split')") == "75%"
            checks["before_after_carousel"] = advance("#edc-before-after .edba-track", "#edc-before-after [data-edba-next]")
            assert checks["before_after_range"] and checks["before_after_carousel"]

            page.locator("#edc-surgery .eds-image").first.click()
            dialog = page.locator("#edc-surgery dialog")
            assert dialog.evaluate("e => e.open")
            page.locator("#edc-surgery [data-eds-next]").click()
            checks["surgery_modal"] = page.locator("#edc-surgery .eds-count").inner_text().startswith("2 / ")
            page.keyboard.press("Escape")
            assert checks["surgery_modal"] and not dialog.evaluate("e => e.open")

            checks["cases_carousel"] = advance("#edc-cases .edcs-grid", "#edc-cases [data-edcs-track-next]")
            assert checks["cases_carousel"]
            page.locator("#edc-cases .edcs-tile").first.click()
            dialog = page.locator("#edc-cases dialog")
            assert dialog.evaluate("e => e.open")
            page.locator("#edc-cases [data-edcs-next]").click()
            checks["cases_modal"] = page.locator("#edc-cases .edcs-count").inner_text().startswith("2 / ")
            page.keyboard.press("Escape")
            assert checks["cases_modal"] and not dialog.evaluate("e => e.open")

            checks["doctor_profiles"] = page.locator("#edc-doctors .edd-card").count() == 12
            checks["doctors_carousel"] = advance("#edc-doctors .edd-track", "#edc-doctors [data-edd-next]")
            assert checks["doctor_profiles"] and checks["doctors_carousel"]

            checks["reviews_carousel"] = advance("#edc-reviews .edr-track", "#edc-reviews [data-edr-next]")
            assert checks["reviews_carousel"]
            page.locator("#edc-reviews .edr-slide").first.click()
            dialog = page.locator("#edc-reviews dialog")
            assert dialog.evaluate("e => e.open")
            page.locator("#edc-reviews [data-edr-modal-next]").click()
            checks["reviews_modal"] = page.locator("#edc-reviews .edr-count").inner_text().startswith("2 / ")
            page.keyboard.press("Escape")
            assert checks["reviews_modal"] and not dialog.evaluate("e => e.open")

            contacts = page.locator("#edc-contacts")
            checks["contacts"] = contacts.locator('a[href="tel:+77077530004"]').count() > 0 and \
                contacts.locator('a[href*="2gis"]').count() > 0 and contacts.locator("iframe").count() == 1
            assert checks["contacts"]

            quiz = page.locator("#edc-quiz")
            for step in range(5):
                quiz.locator(".edq-step:not([hidden]) label.edq-option").first.click()
                quiz.locator(".edq-next").click()
            checks["quiz_steps"] = quiz.locator(".edq-status").inner_text() == "Контакты и отправка"
            assert checks["quiz_steps"]
            quiz.locator('input[name="phone"]').fill("abc")
            quiz.locator('input[name="share"]').check()
            quiz.locator(".edq-send").click()
            checks["quiz_phone_validation"] = quiz.locator('input[name="phone"]').evaluate("e => !e.validity.valid")
            assert checks["quiz_phone_validation"]
            quiz.locator('input[name="phone"]').fill("+7 700 000 00 00")
            quiz.locator(".edq-send").click()
            page.wait_for_timeout(250)
            checks["whatsapp_draft_only"] = len(intercepted) == 1 and "text=" in intercepted[0]
            checks["page_errors"] = errors
            assert checks["whatsapp_draft_only"] and not errors
            result["widths"][str(width)] = checks
            page.close()
        browser.close()
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = run(args.url)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Functional checks passed at {', '.join(report['widths'])} px")
