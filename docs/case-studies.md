# Case Studies — Real-World Scanner Findings

All case studies are anonymized. IP addresses use documentation ranges (RFC 5737: 192.0.2.0/24, 198.51.100.0/24, 203.0.113.0/24). Device identifiers and user information have been removed.

---

## Case Study 1: 26 SSH Connections on a Xiaomi Device

### Background

**Device:** Xiaomi Redmi Note (Android 13, MIUI 14)
**User complaint:** Rapid battery drain (full to 20% in 3 hours with light use), device warm when idle, unexplained mobile data spikes of 2-3 GB per week beyond normal usage.
**Scan duration:** 5 minutes

### Findings Summary

| Severity | Count | Category |
|----------|-------|----------|
| CRITICAL | 26 | RAT C2 connections |
| HIGH | 4 | Dynamic DNS (C2 infrastructure) |
| INFO | 8 | Manufacturer telemetry |
| NORMAL | 449 | Legitimate traffic |

**Total connections observed:** 487
**Unique destination IPs:** 67

### Critical Findings — Detailed Breakdown

#### Finding 1: SSH Outbound Connections (14 instances)

```
Type:         SSH outbound (dst port 22)
Instances:    14 connections to 14 unique IPs
IP Range:     198.51.100.0/24 (14 unique IPs across 4 countries)
Countries:    Netherlands (6), Germany (4), Singapore (2), USA (2)
Hosting:      All on low-cost VPS providers (DigitalOcean, Hetzner, Vultr)
Interval:     45.2s average (σ=6.8s, CV=0.15)
Jitter:       ~15% — consistent with automated beaconing
Bytes out:    2.1 MB total across all connections
Bytes in:     94 KB total
Ratio:        22:1 upload-to-download
```

**Analysis:** 14 simultaneous SSH outbound connections with highly regular beaconing intervals. The coefficient of variation of 0.15 is far below the 0.30 threshold, confirming automated behavior. The 22:1 upload ratio indicates active data exfiltration. No legitimate mobile application maintains 14 concurrent SSH connections.

#### Finding 2: SpyNote C2 Ports (12 instances)

```
Type:         SpyNote/CypherRAT C2
Instances:    8 on port 7771, 4 on port 7775
IP Range:     203.0.113.0/24 (8 unique IPs)
Countries:    Russia (5), Ukraine (3)
Protocol:     Binary TCP with GZip compression (0x1f 0x8b header)
Interval:     30.1s average (σ=3.2s, CV=0.11)
Bytes out:    2.1 MB total
Bytes in:     86 KB total
```

**Analysis:** Port 7771 and 7775 are default SpyNote RAT ports. The GZip-compressed binary protocol matches known SpyNote traffic patterns. Beaconing CV of 0.11 indicates near-perfect regularity — the malware is checking in with its C2 every ~30 seconds.

#### Finding 3: Dynamic DNS Resolution

```
Type:         Dynamic DNS C2 infrastructure
Domains:      4 unique *.duckdns.org subdomains
Resolution:   Mapped to 4 of the SSH destination IPs
TTL:          60 seconds (typical of DDNS)
```

**Analysis:** Four of the 14 SSH destinations were resolved via DuckDNS, the most heavily abused Dynamic DNS service for Android RATs. DDNS allows attackers to change their C2 server IP without updating the malware.

### Behavioral Analysis Results

| Behavior | Detected | Confidence |
|----------|----------|------------|
| Beaconing (C2 callback) | YES | 0.95 |
| Data exfiltration | YES | 0.89 |
| Camera/mic streaming | NO | — |
| Keylogger pattern | POSSIBLE | 0.45 |
| DNS tunneling | NO | — |

### Telemetry (Informational — Not Malware)

| Domain | Vendor | Category |
|--------|--------|----------|
| tracking.miui.com | Xiaomi | Browser history tracking |
| data.mistat.xiaomi.com | Xiaomi | Usage statistics |
| api.ad.xiaomi.com | Xiaomi | Advertising network |
| sdkconfig.ad.xiaomi.com | Xiaomi | Ad configuration |
| android.clients.google.com | Google | Device check-in |
| play.googleapis.com | Google | Play Services |
| connectivitycheck.gstatic.com | Google | Connectivity check |
| mtalk.google.com | Google | FCM push notifications |

### Timeline Reconstruction

Based on connection timestamps and patterns:

1. **Malware was likely installed 2-4 weeks prior** (based on infrastructure maturity — multiple C2 IPs suggest established campaign)
2. **Data exfiltration peaks during 2 AM - 6 AM** (charging hours, screen off)
3. **C2 infrastructure spans 6 countries** indicating organized operation, not script kiddie
4. **SSH + SpyNote dual protocol** suggests custom-modified SpyNote variant using SSH as backup channel

### Recommendations Provided

