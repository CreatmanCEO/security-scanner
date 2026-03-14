# Device Manufacturer Telemetry — Domain Database

## Overview

Modern smartphones send significant amounts of data to their manufacturers, even when users opt out of data collection. This is not malware — it is built into the operating system by the vendor. However, users deserve transparency about what their devices transmit.

Security Scanner Bot classifies manufacturer telemetry separately from threats. It appears in the scan report under the "Device Telemetry" section with an informational severity level.

---

## Why Track Telemetry?

1. **Transparency:** Users should know what data their phone sends
2. **Differential diagnosis:** Telemetry domains must not be confused with malware
3. **Privacy assessment:** Some telemetry is more invasive than others
4. **Context for experts:** Security researchers need the full picture

---

## Telemetry by Manufacturer

### Xiaomi / MIUI / HyperOS

Xiaomi has the most documented privacy concerns among Android OEMs. Multiple independent studies have confirmed extensive data collection.

| Domain | Category | What It Sends | Privacy Impact | Source |
|--------|----------|--------------|----------------|--------|
| `tracking.miui.com` | Browser tracking | URLs visited in MIUI browser, search queries, reading time per page | **HIGH** — Sends browsing data even in incognito/private mode. Data transmitted to servers in Singapore and Russia. | Forbes 2020, Gabi Cirlig research |
| `data.mistat.xiaomi.com` | Usage statistics | App open/close events, screen time per app, feature usage | MEDIUM — Detailed behavioral profiling | Leith, TCD 2021 |
| `api.ad.xiaomi.com` | Advertising | Advertising ID, targeting profiles, ad interaction data | MEDIUM — Built-in ad network monetizing user data | MIUI analysis |
| `sdkconfig.ad.xiaomi.com` | Ad configuration | Remote ad SDK settings, campaign targeting rules | LOW — Configuration endpoint but reveals ad system scope | MIUI analysis |
| `data.mistat.intl.xiaomi.com` | International telemetry | Same as mistat but for international MIUI builds | MEDIUM — Separate endpoint for non-China users | Network analysis |
| `tracking.intl.miui.com` | International tracking | International version of tracking endpoint | HIGH — Same invasive tracking for global users | Network analysis |
| `api.sec.miui.com` | Security service | Device security status, app scan results | LOW — Legitimate security feature | MIUI docs |
| `connect.rom.miui.com` | Update check | ROM version, device model, update eligibility | LOW — Standard OTA update mechanism | MIUI docs |
| `t.browser.miui.com` | Browser telemetry | Additional browser behavioral data | HIGH — Extends tracking beyond URL collection | Network analysis |
| `mishop.data.xiaomi.com` | Store analytics | Mi Store browsing, purchase consideration data | MEDIUM — Shopping behavior tracking | Network analysis |

**Key finding (Forbes 2020):** Security researcher Gabi Cirlig demonstrated that Xiaomi's default MIUI browser sent all visited URLs, including those visited in incognito mode, to `tracking.miui.com`. The data included the exact URL, timestamp, and device identifiers. Xiaomi acknowledged the behavior and said they would update their privacy policy.

**Key finding (Leith, TCD 2021):** Douglas Leith at Trinity College Dublin found that Xiaomi handsets sent device identifiers (IMEI, MAC address), app usage data, and screen interaction events to Xiaomi servers. Data was transmitted even when users opted out of usage statistics in Settings.

### Samsung / One UI

| Domain | Category | What It Sends | Privacy Impact | Source |
|--------|----------|--------------|----------------|--------|
| `analytics.samsungknox.com` | Knox analytics | Device security state, Knox container status, app installation events | MEDIUM — Enterprise security telemetry on consumer devices | Samsung documentation |
| `sas.samsung.com` | Samsung Analytics | App usage statistics, feature usage, crash reports | MEDIUM — Standard analytics but extensive scope | Leith, TCD 2021 |
| `config.samsungads.com` | Advertising | Samsung Ads platform configuration, targeting data | MEDIUM — Built-in advertising system | Samsung Ads SDK |
| `gos-gsp.io` | Game Optimization | Game performance data, GPU/CPU usage during gaming | LOW — Performance optimization (controversial due to throttling) | Samsung GOS analysis |
| `samsungcloud.com` | Cloud sync | Device backup, settings sync, Find My Mobile | LOW — User-opted cloud service | Samsung docs |
| `push.samsungdm.com` | Device management | Remote device management commands, policy push | LOW-MEDIUM — OTA management capability | Samsung Knox docs |
| `us.analytics.samsung.com` | Regional analytics | US-specific analytics collection | MEDIUM — Regional data processing | Network analysis |
| `metrics.samsunglife.com` | Lifestyle metrics | Samsung Health and lifestyle app data | MEDIUM — Health-adjacent data collection | Samsung Health analysis |

