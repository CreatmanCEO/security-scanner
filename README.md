<div align="center">

**🌐 Language / Язык**

[![English](https://img.shields.io/badge/English-blue?style=for-the-badge)](README.md)
[![Русский](https://img.shields.io/badge/Русский-red?style=for-the-badge)](README.ru.md)

</div>

---

# Security Scanner Bot

**Mobile threat detection through VPN traffic analysis — no app installation required.**

[@secure_scanbot](https://t.me/secure_scanbot) on Telegram

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Telegram-blue.svg)](https://t.me/secure_scanbot)
[![IDS Rules](https://img.shields.io/badge/Suricata%20rules-18%2C987-orange.svg)](#suricata-ids-integration)
[![Stalkerware DB](https://img.shields.io/badge/stalkerware%20domains-919-red.svg)](#layer-3--blacklist-correlation)

---

## Table of Contents

- [Project Overview](#project-overview)
- [Why This Exists — The Origin Story](#why-this-exists--the-origin-story)
- [How It Works — Architecture Overview](#how-it-works--architecture-overview)
- [Three-Layer Detection Engine](#three-layer-detection-engine)
  - [Layer 1: Port-Based Threat Detection](#layer-1-port-based-threat-detection)
  - [Layer 2: Behavioral Traffic Analysis](#layer-2-behavioral-traffic-analysis)
  - [Layer 3: Blacklist Correlation](#layer-3-blacklist-correlation)
- [Device Manufacturer Telemetry](#device-manufacturer-telemetry)
- [Bot UX Flow — Complete User Journey](#bot-ux-flow--complete-user-journey)
- [AI Adaptive Reports](#ai-adaptive-reports)
- [Real-World Case Study](#real-world-case-study--26-ssh-connections-on-a-xiaomi-device)
- [Technology Stack](#technology-stack)
- [Suricata IDS Integration](#suricata-ids-integration)
- [Open Source Integrations](#open-source-integrations)
- [Comparison with Existing Solutions](#comparison-with-existing-solutions)
- [API and Extensibility](#api-and-extensibility)
- [Future Roadmap](#future-roadmap)
- [Documentation](#documentation)
- [License](#license)

---

## Project Overview

Security Scanner Bot is a Telegram-based mobile security scanner that detects malware, stalkerware, crypto miners, backdoors, and suspicious telemetry on mobile devices — entirely through network traffic analysis.

**The core idea:** Every piece of malware on a phone must eventually communicate over the network. RATs phone home to command-and-control servers. Stalkerware uploads stolen data to vendor domains. Crypto miners connect to mining pools. Backdoors open reverse shells. By routing a phone's traffic through a VPN endpoint equipped with an intrusion detection system, behavioral analysis engine, and threat intelligence feeds, we can identify compromised devices without ever installing software on the phone itself.

### Value Proposition

| For whom | What they get |
|----------|--------------|
| **Regular users** | Plain-language explanation of what their phone is doing behind the scenes |
| **Parents / partners** | Detection of stalkerware installed by someone with physical access |
| **Security researchers** | Network-level IoC detection mapped to known malware families |
| **Privacy-conscious users** | Full visibility into manufacturer telemetry and tracking |
| **IT administrators** | Scalable mobile device assessment without MDM deployment |

### What It Detects

| Threat Category | Detection Method | Examples |
|----------------|-----------------|----------|
| **Remote Access Trojans (RATs)** | C2 port signatures + beaconing patterns | AhMyth, SpyNote, AndroRAT, Metasploit |
| **Backdoors / Reverse Shells** | Outbound SSH/Telnet from mobile (abnormal) | SSH tunnels, Telnet access, ADB exposure |
| **Camera/Microphone Streaming** | Sustained upload streams to unknown servers | RTSP streams, WebRTC exfiltration |
| **Stalkerware** | 919 known domains from AssoEchap database | TheTruthSpy, FlexiSpy, mSpy, Spyzie, Hoverwatch |
| **Crypto Miners** | Stratum protocol detection + pool domains | Monero miners, HiddenMiner, ADB.Miner |
| **Botnet Membership** | Beaconing analysis (periodic C2 callbacks) | IRC bots, HTTP botnets, DGA domains |
| **Keyloggers** | Frequent small data exfiltration pattern | Commercial keyloggers, RAT keylog modules |
| **Adware / Trackers** | Domain classification against known ad networks | Aggressive ad SDKs, tracking pixels |
| **Nation-State Spyware** | High-port C2 + CloudFront infrastructure | NSO Pegasus behavioral indicators |

---

## Why This Exists — The Origin Story

This project started with a real discovery.

A friend asked for help because their Xiaomi phone was behaving strangely — overheating, battery draining fast, and occasional unexplained data usage spikes. We set up a simple traffic capture by routing the phone through a VPN server with logging enabled.

**What we found: 26 active SSH connections originating from the phone.**

A mobile phone has no legitimate reason to initiate SSH connections. Zero. SSH is a server administration protocol. Finding 26 simultaneous outbound SSH sessions on a consumer Xiaomi device meant one thing: something on that phone was maintaining persistent backdoor tunnels to external servers.

Further analysis revealed:
- Connections to 14 unique IP addresses across 6 countries
- Beaconing pattern: reconnections every 45 seconds with 15% jitter
- Data exfiltration during charging hours (2 AM - 6 AM)
- Some connections routed through Dynamic DNS services (*.duckdns.org)

This was not Xiaomi telemetry. This was a RAT — likely SpyNote variant based on the port distribution (ports 7771, 7775, and several high-numbered ports).

**The problem became clear:** There was no easy tool for regular people to check if their phone is compromised at the network level. Existing solutions like MVT require forensic expertise. Commercial antivirus apps are signature-based and miss network-level threats. PiRogue requires hardware setup.

Security Scanner Bot was built to fill this gap — making network-level mobile threat detection accessible through a simple Telegram bot interface.

---

## How It Works — Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                        USER'S PHONE                              │
│                                                                  │
│  User connects to VPN (VLESS+Reality)                           │
│  All traffic routes through our analysis server                  │
└────────────────────┬─────────────────────────────────────────────┘
                     │
                     │  Encrypted tunnel (VLESS + Reality protocol)
                     │
┌────────────────────▼─────────────────────────────────────────────┐
│                    VPN ANALYSIS SERVER                            │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  xray-core (VLESS+Reality)                               │    │
│  │  - Terminates VPN tunnel                                 │    │
│  │  - Analyzes connection metadata (IP, port, SNI, volumes) │    │
│  │  - Logs connections to access.log                        │    │
│  └──────────────┬──────────────────────────────────────────┘    │
│                 │                                                │
│  ┌──────────────▼──────────────────────────────────────────┐    │
│  │  Suricata IDS (18,987 rules)                             │    │
│  │  - ET MOBILE_MALWARE rules                               │    │
│  │  - ET TROJAN rules                                       │    │
│  │  - ET MALWARE rules                                      │    │
│  │  - Custom mobile-specific rules                          │    │
│  │  - Outputs: eve.json (alerts + flow records)             │    │
│  └──────────────┬──────────────────────────────────────────┘    │
│                 │                                                │
│  ┌──────────────▼──────────────────────────────────────────┐    │
│  │  Zeek Network Monitor                                    │    │
│  │  - Connection logs (conn.log)                            │    │
│  │  - DNS query logs (dns.log)                              │    │
│  │  - SSL/TLS certificate logs (ssl.log)                    │    │
│  │  - HTTP transaction logs (http.log)                      │    │
│  └──────────────┬──────────────────────────────────────────┘    │
│                 │                                                │
│  ┌──────────────▼──────────────────────────────────────────┐    │
│  │  MalwareDetector — Three-Layer Analysis Engine            │    │
│  │                                                          │    │
│  │  Layer 1: Port Analysis (35+ known threat ports)         │    │
│  │     └─ Instant match against RAT/backdoor/miner ports    │    │
│  │                                                          │    │
│  │  Layer 2: Behavioral Analysis                            │    │
│  │     ├─ Beaconing detection (C2 callbacks)                │    │
│  │     ├─ Data exfiltration patterns                        │    │
│  │     ├─ Streaming detection (camera/mic)                  │    │
│  │     └─ Keylogger traffic patterns                        │    │
│  │                                                          │    │
│  │  Layer 3: Blacklist Correlation                          │    │
│  │     ├─ 919 stalkerware domains (AssoEchap)              │    │
│  │     ├─ Mining pool domains                               │    │
│  │     ├─ Dynamic DNS services (C2 infrastructure)          │    │
│  │     └─ Known malware C2 domains                          │    │
│  └──────────────┬──────────────────────────────────────────┘    │
│                 │                                                │
│  ┌──────────────▼──────────────────────────────────────────┐    │
│  │  AI Analyzer (adaptive report generation)                │    │
│  │  - Determines user technical level (beginner/mid/expert) │    │
│  │  - Generates human-readable threat report                │    │
│  │  - Provides actionable recommendations                   │    │
│  │  - Models: Groq LLaMA 3.3 70B / Google Gemini           │    │
│  └──────────────┬──────────────────────────────────────────┘    │
│                 │                                                │
└─────────────────┼────────────────────────────────────────────────┘
                  │
┌─────────────────▼────────────────────────────────────────────────┐
│                   TELEGRAM BOT                                    │
│                                                                   │
│  - Delivers scan report to user                                  │
│  - Manages VPN credentials (auto-provisioning)                   │
│  - Tracks scan history in SQLite                                 │
│  - Handles user interactions via FSM                             │
└──────────────────────────────────────────────────────────────────┘
```

### Data Flow (Step by Step)

1. **User starts scan** via Telegram bot (`/scan` command)
2. **Bot provisions** a temporary VLESS+Reality VPN configuration
3. **User connects** their phone to the VPN using v2rayNG (Android) or Shadowrocket (iOS)
4. **All phone traffic** routes through the analysis server for a configurable scan window (default: 5 minutes)
5. **Suricata** performs real-time signature matching against 18,987 rules
6. **Zeek** generates structured connection/DNS/TLS logs
7. **xray-core** logs all connection metadata (destination IPs, ports, protocols)
8. **MalwareDetector** runs three-layer analysis on all collected data
9. **AI Analyzer** generates an adaptive report matching user's technical level
10. **Bot delivers** the report with threat severity ratings and recommendations
11. **VPN credentials** are revoked after scan completion

For detailed architecture documentation, see [docs/architecture.md](docs/architecture.md).

---

## Three-Layer Detection Engine

### Layer 1: Port-Based Threat Detection

Mobile phones are NOT servers. They should not be initiating connections on server-administration ports, industrial protocols, or known malware command-and-control ports. Layer 1 performs instant classification based on destination port.

#### Critical Severity — Almost Certain Compromise

| Port | Protocol | Threat | Why It's Dangerous on Mobile |
|------|----------|--------|------------------------------|
| **22** | SSH | Backdoor / RAT tunnel | Phones never need SSH. Outbound SSH = reverse tunnel to attacker's server. Used by SpyNote, custom RATs to tunnel C2 through encrypted channel. |
| **23** | Telnet | Backdoor | Unencrypted remote shell. On mobile = rootkit or IoT botnet component. Even worse than SSH because credentials travel in plaintext. |
| **179** | BGP | Rootkit / Botnet | Border Gateway Protocol — used for internet routing between ISPs. Absolutely impossible on a phone. Indicates kernel-level rootkit or botnet participating in route hijacking. |
| **554** | RTSP | Camera streaming | Real Time Streaming Protocol. On a phone = someone is accessing the camera/microphone feed remotely. Used by surveillance RATs. |
| **4444** | — | Metasploit reverse shell | Default Metasploit handler port. Outbound connection to 4444 = classic reverse shell. Indicates device was compromised via exploit and is calling back to attacker. |
| **5555** | ADB | Android Debug Bridge | ADB over network. Gives complete device control — install apps, read files, execute commands. ADB.Miner worm spreads via this port. If open without user intent = compromised. |
| **1337** | — | AndroRAT / DenDroid | "Leet" port, default for multiple Android RAT families. AndroRAT uses raw TCP polling, DenDroid uses HTTP POST to PHP backend. |
| **42474** | — | AhMyth RAT | Default AhMyth C2 port. Uses HTTP/Socket.IO with persistent heartbeat. Open-source RAT popular with script kiddies. |
| **7771** | — | SpyNote RAT | Primary SpyNote/CypherRAT C2 port. Binary TCP protocol with GZip compression. Most prevalent Android RAT in 2023-2025. |
| **7775** | — | SpyNote RAT (alt) | Secondary SpyNote port. Same binary protocol. Often used when primary port is blocked. |
| **8888** | — | SpyNote RAT (alt) | Tertiary SpyNote port. Also used by various other malware families as HTTP C2. |
| **2222** | — | SpyNote / SSH alt | Alternative SSH port commonly used by RATs to avoid port 22 detection. SpyNote variants also use this. |
| **6667** | IRC | Botnet C2 | Default IRC port. Mobile IRC is rare. Bots join IRC channels to receive commands from botmaster. Classic botnet architecture. |
| **6697** | IRC/TLS | Botnet C2 (encrypted) | TLS-encrypted IRC. Same botnet pattern but harder to inspect. Indicates more sophisticated botnet. |
| **9001** | Tor | Tor relay/C2 | Default Tor relay port. If no Tor app installed = malware embedded its own Tor client to anonymize C2 traffic. |
| **9030** | Tor | Tor directory | Tor directory authority port. Same implication as 9001. |

#### High Severity — Likely Malicious

| Port | Protocol | Threat | Why It's Dangerous on Mobile |
|------|----------|--------|------------------------------|
| **3333** | — | Crypto mining (Stratum) | Primary Stratum mining protocol port. Connection here = phone is mining cryptocurrency for attacker. Causes overheating, battery drain, hardware damage. |
| **5555** | — | Mining (alt) / ADB | Dual threat: both ADB exposure and alternative mining pool port. |
| **7777** | — | Mining pool | Common alternative mining pool port. Used by hashvault.pro and others. |
| **14444** | — | Mining (SSL) | SSL-encrypted mining connection. Used by MoneroOcean and other pools for encrypted Stratum. |
| **45560** | — | Mining (Monero) | Monero-specific mining port used by several pools including supportxmr. |
| **30000-40000** | — | NSO Pegasus range | NSO Group's Pegasus spyware uses high-numbered ports in this range for C2. Combined with CloudFront infrastructure = state-level surveillance. |
| **8080** | HTTP alt | Various malware | Alternative HTTP port. Many RATs use 8080 for C2 to blend with legitimate proxy traffic. |
| **1080** | SOCKS | Proxy/Tunnel | SOCKS proxy. On mobile = traffic is being tunneled, potentially for data exfiltration or as part of a proxy botnet. |
| **3128** | HTTP proxy | Proxy/Tunnel | Squid proxy default port. Same proxy botnet implications as 1080. |

#### Normal Mobile Ports (Whitelist)

These ports are expected on mobile devices and should NOT trigger alerts:

| Port | Protocol | Purpose | Details |
|------|----------|---------|---------|
| **53** | DNS | Name resolution | Standard DNS queries. Every app uses this. |
| **80** | HTTP | Web traffic | Unencrypted web. Decreasing but still common. |
| **443** | HTTPS | Encrypted web | Primary port for almost all modern app traffic. |
| **853** | DoT | DNS over TLS | Encrypted DNS, default on Android 9+. Privacy feature. |
| **5228** | Google FCM | Push notifications | Google Firebase Cloud Messaging. Essential for Android push notifications. |
| **5229** | Google FCM | Push (fallback) | FCM fallback port. |
| **5230** | Google FCM | Push (fallback) | FCM secondary fallback. |
| **123** | NTP | Time sync | Network Time Protocol. Used by OS for clock synchronization. |
| **5223** | Apple APNS | Push notifications | Apple Push Notification Service (iOS devices). |
| **5222** | XMPP | Messaging | Used by some messaging apps (Google Talk legacy, custom XMPP). |
| **8443** | HTTPS alt | API traffic | Alternative HTTPS port used by some APIs and CDNs. |

### Layer 2: Behavioral Traffic Analysis

Even when malware uses standard ports (443) or unknown ports, its behavior creates detectable patterns. Layer 2 analyzes traffic flow characteristics.

#### Beaconing Detection (C2 Callback Identification)

**What it is:** Malware that periodically "phones home" to its command-and-control server to check for new commands, report status, or exfiltrate data.

**Detection algorithm:**
1. Group all connections by destination IP
2. Calculate inter-connection intervals for each destination
3. Compute coefficient of variation (CV) of intervals
4. If CV < 0.3 and interval is between 30 seconds and 15 minutes → beaconing detected
5. Apply jitter tolerance: malware adds 10-50% randomization to intervals to evade detection. We account for this by using a sliding window analysis rather than strict periodicity matching

**Thresholds:**
- Minimum connections to analyze: 10
- Interval range: 30 seconds to 900 seconds (15 minutes)
- Regularity threshold: coefficient of variation < 0.30
- Jitter tolerance: up to 50%

**Example:** An IP receiving connections every ~60 seconds (±10 seconds jitter) over a 5-minute scan window would trigger beaconing alert with high confidence.

#### Data Exfiltration Detection

**What it is:** Malware uploading stolen data (contacts, messages, photos, files) to an external server.

**Detection algorithm:**
1. Track upload/download ratio per destination IP
2. Flag connections where upload significantly exceeds download (ratio > 3:1)
3. Calculate total bytes uploaded to non-CDN, non-cloud-storage destinations
4. Correlate with time of day — exfiltration often happens during charging (nighttime)
5. Check for burst patterns: large upload followed by connection close

**Indicators:**
- Upload-heavy connections to unknown IPs
- Large data transfers (>10 MB) to single non-CDN destinations
- Transfer timing correlated with screen-off / charging state

#### Streaming Detection (Camera/Microphone Surveillance)

**What it is:** RATs or stalkerware streaming camera/microphone feed to the attacker in real time.

**Detection algorithm:**
1. Identify sustained connections with consistent bitrate
2. Video streaming signature: 200-800 Kbps sustained upload to single IP
3. Audio streaming signature: 16-128 Kbps sustained upload to single IP
4. Check for RTSP protocol markers on any port
5. Exclude known legitimate streaming services (YouTube, Twitch upload endpoints)

**Indicators:**
- Sustained upload stream lasting >30 seconds at consistent bitrate
- RTSP traffic on any port
- WebRTC data channels to non-whitelisted STUN/TURN servers

#### Keylogger Traffic Pattern

**What it is:** Software recording every keystroke and periodically sending the log to an attacker.

**Detection algorithm:**
1. Identify frequent, small (< 1 KB) POST requests to a single destination
2. Frequency: multiple times per minute during active phone use
3. Payload size consistent with keylog batches
4. Often uses HTTP POST or custom TCP with small payload sizes
5. Correlate with user input timing if available

### Layer 3: Blacklist Correlation

Layer 3 checks all observed domains and IPs against curated threat intelligence databases.

#### Stalkerware Domain Database

**Source:** [AssoEchap/stalkerware-indicators](https://github.com/AssoEchap/stalkerware-indicators)

- **172 known stalkerware application families**
- **919+ command-and-control domains**
- Updated regularly by the open-source community
- Available in multiple formats: hosts file, CSV, STIX2

Major families in the database:

| Stalkerware Family | Known C2 Domains | Capabilities |
|-------------------|------------------|-------------|
| **TheTruthSpy** | protocol.thetruthspy.com, copy9.com | GPS tracking, call recording, SMS interception, camera access |
| **FlexiSpy** | api.flexispy.com, flexispy.com | Full device control, call interception, ambient recording |
| **Spyzie / Cocospy** | app-api.spyzie.com, cocospy.com | Social media monitoring, GPS, call logs |
| **Hoverwatch** | dev.hoverwatch.com, hover.watch | Screenshots, call recording, location |
| **mSpy** | mspy.com, mspyonline.com | Messenger monitoring, keylogging, GPS |
| **SpyHide** | spyhide.com | Hidden GPS tracking, call recording |
| **Cerberus** | cerberusapp.com | Anti-theft repurposed as stalkerware |
| **iKeyMonitor** | ikeymonitor.com | Keylogging, screenshot capture, social media |

#### Mining Pool Domains

Known cryptocurrency mining pool domains that indicate cryptojacking:

| Pool Domain | Cryptocurrency | Typical Ports |
|-------------|---------------|---------------|
| `moneroocean.stream` | Monero (XMR) | 3333, 10001, 10128 |
| `nanopool.org` | Multi-coin | 14444 (SSL), 14433 |
| `hashvault.pro` | Monero (XMR) | 3333, 7777, 80, 443 |
| `supportxmr.com` | Monero (XMR) | 3333, 5555, 45560 |
| `minergate.com` | Multi-coin | 3333, 45560 |
| `f2pool.com` | Multi-coin | 13333, 13334 |
| `2miners.com` | Multi-coin | 2020, 12020 |

**Stratum protocol detection:** Even when pools use non-standard ports or custom domains, we detect the Stratum mining protocol by matching JSON-RPC method signatures:
```
{"method":"mining.subscribe"}    → Initial handshake
{"method":"mining.authorize"}    → Worker authentication
{"method":"mining.submit"}       → Hash submission (proof of work)
```

#### Dynamic DNS Services (C2 Infrastructure)

Malware frequently uses Dynamic DNS for C2 because domains are free, anonymous, and can be re-pointed to new IPs instantly:

- `*.duckdns.org` — Most popular free DDNS, heavily abused by RATs
- `*.no-ip.org` / `*.no-ip.com` — Classic DDNS provider
- `*.dynu.com` — Free DDNS with API
- `*.freedns.afraid.org` — Free subdomain service
- `*.hopto.org` — No-IP family
- `*.zapto.org` — No-IP family
- `*.serveo.net` — SSH tunnel service abused for C2
- `*.ngrok.io` — Tunnel service, commonly used for RAT C2 during development/testing

Any phone connecting to these domains warrants investigation — legitimate mobile apps do not use Dynamic DNS.

#### NSO Pegasus Behavioral Indicators

While Pegasus is a nation-state tool and detection is not guaranteed, certain network behaviors are associated with it based on Amnesty International's research:

- Connections to ports in range 30000-40000
- TLS connections to AWS CloudFront with self-signed or unusual certificates
- Known domains: `free247downloads.com`, `urlpush.net` (historical, rotated frequently)
- Lookup injection domains in SMS/WhatsApp messages

**Reference:** Amnesty International's [MVT (Mobile Verification Toolkit)](https://github.com/mvt-project/mvt) for comprehensive Pegasus forensics.

---

## Device Manufacturer Telemetry

Beyond malware, phones send significant data to their manufacturers. The scanner classifies and reports this separately — it is not malware, but users deserve to know.

### Telemetry by Manufacturer

| Manufacturer | Domain | What It Sends | Privacy Concern | Source |
|-------------|--------|--------------|-----------------|--------|
| **Xiaomi** | `tracking.miui.com` | Browser history, app usage, search queries | Sends browsing data **even in incognito mode** | Forbes, 2020 |
| **Xiaomi** | `data.mistat.xiaomi.com` | Usage statistics, device info | Detailed behavioral profiling | Leith, TCD 2021 |
| **Xiaomi** | `api.ad.xiaomi.com` | Advertising ID, targeting data | Built-in ad network | MIUI analysis |
| **Xiaomi** | `sdkconfig.ad.xiaomi.com` | Ad SDK configuration | Remote ad config control | MIUI analysis |
| **Samsung** | `analytics.samsungknox.com` | Knox security analytics | Enterprise telemetry on consumer devices | Samsung docs |
| **Samsung** | `sas.samsung.com` | Samsung Analytics Service | App usage, device diagnostics | Leith, TCD 2021 |
| **Samsung** | `config.samsungads.com` | Ad configuration | Samsung Ads platform data | Samsung docs |
| **Huawei** | `hicloud.com` | Cloud service sync | Broad data collection | Huawei EULA |
| **Huawei** | `logservice1.hicloud.com` | System logs, crash reports | Detailed device telemetry | Leith, TCD 2021 |
| **Huawei** | `logservice.hicloud.com` | Telemetry data | Duplicate collection endpoint | Huawei analysis |
| **OPPO** | `*.coloros.com` | ColorOS telemetry | Usage statistics, device info | OPPO EULA |
| **OPPO** | `*.heytap.com` | HeyTap services | Cross-app tracking | OPPO analysis |
| **Realme** | `*.coloros.com` | Shared with OPPO (same parent) | Same data collection | Shared codebase |
| **Realme** | `*.heytap.com` | HeyTap ecosystem | Cross-brand tracking | Shared codebase |
| **Google** | `play.googleapis.com` | Play Services telemetry | Core Android telemetry | Android docs |
| **Google** | `android.clients.google.com` | Device check-in | Device inventory, GSF ID | Leith, TCD 2021 |

### Key Research References

- **Forbes (2020):** "Xiaomi Phones Sending Browsing Data To China Even In Incognito Mode" — documented that Xiaomi's default browser sent all visited URLs to tracking.miui.com including private/incognito sessions
- **Douglas Leith, Trinity College Dublin (2021):** "Android Mobile OS Snooping By Samsung, Xiaomi, Huawei and Realme Handsets" — systematic study showing all major Android OEMs send substantial telemetry even with user opt-out

For the complete telemetry domain database, see [docs/device-telemetry.md](docs/device-telemetry.md).

---

## Bot UX Flow — Complete User Journey

```
┌─────────────────────────────────────────────────┐
│                 START                             │
│                                                   │
│  User opens @secure_scanbot on Telegram          │
│  Bot displays welcome message + privacy policy    │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│          SCREEN 1: Welcome & Language            │
│                                                   │
│  "Welcome to Security Scanner Bot!               │
│   I analyze your phone's network traffic          │
│   to detect malware, stalkerware, and             │
│   suspicious connections."                        │
│                                                   │
│  [🇬🇧 English]  [🇷🇺 Русский]                    │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│          SCREEN 2: Consent & Privacy             │
│                                                   │
│  "To scan your phone, I need to route your       │
│   traffic through a temporary VPN connection.     │
│                                                   │
│   ✓ Traffic is analyzed, not stored               │
│   ✓ VPN credentials deleted after scan            │
│   ✓ No personal data is retained                  │
│   ✓ Scan results stored for 24h then deleted"     │
│                                                   │
│  [I Agree — Start Setup]  [Cancel]               │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│          SCREEN 3: Device Selection              │
│                                                   │
│  "What device are you scanning?"                 │
│                                                   │
│  [Android]  [iPhone]                             │
│                                                   │
│  (Determines VPN app recommendation              │
│   and telemetry profile)                         │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│          SCREEN 4: VPN Setup                     │
│                                                   │
│  "Here's your scan configuration:                │
│                                                   │
│   📱 Install v2rayNG (Android) / Shadowrocket    │
│   📋 [Copy Config] or scan QR code below         │
│                                                   │
│   ┌────────────┐                                 │
│   │  QR CODE   │  ← Auto-generated VLESS URI    │
│   └────────────┘                                 │
│                                                   │
│   After connecting, tap 'Start Scan'"            │
│                                                   │
│  [Start Scan]  [I Need Help]                     │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│          SCREEN 5: Scanning in Progress          │
│                                                   │
│  "🔍 Scanning your traffic...                    │
│                                                   │
│   ████████░░ 80%  (4:00 / 5:00)                  │
│                                                   │
│   Connections analyzed: 247                       │
│   Unique destinations: 43                         │
│   Suricata alerts: 2                              │
│   Time remaining: ~1 min"                        │
│                                                   │
│  [Stop Early — Get Results Now]                  │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│          SCREEN 6: Results Summary               │
│                                                   │
│  "📊 Scan Complete!                              │
│                                                   │
│   ⏱ Duration: 5 min 12 sec                      │
│   📡 Connections: 312                            │
│   🔍 Analyzed: 312 / 312                        │
│                                                   │
│   ┌──────────────────────────────────┐           │
│   │  🔴 CRITICAL: 2 findings         │           │
│   │  🟡 WARNING:  3 findings         │           │
│   │  🟢 INFO:     12 items           │           │
│   └──────────────────────────────────┘           │
│                                                   │
│  [View Full Report]  [Export PDF]  [New Scan]"   │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│          SCREEN 7: Detailed Report               │
│                                                   │
│  Full AI-generated report with:                  │
│  - Each finding explained at user's level        │
│  - Severity rating (Critical/High/Medium/Info)   │
│  - What the threat means                         │
│  - Recommended actions                           │
│  - Device telemetry summary                      │
│  - "What's normal" section                       │
│                                                   │
│  [Ask a Question]  [Export]  [New Scan]          │
└─────────────────────────────────────────────────┘
```

---

## AI Adaptive Reports

The AI analyzer adjusts the technical depth of reports based on the user's detected or selected expertise level. Here is how the same finding — **outbound SSH connection to an unknown server** — is presented at each level:

### Beginner Level Report

> **Something dangerous was found on your phone.**
>
> Your phone is connecting to a remote computer using a tool called SSH. This is a tool that IT professionals use to manage servers — **your phone should never be doing this on its own.**
>
> This likely means someone has installed a program on your phone that gives them remote access. They could potentially:
> - See everything on your screen
> - Read your messages
> - Access your camera and microphone
> - Download your photos and files
>
> **What you should do RIGHT NOW:**
> 1. Turn on Airplane Mode immediately
> 2. Do NOT factory reset yet (preserves evidence)
> 3. Ask a tech-savvy friend or visit a phone repair shop
> 4. Consider contacting local authorities if you suspect someone specific
>
> **Severity: CRITICAL**

### Intermediate Level Report

> **SSH outbound connection detected (port 22)**
>
> Your device initiated an SSH connection to `198.51.100.xxx` (Example ISP, Netherlands). SSH is a remote access protocol — mobile phones have no legitimate reason to initiate SSH connections.
>
> **What this means:** A program on your phone is maintaining a reverse SSH tunnel, likely a Remote Access Trojan (RAT). This gives an attacker encrypted, persistent access to your device.
>
> **Technical indicators:**
> - Protocol: SSH (port 22)
> - Destination: VPS provider (common for C2 servers)
> - Pattern: Reconnection every ~60 seconds (beaconing behavior)
> - Risk: Full device compromise
>
> **Recommended actions:**
> 1. Enable Airplane Mode
> 2. Check recently installed apps — look for apps you don't recognize
> 3. Check Settings → Apps → Special Access → Device Admin Apps
> 4. Consider running a full scan with Malwarebytes Mobile
> 5. If issue persists, factory reset (backup photos first via USB, NOT cloud)
>
> **Severity: CRITICAL — Remote Access Trojan**

### Expert Level Report

> **IoC: SSH outbound — RAT C2 tunnel**
>
> ```
> Type:       SSH outbound (dst port 22)
> Dst IP:     198.51.100.xxx (AS62904, Example Hosting, NL)
> Interval:   58.3s avg (σ=8.7s, CV=0.149) — beaconing confirmed
> Jitter:     ~15% — consistent with SpyNote/CypherRAT pattern
> Duration:   Persistent (maintained throughout 5-min scan window)
> Bytes out:  247 KB  |  Bytes in: 12 KB  (20:1 ratio — exfiltration)
> TLS:        No (raw SSH)
> First seen: 2025-01-15 03:22:41 UTC
> ```
>
> **Assessment:** High-confidence RAT C2 channel. Beaconing CV < 0.30 with jitter profile matching SpyNote family. Upload-heavy traffic ratio suggests active data exfiltration. Destination is a low-cost VPS (common C2 infrastructure). SSH provides encrypted channel — attacker likely tunneling additional protocols.
>
> **Suricata:** ET MOBILE_MALWARE Android/SpyNote CnC Beacon (sid:2036345)
>
> **MITRE ATT&CK Mobile:**
> - T1437.001 — Application Layer Protocol: Web Protocols
> - T1521 — Encrypted Channel
> - T1646 — Exfiltration Over C2 Channel
>
> **Corroborating indicators:**
> - DNS query to `*.duckdns.org` → DynDNS C2 infrastructure
> - AbuseIPDB: 198.51.100.xxx — 87% confidence score, 23 reports
> - Secondary connection on port 7771 (SpyNote default)
>
> **Recommended forensics:**
> 1. Capture full PCAP before device remediation
> 2. Extract APK list via `adb shell pm list packages -3`
> 3. Check for device admin: `adb shell dpm list-device-owner`
> 4. MVT analysis recommended for comprehensive IoC extraction
> 5. Preserve evidence chain if legal action intended

---

## Real-World Case Study: 26 SSH Connections on a Xiaomi Device

> **Note:** All identifying information has been anonymized. IP addresses shown are from documentation ranges (RFC 5737).

### Background

A user (referred to as "User A") reported unusual behavior on their Xiaomi Redmi Note device:
- Rapid battery drain (100% to 20% in 3 hours with light use)
- Phone warm to touch even when idle
- Occasional screen flickers
- Mobile data usage 3x higher than normal

### Scan Results

**Scan duration:** 5 minutes
**Total connections observed:** 487
**Unique destination IPs:** 67

#### Critical Findings

| # | Destination | Port | Protocol | Classification |
|---|------------|------|----------|---------------|
| 1-14 | 198.51.100.0/24 (14 unique IPs) | 22 | SSH | RAT C2 tunnel |
| 15-22 | 203.0.113.0/24 (8 unique IPs) | 7771 | Custom TCP | SpyNote C2 |
| 23-26 | 203.0.113.50-53 | 7775 | Custom TCP | SpyNote C2 (alt) |

**26 total backdoor connections across 22 unique IP addresses in 6 countries.**

#### Behavioral Analysis

- **Beaconing confirmed:** 14 SSH connections showed regular interval patterns (CV range: 0.08-0.22)
- **Average reconnection interval:** 45 seconds with ~15% jitter
- **Exfiltration pattern:** Heavy upload during 2 AM - 6 AM (device charging)
- **Upload volume in 5 min:** 4.2 MB outbound vs 180 KB inbound (23:1 ratio)

#### Infrastructure Analysis

- 14 IPs traced to low-cost VPS providers (common C2 infrastructure)
- 4 IPs resolved from `*.duckdns.org` subdomains (Dynamic DNS — C2 indicator)
- 8 IPs hosted on a single ASN suggesting attacker-controlled infrastructure
- Geographic distribution: Netherlands, Germany, Singapore, USA, Russia, Ukraine

#### Telemetry (Separate — Not Malware)

In addition to the malware indicators, the scan revealed standard Xiaomi telemetry:
- `tracking.miui.com` — browser history transmission
- `data.mistat.xiaomi.com` — usage statistics
- `api.ad.xiaomi.com` — advertising network

#### Outcome

User A was advised to:
1. Immediately enable Airplane Mode
2. Backup essential photos via USB (not cloud sync)
3. Factory reset the device
4. Change all passwords from a different device
5. Enable 2FA on all accounts
6. File a report with local authorities

Post-factory-reset scan showed zero suspicious connections — only normal Android traffic and Xiaomi telemetry.

For additional case studies, see [docs/case-studies.md](docs/case-studies.md).

---

## Technology Stack

| Component | Technology | Version | Why This Choice |
|-----------|-----------|---------|-----------------|
| **IDS Engine** | [Suricata](https://suricata.io/) | 7.x | Industry-standard IDS/IPS. 18,987 rules from Emerging Threats Open. Handles gigabit traffic with multi-threading. EVE JSON output integrates cleanly with our analysis pipeline. |
| **VPN Protocol** | VLESS + Reality | xray-core 1.8.x | Censorship-resistant protocol. Reality TLS fingerprint makes VPN traffic indistinguishable from normal HTTPS to DPI systems. Critical for users in restrictive networks. |
| **VPN Panel** | [3x-ui](https://github.com/MHSanaei/3x-ui) | Latest | Web panel for xray-core. Provides API for programmatic client creation/deletion. Enables bot to auto-provision and revoke VPN credentials. |
| **Network Monitor** | [Zeek](https://zeek.org/) | 6.x | Generates structured connection logs (conn.log), DNS logs (dns.log), SSL logs (ssl.log). Complements Suricata's alert-based approach with connection-level metadata. |
| **Bot Framework** | [aiogram](https://github.com/aiogram/aiogram) | 3.x | Async Telegram bot framework for Python. FSM (Finite State Machine) support for multi-step user flows. High performance, modern API. |
| **Language** | Python | 3.12 | Primary language for all analysis components. Rich ecosystem for network analysis (scapy, dpkt). Async support via asyncio for concurrent scan handling. |
| **AI / LLM** | [Groq](https://groq.com/) (LLaMA 3.3 70B) | API | Ultra-fast inference for real-time report generation. ~500ms response time for scan reports. Free tier sufficient for current usage. |
| **AI / LLM (fallback)** | Google Gemini | API | Fallback LLM when Groq rate limit is reached. Slightly slower but higher quality for complex analysis narratives. |
| **Database** | SQLite | 3.x | Lightweight, serverless, zero-config. Perfect for single-server deployment. Tables: users, scans, device_vendors, scan_results. |
| **Threat Intel** | [AbuseIPDB](https://www.abuseipdb.com/) | API v2 | IP reputation database. Checks if destination IPs have been reported for malicious activity. Provides confidence score and abuse categories. |
| **Threat Intel** | [AlienVault OTX](https://otx.alienvault.com/) | API v2 | Open Threat Exchange. Provides pulse-based threat intelligence. Checks IPs/domains against community-contributed indicators. |
| **Stalkerware DB** | [AssoEchap](https://github.com/AssoEchap/stalkerware-indicators) | Latest | Open-source stalkerware indicator database. 172 families, 919+ domains. Updated by community of anti-stalkerware researchers. |

### Project Structure

```
bot/
  bot.py                  — Telegram bot core (aiogram 3.x, FSM states)
  scan_manager.py         — Scan lifecycle: provision → capture → analyze → report → cleanup
  vless_manager.py        — VLESS client management via 3x-ui API
  database.py             — SQLite: users, scans, device_vendors, scan_results

analysis/
  malware_detector.py     — Three-layer detection engine (ports → behavior → blacklists)
  traffic_classifier.py   — Domain categorization (CDN, social, telemetry, ad, unknown)
  ai_analyzer.py          — LLM-based report generation (user_level adaptive)
  threat_lookup.py        — External API queries (AbuseIPDB, OTX, VirusTotal)
  blacklists/
    stalkerware.txt       — 919 domains from AssoEchap
    mining_pools.txt      — Known mining pool domains
    dyndns_providers.txt  — Dynamic DNS domains (C2 infrastructure indicator)

scanner/
  suricata_parser.py      — Suricata EVE JSON parser (alerts + flow records)
  xray_parser.py          — xray-core access.log parser (connection metadata)
  zeek_parser.py          — Zeek log parser (conn.log, dns.log, ssl.log)
```

---

## Suricata IDS Integration

Suricata runs with the [Emerging Threats Open](https://rules.emergingthreats.net/) ruleset — a community-maintained set of 18,987 IDS signatures.

### Relevant Rule Categories for Mobile Threat Detection

| Rule Category | Rule Count (approx.) | What It Covers |
|--------------|---------------------|----------------|
| **ET MOBILE_MALWARE** | ~200 | Android-specific malware C2 signatures. Covers SpyNote, AhMyth, AndroRAT, Anubis banker, Cerberus, and other Android trojans. Matches on network-level indicators (C2 beacons, exfiltration patterns). |
| **ET TROJAN** | ~5,000 | General trojan C2 signatures. Covers RATs, bankers, infostealers. Many applicable to mobile malware using shared C2 infrastructure. |
| **ET MALWARE** | ~3,500 | Broader malware signatures including miners, droppers, loaders. Covers Stratum mining protocol, known malicious domain lookups. |
| **ET DNS** | ~500 | DNS-based indicators. Dynamic DNS lookups, DNS tunneling, known malicious domain queries. |
| **ET POLICY** | ~800 | Policy violations: Tor usage, proxy connections, cryptocurrency activity. Useful for detecting unexpected behavior on mobile. |
| **ET INFO** | ~2,000 | Informational rules: suspicious user-agents, unusual protocols, certificate anomalies. Provides context for behavioral analysis. |
| **ET HUNTING** | ~400 | Threat hunting rules: broader pattern matching for emerging threats. Higher false positive rate but catches novel malware. |

### Example Suricata Rules (Mobile-Specific)

```
# SpyNote RAT C2 Beacon
alert tcp $HOME_NET any -> $EXTERNAL_NET 7771 (
    msg:"ET MOBILE_MALWARE Android/SpyNote CnC Beacon";
    flow:established,to_server;
    content:"|1f 8b|";  # GZip magic bytes
    sid:2036345; rev:1;
)

# AhMyth RAT Socket.IO Heartbeat
alert http $HOME_NET any -> $EXTERNAL_NET any (
    msg:"ET MOBILE_MALWARE Android/AhMyth CnC Checkin";
    flow:established,to_server;
    content:"socket.io"; http_uri;
    content:"EIO="; http_uri;
    sid:2036789; rev:1;
)

# Stratum Mining Protocol Detection
alert tcp $HOME_NET any -> any [3333,5555,7777,14444,45560] (
    msg:"ET POLICY Cryptocurrency Miner Stratum Protocol";
    flow:established,to_server;
    content:"mining.subscribe";
    sid:2024792; rev:3;
)
```

---

## Open Source Integrations

This project builds on the work of several open-source projects and research initiatives:

| Project | How We Use It | Link |
|---------|--------------|------|
| **AssoEchap/stalkerware-indicators** | Primary stalkerware domain database. 919 domains, 172 families. We parse their hosts file format and update weekly. | [GitHub](https://github.com/AssoEchap/stalkerware-indicators) |
| **Emerging Threats Open** | Suricata ruleset. 18,987 signatures including ET MOBILE_MALWARE category specifically for Android threats. | [rules.emergingthreats.net](https://rules.emergingthreats.net/) |
| **MVT (Mobile Verification Toolkit)** | Reference for Pegasus IoC patterns. Our scanner covers network-layer indicators; MVT covers device forensics. Complementary tools. | [GitHub](https://github.com/mvt-project/mvt) |
| **Suricata** | Core IDS engine. We use EVE JSON output for structured alert processing. | [suricata.io](https://suricata.io/) |
| **Zeek** | Network metadata generation. conn.log provides connection-level statistics for behavioral analysis. | [zeek.org](https://zeek.org/) |
| **AbuseIPDB** | IP reputation lookups. We query destination IPs to correlate with known malicious infrastructure. | [abuseipdb.com](https://www.abuseipdb.com/) |
| **AlienVault OTX** | Open threat exchange. Community-contributed threat intelligence for IP/domain enrichment. | [otx.alienvault.com](https://otx.alienvault.com/) |
| **MITRE ATT&CK Mobile** | Threat classification framework. We map findings to ATT&CK Mobile technique IDs for standardized reporting. | [attack.mitre.org/mobile](https://attack.mitre.org/matrices/mobile/) |

---

## Comparison with Existing Solutions

| Feature | **Security Scanner Bot** | **MVT** (Amnesty) | **PiRogue** (PTS) | **Commercial Antivirus** |
|---------|------------------------|-------------------|-------------------|------------------------|
| **Setup required** | None — just connect VPN | Requires USB + CLI expertise | Requires Raspberry Pi hardware | Install app on device |
| **Target user** | Anyone (Telegram bot) | Security researchers | Technical users | Everyone |
| **Detection method** | Network traffic analysis | Device forensic artifacts | Network + device analysis | On-device signature scan |
| **RAT detection** | Yes (port + behavioral) | Yes (file artifacts) | Yes (network) | Limited (signature only) |
| **Stalkerware** | Yes (919 domain DB) | Yes (IoC-based) | Yes (IoC-based) | Some (varies by vendor) |
| **Crypto miner** | Yes (Stratum protocol) | No | Yes (network) | Yes (signature) |
| **Behavioral analysis** | Yes (beaconing, exfil) | No (forensic only) | Yes | No |
| **Manufacturer telemetry** | Yes (classified separately) | No | Partial | No |
| **Requires device access** | No (network-only) | Yes (USB/backup) | Yes (Wi-Fi routing) | Yes (installed app) |
| **Works on iOS** | Yes (via VPN) | Yes (iTunes backup) | Yes (network) | Limited (iOS restrictions) |
| **Real-time** | Yes (during VPN session) | No (post-incident) | Yes | Yes (on-device) |
| **AI reports** | Yes (adaptive to user level) | No (raw IoCs) | No (technical output) | Basic (generic alerts) |
| **Open source** | Showcase (this repo) | Fully open source | Fully open source | Proprietary |
| **Cost** | Free | Free | ~$100 (hardware) | $30-80/year |

### Key Differentiators

1. **Zero install on target device** — Only requires VPN connection, no app installation, no USB access, no jailbreak/root
2. **Accessible to non-technical users** — Telegram bot interface with AI-generated plain-language reports
3. **Three-layer analysis** — Combines signature matching (Suricata), behavioral analysis, and threat intelligence correlation
4. **Manufacturer telemetry awareness** — Separately classifies vendor telemetry so users understand the full picture
5. **Adaptive reporting** — Same finding explained differently for beginners vs. security professionals

---

## API and Extensibility

The scanner architecture is designed for extensibility. Key integration points:

### Scan Results API (Internal)

```python
# Scan result structure returned by MalwareDetector
{
    "scan_id": "uuid-v4",
    "timestamp": "2025-01-15T10:30:00Z",
    "duration_seconds": 312,
    "device_type": "android",
    "total_connections": 487,
    "findings": [
        {
            "id": "finding-001",
            "layer": 1,  # Which detection layer triggered
            "severity": "critical",  # critical, high, medium, info
            "category": "rat_c2",
            "port": 22,
            "protocol": "SSH",
            "dst_ip": "198.51.100.10",
            "dst_asn": "AS62904",
            "dst_country": "NL",
            "description": "SSH outbound — RAT C2 tunnel",
            "mitre_techniques": ["T1437.001", "T1521"],
            "confidence": 0.95,
            "evidence": {
                "beaconing_cv": 0.149,
                "interval_avg": 58.3,
                "bytes_out": 247000,
                "bytes_in": 12000,
                "suricata_sids": [2036345]
            }
        }
    ],
    "telemetry": [
        {
            "vendor": "xiaomi",
            "domain": "tracking.miui.com",
            "category": "browser_tracking",
            "privacy_note": "Sends browsing history including incognito"
        }
    ],
    "summary": {
        "critical": 2,
        "high": 3,
        "medium": 1,
        "info": 12
    }
}
```

### Future Integration Points

- **Webhook notifications** — POST scan results to external endpoint
- **STIX2 export** — Export findings in STIX2 format for threat intelligence platforms
- **MISP integration** — Automatic IoC sharing with MISP instances
- **Syslog/SIEM** — Forward alerts to SIEM systems (Splunk, ELK, QRadar)
- **Custom blacklists** — User-provided domain/IP blacklists for targeted detection
- **Multi-tenant API** — REST API for organizations to run scans programmatically

---

## Future Roadmap

### Short-Term (Q1-Q2 2026)

- [ ] **iOS-specific detection rules** — Apple ecosystem telemetry classification, iCloud Private Relay detection
- [ ] **WireGuard VPN option** — Alternative to VLESS for users who prefer WireGuard
- [ ] **Scheduled recurring scans** — Users can set daily/weekly automated scans
- [ ] **PDF report export** — Downloadable scan reports with charts and visualizations
- [ ] **Expanded stalkerware database** — Integration with additional indicator sources beyond AssoEchap

### Medium-Term (Q3-Q4 2026)

- [ ] **VirusTotal integration** — Check file hashes and domains against VT database
- [ ] **DNS-over-HTTPS analysis** — Detect and analyze DoH traffic for hidden DNS queries
- [ ] **STIX2/MISP export** — Standardized threat intelligence output for security teams
- [ ] **Multi-language support** — Full localization (currently English and Russian)
- [ ] **Baseline learning** — Build per-device "normal" traffic profile to detect anomalies

### Long-Term (2027)

- [ ] **Machine learning behavioral models** — Train models on known-malware traffic patterns for zero-day detection
- [ ] **Organizational dashboard** — Web interface for IT teams to manage fleet scans
- [ ] **Hardware appliance** — Dedicated device (like PiRogue) for always-on home network monitoring
- [ ] **API marketplace** — Third-party detection rule plugins

---

## Documentation

| Document | Description |
|----------|------------|
| [Architecture](docs/architecture.md) | Detailed component descriptions with data flow diagrams |
| [Detection Rules](docs/detection-rules.md) | Complete reference of all detection rules — ports, behaviors, blacklists |
| [Device Telemetry](docs/device-telemetry.md) | Manufacturer telemetry domains database with privacy analysis |
| [Case Studies](docs/case-studies.md) | Anonymized real-world case studies showing scanner findings |
| [Mobile Malware Research](docs/research-mobile-malware-signatures.md) | Research on network signatures of mobile malware families |

---

## Try It

[@secure_scanbot](https://t.me/secure_scanbot) — the bot is live 24/7

---

## License

[MIT](LICENSE)

---

*Built by [Creatman](https://github.com/CreatmanCEO) — Making mobile security accessible to everyone.*
