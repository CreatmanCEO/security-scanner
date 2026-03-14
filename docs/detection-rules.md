# Detection Rules — Complete Reference

This document is the authoritative reference for all detection rules used by Security Scanner Bot's three-layer analysis engine.

---

## Layer 1: Port-Based Detection

### How It Works

Every connection observed during a scan is checked against a database of known threat ports. Mobile phones are consumer devices — they should only connect to standard web/app ports. Any connection to a server administration port, industrial protocol port, or known malware port is flagged.

### Critical Severity Ports

These ports on a mobile device indicate near-certain compromise.

| Port | Protocol | Threat Category | Malware Families | Detection Rationale |
|------|----------|----------------|-----------------|-------------------|
| 22 | SSH | Backdoor / RAT C2 tunnel | SpyNote, custom RATs | Mobile phones never initiate SSH. Outbound SSH = reverse tunnel giving attacker encrypted persistent access. Most common finding in compromised devices. |
| 23 | Telnet | Backdoor | IoT botnets, rootkits | Unencrypted remote shell. Worse than SSH — credentials visible in plaintext. On mobile = kernel-level compromise or botnet component. |
| 179 | BGP | Rootkit / Botnet | Advanced rootkits | Border Gateway Protocol handles internet routing between ISPs. Physically impossible for a phone to participate in BGP. Indicates kernel rootkit or advanced botnet. |
| 554 | RTSP | Camera/mic surveillance | Surveillance RATs | Real Time Streaming Protocol delivers live video/audio. On mobile = attacker streaming camera/microphone feed. Extremely invasive. |
| 4444 | TCP | Metasploit reverse shell | Metasploit/Meterpreter | Default Metasploit payload handler port. Outbound 4444 = phone was exploited and is calling back to attacker. Classic penetration testing tool abused in real attacks. |
| 5555 | ADB | Full device control | ADB.Miner worm, manual compromise | Android Debug Bridge over network. Grants complete device control: app install, file access, shell commands. ADB.Miner worm actively scans for this port. |
| 1337 | TCP | RAT C2 | AndroRAT, DenDroid | "Leet" port, default for multiple Android RAT families. AndroRAT: raw TCP polling. DenDroid: HTTP POST to PHP. Both provide full device control. |
| 42474 | HTTP/WS | RAT C2 | AhMyth | Default AhMyth RAT C2 port. Open-source RAT using Socket.IO with heartbeat. Popular with low-sophistication attackers due to YouTube tutorials. |
| 7771 | Binary TCP | RAT C2 | SpyNote/CypherRAT | Primary SpyNote C2 port. Most prevalent Android RAT (2023-2025). Binary protocol with GZip compression. Provides camera, mic, SMS, GPS, keylogger, file access. |
| 7775 | Binary TCP | RAT C2 | SpyNote (alternate) | Secondary SpyNote port. Same protocol. Used when primary is blocked or for load distribution across C2 infrastructure. |
| 8888 | HTTP/TCP | RAT C2 | SpyNote (alternate), various | Third SpyNote port. Also used by other malware families for HTTP-based C2. Port sometimes used legitimately (e.g., some proxy software). Context matters. |
| 2222 | SSH/TCP | RAT C2 / SSH alternate | SpyNote, SSH backdoors | Common alternative SSH port used by both RATs and manual backdoors. SpyNote variants use this alongside their primary ports. |
| 6667 | IRC | Botnet C2 | IRC bots | Default IRC port. Phones almost never use IRC legitimately. Bots join IRC channels to receive commands — classic botnet architecture dating back 20+ years. |
| 6697 | IRC/TLS | Botnet C2 (encrypted) | Sophisticated IRC bots | TLS-encrypted IRC. Same botnet pattern but encrypted. Indicates more sophisticated botnet that evades content inspection. |
| 9001 | TCP | Tor relay / hidden C2 | Tor-embedded malware | Default Tor relay port. If user has no Tor app = malware embedded its own Tor client to anonymize C2. Common in banking trojans and ransomware. |
| 9030 | TCP | Tor directory | Tor-embedded malware | Tor directory authority port. Same implication as 9001. Connection here means embedded Tor client is bootstrapping. |

### High Severity Ports

These ports are likely malicious but have some edge cases where they might be legitimate.