1. Enable Airplane Mode immediately
2. Do NOT factory reset yet (preserves forensic evidence)
3. Backup essential photos via USB cable (not cloud)
4. Change all passwords from a DIFFERENT device
5. Enable 2FA on all accounts
6. Consider factory reset after evidence preservation
7. File report with local authorities if attacker is suspected

### Outcome

User performed factory reset after backing up photos. Post-reset scan showed zero suspicious connections — only standard Android traffic and Xiaomi telemetry. User was advised to only install apps from Google Play Store and to avoid sideloading APKs.

---

## Case Study 2: Stalkerware on a Partner's Phone

### Background

**Device:** Samsung Galaxy A54 (Android 14, One UI 6)
**User complaint:** Ex-partner seemed to know user's location and conversations despite blocking them on all platforms. Suspected phone was monitored.
**Scan duration:** 5 minutes

### Findings Summary

| Severity | Count | Category |
|----------|-------|----------|
| CRITICAL | 3 | Stalkerware C2 communication |
| HIGH | 1 | Data exfiltration pattern |
| INFO | 5 | Manufacturer telemetry |
| NORMAL | 298 | Legitimate traffic |

**Total connections observed:** 307
**Unique destination IPs:** 41

### Critical Findings

#### Finding 1: TheTruthSpy Communication

```
Type:         Stalkerware C2
Domain:       protocol.thetruthspy.com (matched in AssoEchap database)
IP:           198.51.100.50
Port:         443 (HTTPS)
Connections:  47 in 5 minutes
Interval:     6.4s average — very aggressive polling
Bytes out:    890 KB
Bytes in:     12 KB
TLS SNI:      protocol.thetruthspy.com
```

**Analysis:** Direct match against the AssoEchap stalkerware database. TheTruthSpy is a commercial stalkerware application that provides GPS tracking, call recording, SMS interception, and camera access. The 47 connections in 5 minutes indicate the app is actively uploading intercepted data.

#### Finding 2: Secondary Stalkerware Domain

```
Type:         Stalkerware C2 (related)
Domain:       copy9.com (matched in AssoEchap database)
IP:           198.51.100.51
Port:         443 (HTTPS)
Connections:  12 in 5 minutes
```

**Analysis:** copy9.com is a known alias/related service to TheTruthSpy. Both domains appearing confirms TheTruthSpy installation.

#### Finding 3: Location Data Upload

```
Type:         Stalkerware data upload
Domain:       api.thetruthspy.com
Port:         443 (HTTPS)
Connections:  8 in 5 minutes
Bytes out:    234 KB (likely GPS coordinates + metadata)
Pattern:      Regular 35-second interval — location reporting
```

**Analysis:** Separate API endpoint for structured data upload. The 35-second interval matches TheTruthSpy's documented GPS reporting frequency.

### Behavioral Analysis

| Behavior | Detected | Confidence |
|----------|----------|------------|
| Beaconing | YES | 0.98 (extremely regular 6.4s interval) |
| Data exfiltration | YES | 0.92 (continuous upload stream) |
| Camera/mic streaming | NO | — (not during scan, but capability exists) |
| Keylogger pattern | YES | 0.67 (small frequent payloads within main stream) |

### What TheTruthSpy Can Access

Based on known capabilities of this stalkerware family:

- Real-time GPS location (updating every 35 seconds)
- All SMS messages (sent and received)
- Call logs and call recording
- WhatsApp, Telegram, Viber, and other messenger data
- Browser history
- Photos and videos
- Contact list
- Camera access (on-demand)
- Microphone access (ambient recording)
- Keylogging

### Recommendations Provided

1. **This is likely a criminal offense** — stalkerware installation without consent is illegal in most jurisdictions
2. Do NOT confront the suspected person (for safety)
3. Document the finding (screenshot the scan report)
4. Contact a domestic violence hotline or legal advisor
5. Consider involving law enforcement
6. Factory reset only after evidence is preserved
7. Change all passwords from a different device
8. Check for physical access prevention (change locks if needed)

### Outcome

User contacted local authorities with the scan report as evidence. The device was preserved for forensic examination. After legal proceedings were initiated, user obtained a new device.

---

## Case Study 3: Cryptojacking on a Gaming Phone

### Background

**Device:** Xiaomi POCO X5 (Android 13)
**User complaint:** Phone extremely hot during idle, battery draining 4x faster than normal, phone sluggish even for simple tasks like messaging.
**Scan duration:** 5 minutes

### Findings Summary

| Severity | Count | Category |
|----------|-------|----------|
| HIGH | 4 | Crypto mining connections |
| MEDIUM | 1 | Suspicious app behavior |
| INFO | 6 | Manufacturer telemetry |
| NORMAL | 156 | Legitimate traffic |

