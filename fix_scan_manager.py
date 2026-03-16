import re

with open("/root/security-scanner/bot/scan_manager.py", "r") as f:
    content = f.read()

# === FIX 2a: Add IP enrichment after external_ips collection, before threat_intel ===
old_whitelist = "            # Whitelist known safe IPs/ranges"
new_enrichment = """            # IP enrichment - add org names
            from analysis.ip_enrichment import enrich_ip_list
            ip_enrichment = enrich_ip_list(list(external_ips)[:50])
            known_service_ips = {ip for ip, info in ip_enrichment.items() if info.get("is_known_service")}
            logger.info("IP enrichment: " + str(len(known_service_ips)) + " known services of " + str(len(external_ips)))

            # Whitelist known safe IPs/ranges"""
content = content.replace(old_whitelist, new_enrichment, 1)

# === FIX 2b: Add known service skip in threat_intel loop ===
old_loop = """            for ip in list(external_ips)[:20]:
                # Skip known safe IPs
                if any(ip.startswith(p) for p in SAFE_PREFIXES):
                    threat_data[ip] = {"threat_level": "safe", "whitelisted": True, "note": "Known safe service"}
                    continue
                result = await threat_lookup.lookup_ip(ip)
                threat_data[ip] = result"""
new_loop = """            for ip in list(external_ips)[:20]:
                # Skip known safe IPs
                if any(ip.startswith(p) for p in SAFE_PREFIXES):
                    threat_data[ip] = {"threat_level": "safe", "whitelisted": True, "note": "Known safe service"}
                    continue
                # Skip known services from IP enrichment
                if ip in known_service_ips:
                    threat_data[ip] = {"threat_level": "safe", "whitelisted": True, "org": ip_enrichment.get(ip, {}).get("org", "Known service")}
                    continue
                result = await threat_lookup.lookup_ip(ip)
                threat_data[ip] = result"""
content = content.replace(old_loop, new_loop, 1)

# === FIX 10: Override threat_level for low AbuseIPDB scores ===
old_threat_check = """                if abuse_score > 50:
                        threat_ips.add(ip)
                    elif result.get("threat_level") in ("high", "critical") and abuse_score > 30:
                        threat_ips.add(ip)"""
new_threat_check = """                # Override: low AbuseIPDB = not a real threat regardless of OTX
                    if 0 < abuse_score < 10:
                        result["threat_level"] = "low"
                        result["note"] = "Low AbuseIPDB score, likely false positive"
                        threat_data[ip] = result
                    if abuse_score > 50:
                        threat_ips.add(ip)
                    elif result.get("threat_level") in ("high", "critical") and abuse_score > 30:
                        threat_ips.add(ip)"""
content = content.replace(old_threat_check, new_threat_check, 1)

# === FIX 2c: Pass ip_enrichment to AI analyzer ===
old_ai_data = '''                "device_manufacturer": scan_info.get("device_manufacturer", ""),
                "device_model": scan_info.get("device_model", ""),
            })'''
new_ai_data = '''                "device_manufacturer": scan_info.get("device_manufacturer", ""),
                "device_model": scan_info.get("device_model", ""),
                "ip_enrichment": {ip: info for ip, info in ip_enrichment.items()},
            })'''
content = content.replace(old_ai_data, new_ai_data, 1)

# === FIX 6: Add cleanup_stale_scans method and call from start() ===
old_start = '''    async def start(self):
        """Запуск менеджера"""
        # Создаём директорию для отчётов
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)

        # Запускаем фоновую очистку
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("ScanManager started (VLESS mode)")'''

new_start = '''    async def start(self):
        """Запуск менеджера"""
        # Создаём директорию для отчётов
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)

        # Clean up stale scans on startup
        await self.cleanup_stale_scans()

        # Запускаем фоновую очистку
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("ScanManager started (VLESS mode)")

    async def cleanup_stale_scans(self):
        """Mark old scanning/connecting scans as timed out"""
        import sqlite3
        try:
            conn = sqlite3.connect("/root/security-scanner/bot/scanner.db")
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE scans SET status='timeout' "
                "WHERE status IN ('scanning', 'connecting', 'waiting_connection') "
                "AND created_at < datetime('now', '-45 minutes')"
            )
            updated = cursor.rowcount
            conn.commit()
            conn.close()
            if updated > 0:
                logger.info("Cleaned up " + str(updated) + " stale scans")
        except Exception as e:
            logger.error("Stale scan cleanup error: " + str(e))'''

content = content.replace(old_start, new_start, 1)

# === FIX 8: Move VLESS client deletion to AFTER report generation ===
old_finish = '''        try:
            # Удаляем VLESS клиента
            if vless_uuid:
                vless = get_vless_manager()
                try:
                    await vless.delete_client(vless_uuid)
                    logger.info(f"Cleaned up VLESS client for scan {scan_id}")
                except Exception as e:
                    logger.error(f"Failed to cleanup VLESS client: {e}")

            # Если сканирование было успешным, генерируем отчёт
            report_data = None
            if status == "completed" and scan_info.get("started_at"):'''
new_finish = '''        try:
            # Generate report BEFORE deleting VLESS key
            report_data = None
            if status == "completed" and scan_info.get("started_at"):'''
content = content.replace(old_finish, new_finish, 1)

# Add VLESS deletion AFTER notify callback
old_notify = '''            # Вызываем callback
            on_complete = scan_info.get("on_complete")'''
new_notify = '''            # Now delete VLESS client (after report is ready)
            if vless_uuid:
                vless = get_vless_manager()
                try:
                    await vless.delete_client(vless_uuid)
                    logger.info(f"Cleaned up VLESS client for scan {scan_id}")
                except Exception as e:
                    logger.error(f"Failed to cleanup VLESS client: {e}")

            # Вызываем callback
            on_complete = scan_info.get("on_complete")'''
content = content.replace(old_notify, new_notify, 1)

with open("/root/security-scanner/bot/scan_manager.py", "w") as f:
    f.write(content)

print("scan_manager.py patched successfully")