| Port | Protocol | Threat Category | Detection Rationale | False Positive Notes |
|------|----------|----------------|-------------------|---------------------|
| 3333 | Stratum | Crypto mining | Primary Stratum protocol port for cryptocurrency mining. Connection to 3333 with Stratum JSON-RPC = phone mining crypto for attacker. | Some game servers use 3333. Check for Stratum protocol markers. |
| 5555 | Stratum/ADB | Mining / ADB | Dual threat: mining pool alternate port AND Android Debug Bridge. Either way, should not be active on consumer device. | Developer devices may have ADB enabled intentionally. |
| 7777 | Stratum | Crypto mining | Alternative mining pool port. Used by hashvault.pro and others. | Some game servers and apps use 7777. Check protocol. |
| 14444 | Stratum/SSL | Crypto mining (encrypted) | SSL-encrypted Stratum mining. Used by MoneroOcean, Nanopool for encrypted mining connections. | Very unlikely to be legitimate on mobile. |
| 45560 | Stratum | Crypto mining (Monero) | Monero-specific mining port. Used by supportxmr.com and other Monero pools. | Almost never legitimate on mobile. |
| 30000-40000 | Various | NSO Pegasus range | NSO Group's Pegasus spyware uses high-numbered ports in this range for C2 communication. Combined with CloudFront infrastructure patterns = high-confidence Pegasus indicator. | Many legitimate services use ports in this range. Must be combined with other indicators. |
| 8080 | HTTP | Various malware HTTP C2 | Alternative HTTP port. Many RATs use 8080 for HTTP-based C2 to blend with proxy traffic. | Legitimate: some APIs and web services use 8080. Context-dependent. |
| 1080 | SOCKS | Proxy tunnel | SOCKS proxy port. On mobile = traffic is being tunneled through external proxy, possibly for exfiltration or as part of proxy botnet. | Some VPN apps use SOCKS. Check if user-intended. |
| 3128 | HTTP proxy | Proxy tunnel | Default Squid proxy port. Same proxy/botnet implications as 1080. | Corporate proxy configurations. Rare on mobile. |
| 5900 | VNC | Remote desktop | VNC remote desktop protocol. On mobile = visual remote access to device screen. | Some legitimate remote support apps use VNC. |
| 3389 | RDP | Remote desktop | Windows Remote Desktop Protocol. On mobile = extremely unusual, potential proxy to compromised RDP host. | Almost never legitimate on mobile. |

### Medium Severity Ports

| Port | Protocol | Threat Category | Detection Rationale |
|------|----------|----------------|-------------------|
| 8443 | HTTPS alt | Suspicious web | Alternative HTTPS. Some C2 uses 8443 to avoid standard port monitoring. Also used by legitimate APIs. |
| 25 | SMTP | Spam relay | Mail sending from phone = potential spam bot or data exfiltration via email. |
| 587 | SMTP/TLS | Email send | Encrypted mail sending. Could be legitimate email client or exfiltration channel. |
| 161 | SNMP | Network probing | Network management protocol. No reason for a phone to use SNMP. |
| 445 | SMB | Worm/lateral movement | Windows file sharing. If phone connects to SMB = worm behavior or proxy to internal network. |
| 1433 | MSSQL | Database access | SQL Server port. Phone accessing database directly = data theft or misconfigured app. |
| 3306 | MySQL | Database access | MySQL port. Same concern as 1433. |

### Whitelisted (Normal) Ports

| Port | Protocol | Purpose | Why It's Normal |
|------|----------|---------|----------------|
| 53 | DNS | Name resolution | Every app resolves domains. Standard behavior. |
| 80 | HTTP | Web traffic | Unencrypted web. Still used by some apps and CDNs. |
| 443 | HTTPS | Encrypted web | Primary port for almost all modern app traffic. Expected on every device. |
| 853 | DoT | DNS over TLS | Android 9+ Private DNS feature. Privacy-enhancing behavior. |
| 5228 | TCP | Google FCM | Firebase Cloud Messaging — Android push notifications. Essential service. |
| 5229 | TCP | Google FCM (fallback) | FCM fallback when 5228 blocked. |
| 5230 | TCP | Google FCM (fallback) | FCM second fallback. |
| 123 | UDP | NTP | Time synchronization. Every device periodically syncs clock. |
| 5223 | TCP | Apple APNS | Apple Push Notification Service for iOS. |
| 5222 | TCP | XMPP | Messaging protocol. Used by some chat apps. |
| 993 | IMAP/TLS | Email fetch | Encrypted email retrieval. Normal for email clients. |
| 995 | POP3/TLS | Email fetch | Encrypted email retrieval (POP3). Normal for email clients. |