**Samsung GOS controversy (2022):** Samsung's Game Optimizing Service was found to throttle performance in 10,000+ apps by checking package names against a list. While not a privacy issue per se, it demonstrated Samsung's ability to remotely control device behavior via `gos-gsp.io`.

### Huawei / EMUI / HarmonyOS

| Domain | Category | What It Sends | Privacy Impact | Source |
|--------|----------|--------------|----------------|--------|
| `hicloud.com` | Cloud services | Device backup, sync data, Huawei Mobile Services | MEDIUM — Broad cloud integration | Huawei EULA |
| `logservice1.hicloud.com` | System telemetry | System logs, crash reports, performance data | MEDIUM — Detailed device telemetry | Leith, TCD 2021 |
| `logservice.hicloud.com` | System telemetry | Duplicate/fallback telemetry endpoint | MEDIUM — Redundant collection | Network analysis |
| `metrics1.data.hicloud.com` | Metrics | App usage metrics, feature engagement | MEDIUM — Behavioral analytics | Network analysis |
| `metrics2.data.hicloud.com` | Metrics | Secondary metrics collection endpoint | MEDIUM — Load-balanced collection | Network analysis |
| `store.hispace.hicloud.com` | AppGallery | App store browsing data, download/install events | LOW-MEDIUM — Store analytics | Huawei docs |
| `push.hicloud.com` | Push service | Huawei Push Kit (equivalent to FCM) | LOW — Legitimate push notifications | Huawei docs |
| `hms.dbankcloud.com` | HMS Core | Huawei Mobile Services telemetry | MEDIUM — Core services data collection | HMS documentation |

**Leith, TCD 2021 findings:** Huawei handsets transmitted persistent device identifiers and usage data. Notably, Huawei devices continued transmitting telemetry even after factory reset, using persistent identifiers that survived the reset process.

### OPPO / ColorOS

| Domain | Category | What It Sends | Privacy Impact | Source |
|--------|----------|--------------|----------------|--------|
| `*.coloros.com` | ColorOS telemetry | System telemetry, app usage, feature engagement | MEDIUM — OS-level data collection | OPPO EULA |
| `*.heytap.com` | HeyTap platform | Cross-app tracking, HeyTap account data, service usage | MEDIUM — Unified tracking across OPPO ecosystem | OPPO/HeyTap docs |
| `push.coloros.com` | Push service | OPPO Push (regional alternative to FCM) | LOW — Legitimate push notification service | ColorOS docs |
| `store.coloros.com` | App store | App store analytics, download metrics | LOW — Store usage data | ColorOS docs |
| `browser.coloros.com` | Browser telemetry | OPPO Browser usage data, visited URLs | HIGH — Browser tracking (similar to Xiaomi) | Network analysis |

### Realme / Realme UI

Realme is a subsidiary of BBK Electronics (same parent as OPPO and OnePlus). It shares much of ColorOS's codebase and telemetry infrastructure.

| Domain | Category | What It Sends | Privacy Impact | Source |
|--------|----------|--------------|----------------|--------|
| `*.coloros.com` | Shared with OPPO | Same ColorOS telemetry | MEDIUM — Inherited from OPPO | Shared codebase |
| `*.heytap.com` | Shared with OPPO | Same HeyTap platform | MEDIUM — Cross-brand tracking | Shared codebase |
| `*.realme.com` | Brand-specific | Realme-specific features, Realme Link data | LOW-MEDIUM — Brand layer on top of ColorOS | Realme EULA |
| `push.realme.com` | Push service | Realme-specific push notifications | LOW — Legitimate service | Realme docs |

### Google / Android (Base OS)

These are present on ALL Android devices regardless of manufacturer.

