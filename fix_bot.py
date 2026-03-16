with open("/root/security-scanner/bot/bot.py", "r") as f:
    content = f.read()

# === FIX 7: Show username in admin active scans ===
old_admin_scans = '''        for scan in scans:
            text += f"• {scan['scan_id'][:16]}...\\n"
            text += f"  User: {scan['telegram_id']}, IP: {scan.get('client_ip', 'N/A')}\\n"
            text += f"  Status: {scan['status']}\\n\\n"'''

new_admin_scans = '''        for scan in scans:
            # Resolve username for admin view
            scan_username = str(scan['telegram_id'])
            try:
                import sqlite3 as _sq
                _conn = _sq.connect("/root/security-scanner/bot/scanner.db")
                _cur = _conn.cursor()
                _cur.execute("SELECT username, first_name FROM users WHERE telegram_id=?", (scan['telegram_id'],))
                _row = _cur.fetchone()
                if _row:
                    scan_username = "@" + _row[0] if _row[0] else _row[1] or str(scan['telegram_id'])
                _conn.close()
            except Exception:
                pass
            text += f"\\u2022 {scan['scan_id'][:16]}...\\n"
            text += f"  User: {scan_username} ({scan['telegram_id']})\\n"
            text += f"  Status: {scan['status']}\\n\\n"'''

content = content.replace(old_admin_scans, new_admin_scans, 1)

# === FIX 6 (part 2): Call cleanup_stale_scans on startup ===
old_startup = '''    # Запускаем scan manager
    manager = get_scan_manager()
    manager.bot = bot
    await manager.start()'''
new_startup = '''    # Запускаем scan manager
    manager = get_scan_manager()
    manager.bot = bot
    await manager.start()

    # Also run periodic stale scan cleanup
    async def _periodic_stale_cleanup():
        import asyncio as _aio
        while True:
            await _aio.sleep(1800)  # Every 30 minutes
            try:
                await manager.cleanup_stale_scans()
            except Exception as e:
                logger.error("Periodic stale cleanup error: " + str(e))
    asyncio.create_task(_periodic_stale_cleanup())'''
content = content.replace(old_startup, new_startup, 1)

with open("/root/security-scanner/bot/bot.py", "w") as f:
    f.write(content)

print("bot.py patched successfully")