---

## Layer 2: Behavioral Detection

### Rule B1: Beaconing Detection (C2 Callback)

**Purpose:** Detect malware periodically phoning home to its command-and-control server.

**Algorithm:**
```
FOR each unique destination IP:
    connections = get_connections_to(dst_ip)
    IF len(connections) < MIN_CONNECTIONS (10):
        SKIP  # Not enough data

    intervals = calculate_intervals(connections)
    mean_interval = mean(intervals)
    std_interval = std(intervals)
    cv = std_interval / mean_interval  # Coefficient of Variation

    IF cv < CV_THRESHOLD (0.30) AND
       MIN_INTERVAL (30s) < mean_interval < MAX_INTERVAL (900s):

        # Jitter analysis
        jitter_pct = std_interval / mean_interval * 100
        IF jitter_pct < 50:  # Malware typically adds 10-50% jitter
            ALERT: Beaconing detected
            confidence = 1.0 - cv  # Lower CV = higher confidence
```

**Parameters:**
| Parameter | Value | Rationale |
|-----------|-------|-----------|
| MIN_CONNECTIONS | 10 | Need enough samples for statistical significance in 5-min window |
| CV_THRESHOLD | 0.30 | Below 0.30 = highly regular intervals. Human browsing is CV > 0.8 |
| MIN_INTERVAL | 30 seconds | Shorter = likely keepalive. Longer = less detectable but still functional |
| MAX_INTERVAL | 900 seconds | 15 minutes. Longer intervals need longer scan windows |
| JITTER_TOLERANCE | 50% | Most malware adds 10-50% randomization |

**False positive mitigations:**
- Exclude known CDN IPs (Cloudflare, Akamai, Fastly)
- Exclude Google/Apple push notification servers
- Exclude NTP servers (port 123)
- Require destination to be non-whitelisted

### Rule B2: Data Exfiltration Detection

**Purpose:** Detect malware uploading stolen data (contacts, SMS, photos, files) to an external server.

**Algorithm:**
```
FOR each unique destination IP (non-whitelisted):
    total_upload = sum(bytes_out for connections to dst_ip)
    total_download = sum(bytes_in for connections to dst_ip)

    ratio = total_upload / max(total_download, 1)

    IF ratio > EXFIL_RATIO_THRESHOLD (3.0):
        IF total_upload > MIN_EXFIL_BYTES (1_000_000):  # 1 MB
            ALERT: Data exfiltration suspected
            severity = HIGH
        ELIF total_upload > 100_000:  # 100 KB
            ALERT: Possible data exfiltration
            severity = MEDIUM

    # Time-of-day correlation
    IF connections occur primarily during 00:00-06:00 local time:
        boost_confidence(+0.2)  # Nighttime exfil is common pattern
```

**Parameters:**
| Parameter | Value | Rationale |
|-----------|-------|-----------|
| EXFIL_RATIO_THRESHOLD | 3.0 | Upload 3x more than download = not normal browsing |
| MIN_EXFIL_BYTES (high) | 1 MB | Significant data upload in 5-min window |
| MIN_EXFIL_BYTES (medium) | 100 KB | Smaller but still suspicious |
| NIGHTTIME_BOOST | +0.2 confidence | Malware often exfiltrates during charging/sleep |

### Rule B3: Streaming Detection (Camera/Microphone)

**Purpose:** Detect real-time camera or microphone streaming to an attacker.

**Algorithm:**
```
FOR each sustained connection (duration > 30 seconds):
    IF dst_ip NOT in streaming_whitelist:
        bitrate = bytes_out / duration

        # Video streaming signature
        IF 200_000 < bitrate < 800_000:  # 200-800 Kbps
            IF bitrate_variance < 0.3:   # Consistent rate
                ALERT: Possible video streaming (camera)
                severity = CRITICAL

        # Audio streaming signature
        IF 16_000 < bitrate < 128_000:   # 16-128 Kbps
            IF bitrate_variance < 0.3:
                ALERT: Possible audio streaming (microphone)
                severity = CRITICAL

        # RTSP detection (any port)
        IF connection contains RTSP markers:
            ALERT: RTSP streaming detected
            severity = CRITICAL
```

