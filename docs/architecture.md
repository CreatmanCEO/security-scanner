# Architecture — Security Scanner Bot

## System Overview

Security Scanner Bot is a server-side mobile traffic analysis system. It never installs software on the target device. Instead, it routes the phone's traffic through a VPN endpoint where three analysis engines (Suricata IDS, behavioral analyzer, blacklist correlator) inspect all connections in real time.

---

## Component Architecture

```
┌────────────────────────────────────────────────────────────────────────────┐
│                           VPN ANALYSIS SERVER                              │
│                                                                            │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                        TELEGRAM BOT LAYER                            │  │
│  │                                                                      │  │
│  │  bot.py ─────── scan_manager.py ─────── vless_manager.py            │  │
│  │     │                  │                       │                     │  │
│  │     │                  │                       ├── 3x-ui API calls   │  │
│  │     │                  │                       ├── Create VPN client │  │
│  │     │                  │                       └── Revoke on done    │  │
│  │     │                  │                                             │  │
│  │  database.py ──────────┘                                             │  │
│  │  (SQLite: users, scans, results)                                    │  │
│  └──────────────────────────────┬───────────────────────────────────────┘  │
│                                 │                                          │
│  ┌──────────────────────────────▼───────────────────────────────────────┐  │
│  │                     TRAFFIC CAPTURE LAYER                            │  │
│  │                                                                      │  │
│  │  xray-core (VLESS+Reality) ──── suricata ──── zeek                  │  │
│  │       │                            │            │                    │  │
│  │       ├── access.log               ├── eve.json ├── conn.log        │  │
│  │       │   (connections)            │   (alerts) │   (connections)    │  │
│  │       │                            │            ├── dns.log         │  │
│  │       │                            │            ├── ssl.log         │  │
│  │       │                            │            └── http.log        │  │
│  └───────┼────────────────────────────┼────────────┼───────────────────┘  │
│          │                            │            │                      │
│  ┌───────▼────────────────────────────▼────────────▼───────────────────┐  │
│  │                      ANALYSIS LAYER                                  │  │
│  │                                                                      │  │
│  │  ┌──────────────┐  ┌─────────────────┐  ┌───────────────────────┐  │  │
│  │  │ xray_parser  │  │ suricata_parser │  │ zeek_parser           │  │  │
│  │  │              │  │                 │  │                       │  │  │
│  │  │ Parse access │  │ Parse EVE JSON  │  │ Parse conn/dns/ssl   │  │  │
│  │  │ log entries  │  │ alerts + flows  │  │ logs into structs    │  │  │
│  │  └──────┬───────┘  └────────┬────────┘  └───────────┬───────────┘  │  │
│  │         │                   │                       │              │  │
│  │         └───────────────────┼───────────────────────┘              │  │
│  │                             │                                      │  │
│  │                  ┌──────────▼──────────┐                           │  │
│  │                  │  malware_detector   │                           │  │
│  │                  │                     │                           │  │
│  │                  │  Layer 1: Ports     │                           │  │
│  │                  │  Layer 2: Behavior  │                           │  │
│  │                  │  Layer 3: Blacklist │                           │  │
│  │                  └──────────┬──────────┘                           │  │
│  │                             │                                      │  │
│  │              ┌──────────────┼──────────────┐                      │  │
│  │              │              │              │                       │  │
│  │    ┌─────────▼──┐  ┌───────▼──────┐  ┌───▼────────────┐         │  │
│  │    │ traffic_   │  │ threat_      │  │ ai_analyzer    │         │  │
│  │    │ classifier │  │ lookup       │  │                │         │  │
│  │    │            │  │              │  │ Groq/Gemini    │         │  │
│  │    │ CDN, ads,  │  │ AbuseIPDB,   │  │ User-level     │         │  │
│  │    │ social,    │  │ OTX,         │  │ adaptive       │         │  │
│  │    │ telemetry  │  │ VirusTotal   │  │ report gen     │         │  │
│  │    └────────────┘  └──────────────┘  └────────────────┘         │  │
│  │                                                                   │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Component Descriptions

### 1. Telegram Bot Layer

#### `bot.py` — Core Bot Logic

- **Framework:** aiogram 3.x with Finite State Machine (FSM)
- **Responsibilities:**
  - User registration and language selection
  - Consent flow for privacy policy
  - Manufacturer selection (mobile-only, PC removed)
  - Scan initiation and progress reporting
  - Report delivery and follow-up questions
- **FSM States:**
  - `WELCOME` → `CONSENT` → `MANUFACTURER` → `MODEL` → `SECURITY_LEVEL` → `VPN_SETUP` → `SCANNING` → `RESULTS`
- **Handlers:** Command handlers (`/start`, `/scan`, `/history`, `/help`), callback query handlers for inline buttons, message handlers for free-text questions

#### `scan_manager.py` — Scan Lifecycle Manager

- **Responsibilities:**
  - Orchestrates the full scan lifecycle
  - Provisions VPN credentials before scan
  - Monitors scan duration (30 minutes for users, 10 minutes for admin testing)
  - Triggers analysis pipeline when scan completes
  - Cleans up VPN credentials after scan
  - Handles concurrent scans (queue system)
- **Key methods:**
  - `start_scan(user_id, device_type)` → Provisions VPN, returns config
  - `monitor_scan(scan_id)` → Watches for scan completion/timeout
  - `complete_scan(scan_id)` → Triggers analysis, delivers report
  - `cleanup_scan(scan_id)` → Revokes VPN, archives logs

#### `vless_manager.py` — VPN Client Management

- **Integration:** 3x-ui panel API (HTTP REST)
- **Responsibilities:**
  - Create temporary VLESS+Reality inbound client
  - Generate connection URI for v2rayNG / Shadowrocket
  - Generate QR code for easy setup
  - Delete client after scan completion
  - Monitor connected client traffic stats
- **Security:** Each scan gets unique UUID client. Credentials valid for scan duration + 5 min grace period. Auto-revocation on timeout.

#### `database.py` — Data Persistence

- **Engine:** SQLite 3 (single file, serverless)
- **Tables:**
  - `users` — Telegram user ID, language preference, technical level, registration date
  - `scans` — Scan ID, user ID, device type, start/end time, status, VPN client UUID
  - `scan_results` — Finding ID, scan ID, layer, severity, category, details (JSON)
  - `device_vendors` — Vendor name, telemetry domains, privacy notes

### 2. Traffic Capture Layer

#### xray-core (VLESS+Reality)

- **Purpose:** VPN tunnel termination
- **Protocol:** VLESS with Reality TLS camouflage
- **Why Reality:** The Reality protocol makes VPN traffic appear as legitimate TLS traffic to deep packet inspection (DPI) systems. This is essential for users in restrictive networks where standard VPN protocols are blocked.
- **Output:** `access.log` — each line contains timestamp, client IP, destination IP:port, protocol, bytes transferred
- **Management:** Controlled via 3x-ui panel which provides REST API for client CRUD operations

#### Suricata IDS

- **Purpose:** Signature-based threat detection
- **Ruleset:** Emerging Threats Open (18,987 rules)
- **Configuration:** Runs in IDS mode (detection, not prevention) on the VPN server's network interface
- **Output:** `eve.json` — structured JSON containing:
  - `alert` events — rule matches with sid, signature, severity
  - `flow` events — connection metadata (src/dst, bytes, duration)
  - `dns` events — DNS query/response pairs
  - `tls` events — TLS handshake data (SNI, certificate info)
- **Performance:** Multi-threaded, handles full VPN throughput without packet drops

#### Zeek Network Monitor

- **Purpose:** Structured network metadata generation
- **Why both Suricata AND Zeek:** Suricata excels at signature matching (known threats). Zeek excels at structured logging for behavioral analysis (unknown threats). Together they provide comprehensive coverage.
- **Output logs:**
  - `conn.log` — Every TCP/UDP connection with duration, bytes, state
  - `dns.log` — Every DNS query/response with query name, type, response
  - `ssl.log` — TLS connections with SNI, certificate chain, JA3 hash
  - `http.log` — HTTP transactions with method, URI, user-agent, status

### 3. Analysis Layer

#### Parser Modules

**`suricata_parser.py`**
- Reads Suricata EVE JSON output
- Extracts alert events (matched signatures)
- Extracts flow records for behavioral analysis
- Maps Suricata severity levels to internal severity scale
- Correlates alerts with connection metadata

**`xray_parser.py`**
- Reads xray-core access.log
- Extracts per-connection metadata: timestamp, destination IP, destination port, protocol, bytes in/out
- Provides the primary connection inventory for Layer 1 (port analysis)

**`zeek_parser.py`**
- Reads Zeek log files (TSV format)
- Parses conn.log for connection duration, byte counts, connection states
- Parses dns.log for domain-to-IP mapping
- Parses ssl.log for certificate analysis
- Provides enriched connection data for Layer 2 (behavioral analysis)

#### `malware_detector.py` — Three-Layer Detection Engine

This is the core analysis component. See [detection-rules.md](detection-rules.md) for the complete rule reference.

**Layer 1 — Port Analysis:**
- Input: All observed destination ports from xray_parser
- Process: Match against threat port database (35+ entries)
- Output: Instant classification with severity and threat category
- Speed: O(1) lookup per connection, sub-millisecond

**Layer 2 — Behavioral Analysis:**
- Input: Connection metadata from zeek_parser (timing, bytes, duration)
- Process: Statistical analysis of traffic patterns
  - Beaconing detection: interval regularity analysis per destination
  - Exfiltration detection: upload/download ratio analysis
  - Streaming detection: sustained bitrate analysis
  - Keylogger detection: frequent small payload analysis
- Output: Behavioral findings with confidence scores
- Speed: O(n log n) for n connections, typically < 1 second

**Layer 3 — Blacklist Correlation:**
- Input: All observed domains (from DNS logs) and IPs
- Process: Lookup against curated blacklists
  - Stalkerware domains (919 entries from AssoEchap)
  - Mining pool domains
  - Dynamic DNS providers
  - Known C2 domains
- Output: Blacklist matches with source attribution
- Speed: O(1) per domain using hash set lookup

#### `traffic_classifier.py` — Domain Categorization

Classifies all observed domains into categories for the report:

| Category | Examples | Purpose |
|----------|---------|---------|
| `cdn` | cloudflare.com, akamai.net, fastly.net | Content delivery — normal |
| `social` | facebook.com, instagram.com, tiktok.com | Social media — normal |
| `messaging` | whatsapp.net, telegram.org | Messaging — normal |
| `search` | google.com, bing.com | Search engines — normal |
| `telemetry` | tracking.miui.com, analytics.samsungknox.com | Vendor telemetry — flagged |
| `advertising` | doubleclick.net, admob.com | Ad networks — flagged |
| `suspicious` | *.duckdns.org, unknown VPS IPs | Requires investigation |
| `malicious` | Stalkerware domains, known C2 | Confirmed threat |

#### `threat_lookup.py` — External Threat Intelligence

Queries external APIs to enrich findings:

- **AbuseIPDB:** Checks destination IPs for abuse reports. Returns confidence score (0-100) and abuse categories.
- **AlienVault OTX:** Checks IPs and domains against OTX pulses. Returns associated malware families and threat tags.
- **Rate limiting:** Respects API rate limits. Caches results for 24 hours. Batches lookups for efficiency.

#### `ai_analyzer.py` — Adaptive Report Generation

- **LLM Providers:** Groq (LLaMA 3.3 70B) primary, Google Gemini fallback
- **Input:** Structured findings from malware_detector + enrichment from threat_lookup + classifications from traffic_classifier
- **Process:**
  1. Determine user's technical level (from profile or auto-detection)
  2. Construct prompt with findings, severity, evidence
  3. Request LLM to generate report at appropriate technical depth
  4. Post-process: add severity badges, format for Telegram markdown
- **Output:** Formatted Telegram message with:
  - Summary section (counts by severity)
  - Per-finding explanations
  - Recommended actions
  - Telemetry section (separate from threats)
  - "What's normal" section (reassurance about legitimate traffic)

---

## Data Flow — Complete Sequence

```
1. User sends /scan to Telegram bot
       │
