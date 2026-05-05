# Changelog

Public-facing milestones for the Security Scanner Bot project. Internal commit history is private — this file tracks user-visible behavioural / detection-engine changes.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) · [SemVer](https://semver.org/spec/v2.0.0.html).

## [Unreleased] — Phase 2: open-source / self-hosted (in progress)

### Working on
- Docker-compose self-hosted package (`docker compose up` deploys the entire stack on user's own server)
- Full backend code release under MIT (currently public repo is documentation-only)
- iOS-specific detection rules (Apple ecosystem telemetry classification, iCloud Private Relay detection)
- WireGuard VPN option (alternative to VLESS for users who prefer WireGuard)
- Scheduled recurring scans (daily / weekly automated)
- PDF report export with charts and visualisations
- Expanded stalkerware database beyond the 919-domain AssoEchap baseline

## [Showcase 0.2.0] — 2026-05-05

### Added
- `docs/screenshots/01-onboarding-and-vpn.webp` — three-screen onboarding flow showing greeting / privacy disclaimer / VPN-client picker
- `docs/screenshots/02-scan-and-report-delivery.webp` — three-screen active scan flow showing scan-started state / two VPN-key delivery modes / final report with download attachment
- `docs/reports/sample-scan-report.md` — anonymised real-world report example (3 CRITICAL findings — SSH/Telnet/RTSP — plus 6 HIGH-severity threat-intel IPs, traffic statistics, plain-language recommendations)
- `docs/reports/sample-scan-report.html` — same report rendered as standalone HTML (inline CSS, dark theme, mobile-friendly) — matches the file format the bot delivers to users
- `Limitations & known failure modes` section — 8 honest constraints (encrypted-payload blindness, JA3 evasion, detection lag for slow beaconing, mobile-only scope, network-side only, VPN-trust requirement, false-positive rate, no on-device remediation)
- `Contact` section with explicit channels for end users, security researchers / responsible disclosure, press, partnership / commercial discussions
- `Related — Claude Code ecosystem` section with cross-links to all 7 sister repos by the same author (anti-regression-setup, ai-context-hierarchy, claude-statusline, notebooklm-claude-workflows, lingua-companion, diabot, ghost-showcase)
- Author signature expanded — Nick Podolyak with GitHub / Habr / dev.to / Telegram links
- `CHANGELOG.md` (this file)
- `CONTRIBUTING.md` with Phase-2-readiness priorities (detection rules, manufacturer telemetry data, language locales, Docker-compose hardening, security-disclosure clause)
- `.github/workflows/validate.yml` — LICENSE / CHANGELOG presence, every `docs/*` asset referenced from README exists, internal Markdown links resolve, sample HTML report parses as valid HTML, sample MD report has no broken cross-refs
- New badges — Stars, Validate CI, "@secure_scanbot LIVE"

### Changed
- README structured into a clear flow with the new "What it looks like" section right after badges (screenshots + sample-report link visible above the Table of Contents — readers see *what the bot actually does* before reading the architecture)
- Author signature footer no longer just "Built by Creatman" — full attribution with all professional channels

### Operational fix
- **Bot uptime restored.** `security-scanner-bot.service` was crash-looping with `status=203/EXEC` since 2026-04-15 06:46 UTC because `/root/security-scanner/venv/` had been removed from disk (likely during cleanup). systemd attempted 170,678 restarts before this fix. The venv has been recreated, dependencies reinstalled (aiogram 3.4.1, aiohttp 3.9.3, aiosqlite 0.19.0, nest_asyncio, plus the analysis stack), and the service is back to active polling. Bot is once again live at @secure_scanbot.

## [Showcase 0.1.0] — 2026-03-16

### Added (initial showcase publication)
- Bilingual `README.md` and `README.ru.md` (1,072 / 1,077 lines) — comprehensive documentation of detection layers, architecture, comparison with existing solutions, real-world case study
- Five hero badges with concrete numbers — License, Telegram platform, 18,987 Suricata rules, 919 stalkerware domains, 97 JA3 fingerprints
- `docs/architecture.md` — detailed component descriptions with data-flow diagrams
- `docs/case-studies.md` — anonymised real-world case studies showing scanner findings
- `docs/detection-rules.md` — complete reference of all detection rules (ports, behaviours, blacklists)
- `docs/device-telemetry.md` — manufacturer telemetry domains database with privacy analysis
- `docs/research-mobile-malware-signatures.md` — research on network signatures of mobile malware families
- Real-world case study in README — 26 SSH connections discovered on a Xiaomi Redmi Note device (anonymised)
- Comparison table vs Amnesty MVT, PiRogue Security Suite, commercial mobile antivirus
- LICENSE — MIT

## [Bot v2.3 production] — 2026-03 (private code, public behaviour)

### Implemented behavioural changes (visible to users of @secure_scanbot)

- **Layer 4: JA3 TLS fingerprinting** — 97 malware fingerprints from abuse.ch SSLBL. Suricata extracts JA3 hashes; `ja3_matcher.py` correlates against the database. Detects malware by TLS handshake even on port 443.
- **Secure VPN key delivery** — subscription URL (recommended) and raw VLESS URI (fallback) so the user can choose their preferred client.
- **Admin broadcast system** — FSM flow: compose text, preview with user count, confirm, send to all users. HTML support with fallback on parse errors. Per-user error logging.
- **Tone-of-voice rewrite** — all user-facing messages simplified for non-technical users. Three report styles: plain language / technical / expert.
- **App download links** — inline button in scan message; per-OS links: Android (GitHub APK direct) + iPhone (AppStore) with Russia-aware warnings. Apps: Hiddify, v2rayNG, NekoBox, Streisand.
- **Cancel / back flow** — Cancel deletes scan from DB, removes the VPN key, notifies the user. "Back to scan" from app links does *not* cancel an active scan.
- **IP enrichment pipeline** — offline prefix matching + IP-API.com + SQLite cache (24-hour TTL).
- **False-positive protection** — server IP filtering, `SAFE_PREFIXES`, AbuseIPDB confidence threshold, client-IP exclusion.
- **Stale scan cleanup** — auto-cleanup of scans older than 45 minutes; periodic check every 30 minutes.
- **Admin metrics** — scan statistics, AI cost tracking (model, tokens, cost per scan), active scan monitoring with username.