**Streaming whitelist (legitimate services):**
- YouTube upload endpoints
- Twitch/Kick streaming endpoints
- Instagram/TikTok live endpoints
- Zoom/Teams/Google Meet endpoints
- Spotify/Apple Music (download direction only)

### Rule B4: Keylogger Traffic Pattern

**Purpose:** Detect keylogging software that sends captured keystrokes to a remote server.

**Algorithm:**
```
FOR each destination IP with multiple small connections:
    small_payloads = [c for c in connections if c.bytes_out < 1024]

    IF len(small_payloads) > KEYLOG_MIN_PACKETS (20):
        avg_size = mean(c.bytes_out for c in small_payloads)
        frequency = len(small_payloads) / scan_duration_minutes

        IF avg_size < 512 AND frequency > 5 per minute:
            ALERT: Keylogger traffic pattern
            severity = HIGH
            evidence = {
                "avg_payload_size": avg_size,
                "frequency_per_min": frequency,
                "total_packets": len(small_payloads)
            }
```

### Rule B5: DNS Tunneling Detection

**Purpose:** Detect data exfiltration or C2 communication hidden in DNS queries.

**Algorithm:**
```
FOR each base domain in DNS queries:
    subdomains = get_unique_subdomains(base_domain)

    IF len(subdomains) > DNS_TUNNEL_THRESHOLD (50):
        avg_subdomain_length = mean(len(s) for s in subdomains)
        entropy = calculate_entropy(concatenated_subdomains)

        IF avg_subdomain_length > 30 AND entropy > 3.5:
            ALERT: DNS tunneling suspected
            severity = HIGH
            # High-entropy, long subdomains = encoded data in DNS
```

---

## Layer 3: Blacklist Detection

### Stalkerware Domain Database