2. bot.py → scan_manager.start_scan()
       │
3. scan_manager → vless_manager.create_client()
       │         → Returns VLESS URI + QR code
       │
4. User connects phone to VPN
       │
5. Phone traffic flows through xray-core
       │         ├── Logged to access.log
       │         ├── Mirrored to Suricata
       │         └── Mirrored to Zeek
       │
6. scan_manager.monitor_scan() waits for duration
       │
7. scan_manager.complete_scan() triggers analysis:
       │
       ├── xray_parser.parse() → connection list
       ├── suricata_parser.parse() → alerts + flows
       └── zeek_parser.parse() → conn/dns/ssl data
              │
              ▼
8. malware_detector.analyze()
       ├── Layer 1: port_analysis(connections)
       ├── Layer 2: behavioral_analysis(connections, flows)
       └── Layer 3: blacklist_check(domains, ips)
              │
              ▼
9. traffic_classifier.classify(domains)
       │
10. threat_lookup.enrich(findings)
       │         ├── AbuseIPDB queries
       │         └── OTX queries
       │
       ▼
11. ai_analyzer.generate_report(findings, user_level)
       │         ├── Groq LLaMA 3.3 70B (primary)
       │         └── Google Gemini (fallback)
       │
       ▼
12. bot.py delivers report to user via Telegram
       │
13. scan_manager.cleanup_scan()
       │         └── vless_manager.delete_client()
       │
14. Results stored in database (24h retention)
```

---

## Deployment

Single server deployment. All components run on the same machine:

- **OS:** Ubuntu 22.04 LTS
- **Requirements:** 2+ CPU cores, 4 GB RAM, 20 GB SSD
- **Services:** xray-core (systemd), Suricata (systemd), Zeek (systemd), Python bot (systemd)
- **Monitoring:** Systemd journal for logs, simple health check endpoint

---

## Security Considerations

- **No traffic storage:** Raw traffic (PCAP) is never written to disk. Only metadata and analysis results are stored.
- **Credential lifecycle:** VPN credentials are created per-scan and revoked immediately after.
- **Data retention:** Scan results are deleted after 24 hours.
- **No PII in logs:** Parser outputs are stripped of content — only metadata (IPs, ports, bytes, timing) is retained.
- **Server hardening:** Standard Linux hardening — firewall (iptables), SSH key-only, fail2ban, unattended upgrades.