**Total connections observed:** 167
**Unique destination IPs:** 31

### Critical Findings

#### Finding 1: Stratum Mining Protocol

```
Type:         Cryptocurrency mining
Destination:  pool.moneroocean.stream:14444
Protocol:     Stratum (JSON-RPC over TCP/SSL)
Connection:   Single persistent TCP connection (entire 5-min scan)
Bytes out:    48 KB (hash submissions)
Bytes in:     156 KB (job assignments)
```

**Stratum protocol captured:**
```json
→ {"id":1,"method":"mining.subscribe","params":["xmrig/6.20.0"]}
← {"id":1,"result":["session_id","nonce"],"error":null}
→ {"id":2,"method":"mining.authorize","params":["wallet_addr.worker1",""]}
→ {"id":3,"method":"mining.submit","params":["wallet_addr.worker1","job_id","nonce","hash"]}
```

**Analysis:** Direct evidence of Monero mining. The user-agent string `xmrig/6.20.0` reveals XMRig miner embedded in an app. MoneroOcean is a popular mining pool that auto-selects the most profitable algorithm. Port 14444 is the SSL-encrypted Stratum endpoint.

#### Finding 2: Mining Pool Fallback Connections

```
Type:         Mining pool (backup)
Destinations:
  - pool.hashvault.pro:7777 (3 connection attempts, none sustained)
  - xmr.nanopool.org:14433 (1 connection attempt)
```

**Analysis:** The miner is configured with backup pools. This is standard for mining software — if the primary pool is unreachable, it fails over. Three failed attempts to hashvault.pro suggest it may be temporarily blocking the connection.

### Resource Impact Assessment

Based on the mining configuration detected:

- **CPU usage:** Likely 80-100% on all cores (XMRig default behavior)
- **Battery impact:** Mining at full CPU will drain battery 3-4x faster
- **Heat:** Sustained CPU load generates significant heat, potentially reducing battery lifespan
- **Data usage:** ~50-200 MB/day for mining communication
- **Performance:** Device will be sluggish for all normal tasks

### Source Investigation

The user reported installing a "free VPN" APK from a third-party website. This is the most common vector for mobile cryptojacking — trojanized apps that include hidden mining components. The APK likely:

1. Functions as a basic VPN (providing expected functionality)
2. Runs XMRig miner in the background as a service
3. Mines Monero to the attacker's wallet address
4. Configured with multiple pool fallbacks for reliability

### Recommendations Provided

1. Uninstall the suspected VPN app immediately
2. Check for device administrator permissions: Settings → Security → Device Admin Apps
3. If the app resists uninstallation, boot to Safe Mode and remove
4. Install a reputable antivirus (Malwarebytes) to scan for remnants
5. Only install VPN apps from Google Play Store by established vendors
6. Monitor battery usage in Settings → Battery for any app using excessive power

### Outcome

User identified and uninstalled a "SpeedVPN Free" app that was sideloaded. Post-removal scan showed zero mining connections. Battery life and performance returned to normal immediately.

---

## Case Study 4: Clean Device — What Normal Looks Like

### Background

**Device:** Google Pixel 8 (Android 14)
**User motivation:** Wanted to verify phone security after reading about mobile malware.
**Scan duration:** 5 minutes

### Findings Summary

| Severity | Count | Category |
|----------|-------|----------|
| CRITICAL | 0 | — |
| HIGH | 0 | — |
| MEDIUM | 0 | — |
| INFO | 4 | Google telemetry |
| NORMAL | 203 | Legitimate traffic |

**Total connections observed:** 207
**Unique destination IPs:** 38

### What Normal Traffic Looks Like

All connections fell into expected categories:

| Category | Connections | Examples |
|----------|------------|---------|
| Google Services | 67 | googleapis.com, gstatic.com, google.com |
| CDN | 45 | cloudflare.com, akamaized.net, fbcdn.net |
| Social Media | 32 | instagram.com, facebook.com |
| Messaging | 28 | whatsapp.net, web.telegram.org |
| Email | 12 | outlook.office365.com |
| Push Notifications | 15 | mtalk.google.com (port 5228) |
| DNS | 8 | Cloudflare DNS (1.1.1.1:853 DoT) |

### Port Distribution (Clean Device)

| Port | Count | Percentage |
|------|-------|-----------|
| 443 (HTTPS) | 178 | 86% |
| 80 (HTTP) | 8 | 4% |
| 5228 (FCM) | 12 | 6% |
| 853 (DoT) | 6 | 3% |
| 123 (NTP) | 3 | 1% |

**Key observation:** A clean device communicates almost exclusively on ports 443, 80, 5228, 853, and 123. Any connection outside these ports warrants attention.

### Telemetry (Expected for Pixel)

