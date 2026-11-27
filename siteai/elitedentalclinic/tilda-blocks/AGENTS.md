# AGENTS.md — Elite Dental Clinic migration
- Reference commit 6a7de21f6e8da40fda18cda010f51d875afc14f8; do not redesign or alter copy, imagery, typography, spacing, animation, behavior, CSS cascade or approved facts.
- Read manifest and README. Generate from the source; never use historical standalone blocks.
- Inspect connected Tilda MCP tool schemas before choosing any write method. If raw T123 HTML editing is unsupported, stop and report; do not substitute Zero Block.
- Use a separate noindex test page only. Never modify/publish production without explicit approval.
- Start with header + hero. Capture Playwright baseline and Tilda screenshots at 320/360/375/390/430/768/1024/1280/1366/1440/1580/1600/1920/2560 widths; same browser, fonts, DPR, assets, animation state. Compare bounding boxes and computed styles; report diffs, do not assert parity without tests.
- Preserve shared styles order; audit Tilda wrappers, sticky, global body rules and scroll behavior. Do not duplicate IDs or span open tags across records. Split nested groups only after selector and geometry tests. Final goal: separate T123 per visible section.
- Verify menu, anchors, galleries, quiz, booking and WhatsApp draft without real patient data or sending messages. Test keyboard and mobile Safari. Validate SEO and production image hosting before release.