**Source:** [AssoEchap/stalkerware-indicators](https://github.com/AssoEchap/stalkerware-indicators)
**Count:** 919 domains from 172 stalkerware families
**Update frequency:** Weekly automated pull
**Format:** Loaded as hash set for O(1) lookup

**Top stalkerware families by domain count:**

| Family | Domain Count | Primary Capabilities |
|--------|-------------|---------------------|
| TheTruthSpy / Copy9 | 15+ | GPS, calls, SMS, camera, browser history |
| FlexiSpy | 10+ | Call interception, ambient recording, full control |
| Cocospy / Spyzie | 12+ | Social media monitoring, GPS, call logs |
| Hoverwatch | 8+ | Screenshots, call recording, location tracking |
| mSpy | 10+ | Messenger monitoring, keylogging, GPS |
| SpyHide | 5+ | Hidden GPS tracking, call recording |
| Cerberus | 5+ | Anti-theft features repurposed for stalking |
| iKeyMonitor | 8+ | Keylogging, screenshots, social media capture |
| KidsGuard | 10+ | Marketed as parental control, used as stalkerware |
| Spyic | 8+ | Real-time location, message monitoring |

**Detection rule:**
```
FOR each domain in observed_dns_queries:
    IF domain in stalkerware_domains OR
       any_parent_domain(domain) in stalkerware_domains:
        ALERT: Stalkerware communication detected
        severity = CRITICAL
        family = lookup_family(domain)
```

### Mining Pool Domain Database

**Count:** 50+ domains covering major mining pools
**Focus:** Monero (XMR) pools — most common mobile mining target due to CPU-friendly algorithm

| Domain Pattern | Pool | Coins |
|---------------|------|-------|
| `*.moneroocean.stream` | MoneroOcean | XMR |
| `*.nanopool.org` | Nanopool | XMR, ETH, ETC |
| `*.hashvault.pro` | HashVault | XMR |
| `*.supportxmr.com` | SupportXMR | XMR |
| `*.minergate.com` | MinerGate | Multi |
| `*.f2pool.com` | F2Pool | Multi |
| `*.2miners.com` | 2Miners | Multi |
| `*.herominers.com` | HeroMiners | Multi |
| `*.minexmr.com` | MineXMR | XMR |
| `*.xmrpool.eu` | XMR Pool EU | XMR |

**Detection rule:**
```
FOR each domain in observed_dns_queries:
    IF domain in mining_pool_domains:
        ALERT: Cryptocurrency mining pool connection
        severity = HIGH
        pool = identify_pool(domain)

    # Stratum protocol detection (domain-independent)
    IF connection contains "mining.subscribe" OR "mining.authorize":
        ALERT: Stratum mining protocol detected
        severity = HIGH
```

### Dynamic DNS Provider Database

**Purpose:** Dynamic DNS is heavily abused for C2 infrastructure because domains are free, anonymous, and can be re-pointed instantly.

| Provider | Domain Patterns | Abuse Level |
|----------|---------------|------------|
| Duck DNS | `*.duckdns.org` | Very High — #1 abused DDNS for Android RATs |
| No-IP | `*.no-ip.org`, `*.no-ip.com`, `*.no-ip.biz` | High |
| Dynu | `*.dynu.com`, `*.dynu.net` | High |
| FreeDNS | `*.freedns.afraid.org` | High |
| No-IP family | `*.hopto.org`, `*.zapto.org`, `*.sytes.net` | High |
| ChangeIP | `*.changeip.com` | Medium |
| DNS Exit | `*.dnsexit.com` | Medium |

**Detection rule:**
```
FOR each domain in observed_dns_queries:
    IF domain matches any DDNS_PROVIDER pattern:
        ALERT: Dynamic DNS connection — possible C2 infrastructure
        severity = HIGH
        note = "Legitimate apps do not use Dynamic DNS"
```

### Known Malware Infrastructure

Additional domains and IP ranges associated with known malware campaigns. Updated from threat intelligence feeds (OTX, AbuseIPDB).

**Detection rule:**
```
FOR each (domain, ip) in observed_connections:
    abuse_score = query_abuseipdb(ip)
    otx_pulses = query_otx(ip, domain)

    IF abuse_score > 80:
        ALERT: Connection to known malicious IP
        severity = HIGH

    IF otx_pulses contains mobile_malware_tags:
        ALERT: Connection to threat-intel-flagged infrastructure
        severity = HIGH
```

---

## Rule Interaction and Severity Escalation

When multiple layers detect the same connection, severity is escalated:

| Combination | Resulting Severity | Example |
|------------|-------------------|---------|
| Layer 1 (port) + Layer 2 (beaconing) | CRITICAL (escalated) | Port 7771 + regular interval = confirmed SpyNote C2 |
| Layer 1 (port) + Layer 3 (blacklist) | CRITICAL (confirmed) | Port 22 + DuckDNS domain = confirmed RAT tunnel |
| Layer 2 (behavior) + Layer 3 (blacklist) | CRITICAL (confirmed) | Beaconing + stalkerware domain = confirmed stalkerware |
| Layer 1 + Layer 2 + Layer 3 | CRITICAL (highest confidence) | All three layers agree = maximum confidence finding |
| Layer 1 only (unusual port) | HIGH | Suspicious port without behavioral/blacklist confirmation |
| Layer 2 only (behavior anomaly) | MEDIUM-HIGH | Anomalous behavior without port/blacklist match |
| Layer 3 only (blacklist match) | HIGH-CRITICAL | Known bad domain/IP, severity depends on category |

---

## MITRE ATT&CK Mobile Mapping

Each detection rule maps to MITRE ATT&CK Mobile techniques for standardized classification:

| Detection | MITRE Technique | ID |
|-----------|----------------|-----|
| SSH outbound (RAT tunnel) | Application Layer Protocol | T1437.001 |
| Encrypted C2 channel | Encrypted Channel | T1521 |
| Data exfiltration over C2 | Exfiltration Over C2 Channel | T1646 |
| Camera/mic streaming | Audio Capture / Video Capture | T1429 / T1512 |
| Keylogger pattern | Input Capture: Keylogging | T1417.001 |
| SMS exfiltration | SMS Messages | T1636.004 |
| Mining | Resource Hijacking | T1496 |
| Beaconing (scheduled C2) | Scheduled Task/Job | T1603 |
| DDNS for C2 | Dynamic Resolution | T1637 |
| Stalkerware install | Application Discovery | T1418 |