| Domain | Category | Note |
|--------|----------|------|
| android.clients.google.com | Device check-in | Standard Android behavior |
| play.googleapis.com | Play Services | App updates, licensing |
| firebaseinstallations.googleapis.com | Firebase | App analytics (used by installed apps) |
| app-measurement.com | Firebase Analytics | Usage metrics |

### Behavioral Analysis

| Behavior | Detected | Note |
|----------|----------|------|
| Beaconing | NO | FCM has regular intervals but is whitelisted |
| Data exfiltration | NO | All upload/download ratios within normal ranges |
| Streaming | NO | No sustained upload streams detected |
| Keylogger | NO | No small-payload repetitive pattern |
| DNS tunneling | NO | All DNS queries are standard length |

### Report Delivered

> **Your phone is clean.**
>
> We analyzed 207 connections over 5 minutes and found no signs of malware, stalkerware, or suspicious activity.
>
> All traffic goes to expected destinations: Google services, social media, messaging apps, and content delivery networks.
>
> **Google telemetry:** Your Pixel sends standard Android telemetry to Google (device check-ins, Play Services, Firebase analytics). This is normal for Android devices and is documented by Google.
>
> **Good security practices detected:**
> - DNS over TLS enabled (using Cloudflare 1.1.1.1)
> - All web traffic encrypted (HTTPS)
> - No sideloaded apps detected

---

## Case Study 5: Botnet-Infected Device with IRC C2

### Background

**Device:** Samsung Galaxy A13 (Android 12)
**User complaint:** Phone randomly vibrates with no notification, occasional popup ads even without browser open, data usage doubled over past month.
**Scan duration:** 5 minutes

### Findings Summary

| Severity | Count | Category |
|----------|-------|----------|
| CRITICAL | 2 | Botnet C2 (IRC) |
| HIGH | 5 | Adware beacon connections |
| MEDIUM | 3 | Suspicious domain resolution |
| INFO | 4 | Manufacturer telemetry |
| NORMAL | 186 | Legitimate traffic |

**Total connections observed:** 200
**Unique destination IPs:** 44

### Critical Findings

#### Finding 1: IRC Botnet C2

```
Type:         IRC botnet command-and-control
Destination:  198.51.100.80:6667
Protocol:     IRC (plaintext)
Connection:   Single persistent connection (entire scan)
Pattern:      JOIN/PRIVMSG commands observed
Bytes in:     8.2 KB (commands from botmaster)
Bytes out:    1.1 KB (responses/status)
```

**Analysis:** Persistent IRC connection on port 6667. The phone joined an IRC channel and received commands — classic botnet behavior. The plaintext IRC protocol allowed Suricata to match on JOIN and PRIVMSG patterns.

**Suricata alert:** `ET TROJAN IRC Bot Channel Join` (sid:2008124)

#### Finding 2: Encrypted IRC Fallback

```
Type:         IRC botnet C2 (TLS)
Destination:  198.51.100.81:6697
Protocol:     IRC/TLS
Connection:   Attempted, fell back to plaintext 6667
```

**Analysis:** The botnet first attempted encrypted IRC (port 6697), then fell back to plaintext when the TLS connection failed. This indicates a moderately sophisticated botnet with encryption capability.

#### High Severity: Adware Network

```
Type:         Aggressive adware
Destinations: 5 unique IPs associated with ad fraud networks
Pattern:      Beaconing every 120 seconds (CV=0.22)
Purpose:      Ad impression fraud — loading ads in background
```

**Analysis:** The botnet component includes ad fraud functionality — loading and "viewing" ads in the background to generate fraudulent ad revenue for the botmaster. This explains the popup ads the user was experiencing.

### Recommendations Provided

1. Boot into Safe Mode (hold power button → long press "Power Off" → tap "Safe Mode")
2. In Safe Mode, go to Settings → Apps → sort by recently installed
3. Look for apps with generic names ("System Update", "Phone Service", "Security")
4. Uninstall suspicious apps
5. If apps resist removal, check Device Admin Apps and revoke permissions first
6. Run Malwarebytes scan after removing suspicious apps
7. If issue persists, factory reset

### Outcome

User found a sideloaded "Free Games" app that was installed by a family member. Removing it eliminated all botnet and adware traffic. Post-removal scan confirmed clean.

---

## Statistical Summary Across All Scans

Based on aggregated scan data (anonymized):

| Metric | Value |
|--------|-------|
| Total scans performed | 500+ |
| Devices with critical findings | ~8% |
| Devices with high findings | ~12% |
| Devices clean (info/normal only) | ~72% |
| Most common threat | Stalkerware (35% of threats) |
| Second most common | Crypto mining (25% of threats) |
| Third most common | RAT/backdoor (20% of threats) |
| Most common infection vector | Sideloaded APKs (60% of cases) |
| Average scan duration | 5 minutes |
| Average connections per scan | 200-400 |
