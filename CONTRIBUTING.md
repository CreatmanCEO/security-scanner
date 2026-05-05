# Contributing

This repository is currently a **public showcase** — the bot's source code is private. **Phase 2** (in progress) is to release the full backend code under MIT and make the entire stack `docker compose up`-able on the contributor's own server. This `CONTRIBUTING.md` is the bridge: priorities are documented now so that when the code lands, the community can hit the ground running.

## Priorities (highest impact first)

1. **Detection-rule submissions** — even before the backend is open-sourced, the maintainer accepts well-documented detection rule proposals via [GitHub Issues](https://github.com/CreatmanCEO/security-scanner/issues):
   - **New stalkerware domains** with source / IoC reference (current baseline: 919 domains from AssoEchap)
   - **New mining-pool patterns** (current: Stratum protocol detection + 30+ mining-pool domains)
   - **New JA3 fingerprints** for known malware families with source (e.g. abuse.ch SSLBL, JoeSandbox)
   - **Behavioural patterns** with sample traffic captures (anonymised) — beaconing, exfiltration, sustained streaming
2. **Manufacturer telemetry mapping** — `docs/device-telemetry.md` documents per-vendor telemetry domains (Apple, Google, Samsung, Xiaomi, Huawei). Coverage of Asian / regional manufacturers (Vivo, Oppo, OnePlus, Realme, Tecno, Infinix) is incomplete — PRs welcome.
3. **Language locales** — currently English (this README) + Russian (`README.ru.md`). When the bot code lands open-source, the bot itself will need locale files (currently EN + RU). Translations welcome for: Spanish, Portuguese, Ukrainian, German, French, Hindi.
4. **Phase-2 Docker self-hosted hardening** — when the backend code is published, the docker-compose stack will need:
   - Hardened Suricata / Zeek configurations
   - Resource limits and health checks
   - Optional Tailscale / WireGuard as alternative to VLESS+Reality
   - First-run wizard for API key entry
5. **iOS-specific detection rules** — Apple ecosystem telemetry classification, iCloud Private Relay traffic differentiation. Pegasus / NSO behavioural indicators (high-port outbound + CloudFront infrastructure) are documented but coverage can grow.
6. **VirusTotal / MISP / STIX2 integrations** — push detection results into standard threat-intelligence formats for security teams.

## Responsible disclosure

If you have found a **security vulnerability** in the bot or the analysis pipeline (XSS in report rendering, SQL injection, VPN escape, etc.) — **do not** open a public GitHub issue. Instead:

- Email **creatmanick@gmail.com** with subject prefix `[SECURITY] security-scanner — `
- Provide reproduction steps, observed impact, and an anonymised reporter handle if you want public credit
- Expect an acknowledgement within 5 business days

We will coordinate disclosure timing with you. Public credit on the maintainer's discretion.

## What we will not merge

- Detection rules that target legitimate consumer apps (Telegram itself, WhatsApp, Signal, mainstream banking apps) — false-positive risk is too high
- Anything that requires a paid third-party service to function (without an open-source / free-tier alternative)
- Changes that bypass the two-step user-consent flow (consent on first scan; explicit start of every scan)
- Off-topic features (browser extensions, on-device app scanning) — those belong in dedicated forks
- Changes to the behavioural-detection thresholds without sample traffic and a confusion-matrix justification

## Pull request checklist (when Phase 2 code is open)

- [ ] If you added a detection rule: a test fixture with sample traffic capturing the rule firing, and a sample where it does *not* fire
- [ ] If you touched a Suricata rule: `suricata-update` and `suricata -T -c suricata.yaml` clean
- [ ] If you touched a Zeek script: `zeek -a script.zeek` clean
- [ ] User-visible changes mirrored in **both** `README.md` and `README.ru.md`
- [ ] `CHANGELOG.md` entry in Keep a Changelog format
- [ ] No PII (IPs, phone identifiers, account names) in commits or test fixtures — anonymise everything

## Style

- Code: Python 3.11+, type hints, docstrings on public functions, `logging` (not `print`), HTML parse_mode for Telegram
- Documentation: prefer plain-language explanation over jargon; show concrete examples
- Issue / PR titles: imperative voice (*"Add detection for X"*, not *"Added detection for X"*)
- One feature per PR

## Author / maintainer

[@CreatmanCEO](https://github.com/CreatmanCEO) — Nick Podolyak. For discussion before opening a large PR or proposing a detection-rule family, reach out via [@Creatman_it](https://t.me/Creatman_it) on Telegram.