| Domain | Category | What It Sends | Privacy Impact | Source |
|--------|----------|--------------|----------------|--------|
| `play.googleapis.com` | Play Services | App verification, licensing, Play Store data | LOW-MEDIUM — Core Android infrastructure | Google docs |
| `android.clients.google.com` | Device check-in | Device model, Android version, GSF ID, registered accounts | MEDIUM — Device inventory and identification | Leith, TCD 2021 |
| `www.googleapis.com` | API gateway | Various Google API calls | LOW — Umbrella API endpoint | Google docs |
| `connectivitycheck.gstatic.com` | Connectivity | Checks if internet is available | LOW — Standard captive portal check | Android source |
| `mtalk.google.com` | FCM | Firebase Cloud Messaging for push notifications | LOW — Essential for app notifications | Firebase docs |
| `android.googleapis.com` | Android services | SafetyNet, device attestation, integrity checks | LOW-MEDIUM — Security but also device fingerprinting | Google docs |
| `firebaseinstallations.googleapis.com` | Firebase | App installation tracking, Firebase project binding | MEDIUM — App-level tracking | Firebase docs |
| `app-measurement.com` | Firebase Analytics | App usage analytics (if app uses Firebase) | MEDIUM — Per-app analytics | Firebase docs |

### Apple / iOS

For completeness, iOS telemetry domains observed when scanning iPhones:

| Domain | Category | What It Sends | Privacy Impact | Source |
|--------|----------|--------------|----------------|--------|
| `xp.apple.com` | Diagnostics | Device diagnostics and usage data | LOW-MEDIUM — Apple's own analytics | Apple docs |
| `metrics.apple.com` | Metrics | OS and app performance metrics | LOW-MEDIUM — Performance telemetry | Apple docs |
| `idiagnostics.apple.com` | Crash reports | App crash logs, system crashes | LOW — Standard crash reporting | Apple docs |
| `configuration.apple.com` | Config | Device configuration profiles | LOW — Management endpoint | Apple docs |
| `identity.apple.com` | Apple ID | Authentication, account verification | LOW — Account security service | Apple docs |
| `icloud.com` | iCloud | iCloud sync (user-opted) | LOW — User-controlled cloud sync | Apple docs |
| `push.apple.com` (port 5223) | APNS | Push notifications | LOW — Essential notification service | Apple docs |

---

## Privacy Impact Scale

| Rating | Meaning | User Action Recommended |
|--------|---------|------------------------|
| **HIGH** | Data collection beyond what user expects, potentially invasive, may include browsing/location/personal data | Review privacy settings, consider alternative browser/apps, use DNS-level blocking |
| **MEDIUM** | Standard analytics but extensive scope, behavioral profiling, device fingerprinting | Review and disable optional analytics in Settings if available |
| **LOW-MEDIUM** | Legitimate service with some data collection side effects | Awareness only — typically cannot be disabled without breaking functionality |
| **LOW** | Essential device functionality, standard connectivity checks | No action needed — these are required for phone operation |

---

## Research References

1. **Forbes (2020):** "Xiaomi Phones Sending Browsing Data To China Even In Incognito Mode" — Gabi Cirlig and Andrew Tierney documented Xiaomi MIUI browser sending all URLs to remote servers
2. **Douglas Leith, Trinity College Dublin (2021):** "Android Mobile OS Snooping By Samsung, Xiaomi, Huawei and Realme Handsets" — Systematic study of telemetry from major Android OEMs. Found all tested manufacturers send substantial data even with user opt-out.
3. **Leith, TCD (2021):** "Mobile Handset Privacy: Measuring The Data iOS and Android Send to Apple And Google" — Comparison study showing both iOS and Android transmit device telemetry.
4. **Haoyu Liu et al. (2022):** "Android OS Privacy Under the Loupe" — Expanded study of pre-installed system apps and their data collection behavior.
5. **Samsung GOS Controversy (2022):** Multiple outlets documented Samsung's Game Optimizing Service throttling apps using a remote-controlled package list.

---

## How We Use This Data

In the scanner, manufacturer telemetry domains are:

1. **Identified and classified** — Not confused with malware
2. **Reported separately** — Under "Device Telemetry" section, not "Threats"
3. **Severity: INFO** — Not marked as malicious, but noted for transparency
4. **Privacy-annotated** — Each domain includes what it sends and its privacy impact
5. **Vendor-attributed** — Clearly labeled which manufacturer is collecting the data
