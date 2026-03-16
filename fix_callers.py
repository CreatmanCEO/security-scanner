import re
import sys

# FIX I2: Remove "await" from all callers of database functions

# List of database functions that are now sync
db_funcs = [
    "get_or_create_user", "get_user", "update_user", "create_scan",
    "update_scan", "get_scan", "get_user_scans", "get_active_scans",
    "check_scans_available", "increment_scan_count", "get_active_subscription",
    "activate_subscription", "record_payment", "update_payment", "get_payments",
    "save_wg_key", "deactivate_wg_key", "get_active_wg_keys", "get_user_stats",
    "get_recent_users", "get_user_by_username",
]

def remove_awaits(filepath):
    with open(filepath, "r") as f:
        content = f.read()
    for func in db_funcs:
        content = re.sub(r'\bawait\s+' + func + r'\(', func + '(', content)
    return content

# === bot.py ===
filepath = "/root/security-scanner/bot/bot.py"
content = remove_awaits(filepath)

# FIX C2: Replace raw sqlite3 in admin_scans handler
old_admin = '            # Resolve username for admin view\n            scan_username = str(scan[\'telegram_id\'])\n            try:\n                import sqlite3 as _sq\n                _conn = _sq.connect("/root/security-scanner/bot/scanner.db")\n                _cur = _conn.cursor()\n                _cur.execute("SELECT username, first_name FROM users WHERE telegram_id=?", (scan[\'telegram_id\'],))\n                _row = _cur.fetchone()\n                if _row:\n                    scan_username = "@" + _row[0] if _row[0] else _row[1] or str(scan[\'telegram_id\'])\n                _conn.close()\n            except Exception:\n                pass'
new_admin = '            # Resolve username for admin view\n            from database import get_username_for_telegram_id\n            scan_username = get_username_for_telegram_id(scan[\'telegram_id\'])'

content = content.replace(old_admin, new_admin)

# FIX I4: Replace _ask_user_level
# Find and replace the function
old_func = 'async def _ask_user_level(message, state: FSMContext):\n    """'
new_func = 'async def _ask_user_level(message, state, edit=False):\n    """'
content = content.replace(old_func, new_func)

old_answer = '    await message.answer("\u041d\u0430\u0441\u043a\u043e\u043b\u044c\u043a\u043e \u0432\u044b \u0440\u0430\u0437\u0431\u0438\u0440\u0430\u0435\u0442\u0435\u0441\u044c \u0432 \u0441\u0435\u0442\u0435\u0432\u043e\u0439 \u0431\u0435\u0437\u043e\u043f\u0430\u0441\u043d\u043e\u0441\u0442\u0438?", reply_markup=keyboard)\n    await state.set_state(ScanStates.choosing_user_level)'
new_answer = '    text = "\u041d\u0430\u0441\u043a\u043e\u043b\u044c\u043a\u043e \u0432\u044b \u0440\u0430\u0437\u0431\u0438\u0440\u0430\u0435\u0442\u0435\u0441\u044c \u0432 \u0441\u0435\u0442\u0435\u0432\u043e\u0439 \u0431\u0435\u0437\u043e\u043f\u0430\u0441\u043d\u043e\u0441\u0442\u0438?"\n    if edit:\n        try:\n            await message.edit_text(text, reply_markup=keyboard)\n        except Exception:\n            await message.answer(text, reply_markup=keyboard)\n    else:\n        await message.answer(text, reply_markup=keyboard)\n    await state.set_state(ScanStates.choosing_user_level)'
content = content.replace(old_answer, new_answer)

# Fix the apple caller to use edit=True (from callback handler)
content = content.replace(
    '        await _ask_user_level(callback.message, state)\n    else:',
    '        await _ask_user_level(callback.message, state, edit=True)\n    else:'
)

with open(filepath, "w") as f:
    f.write(content)
print("bot.py updated")


# === scan_manager.py ===
filepath = "/root/security-scanner/bot/scan_manager.py"
content = remove_awaits(filepath)

# FIX C2: Replace cleanup_stale_scans
old_cleanup = '    async def cleanup_stale_scans(self):\n        """Mark old scanning/connecting scans as timed out"""\n        import sqlite3\n        try:\n            conn = sqlite3.connect("/root/security-scanner/bot/scanner.db")\n            cursor = conn.cursor()\n            cursor.execute(\n                "UPDATE scans SET status=\'timeout\' "\n                "WHERE status IN (\'scanning\', \'connecting\', \'waiting_connection\') "\n                "AND created_at < datetime(\'now\', \'-45 minutes\')"\n            )\n            updated = cursor.rowcount\n            conn.commit()\n            conn.close()\n            if updated > 0:\n                logger.info("Cleaned up " + str(updated) + " stale scans")\n        except Exception as e:\n            logger.error("Stale scan cleanup error: " + str(e))'

new_cleanup = '    async def cleanup_stale_scans(self):\n        """Mark old scanning/connecting scans as timed out"""\n        from bot.database import db_cleanup_stale_scans\n        try:\n            updated = db_cleanup_stale_scans(45)\n            if updated:\n                logger.info("Cleaned up " + str(updated) + " stale scans")\n        except Exception as e:\n            logger.error("Stale scan cleanup error: " + str(e))'

content = content.replace(old_cleanup, new_cleanup)

# FIX S1: Replace hardcoded SERVER_IP
content = content.replace(
    '            server_ip = "95.85.235.189"\n',
    '            from bot.config import SERVER_IP\n            server_ip = SERVER_IP\n'
)

with open(filepath, "w") as f:
    f.write(content)
print("scan_manager.py updated")


# === vpn_manager.py ===
filepath = "/root/security-scanner/bot/vpn_manager.py"
with open(filepath, "r") as f:
    content = f.read()
for func in db_funcs:
    content = re.sub(r'\bawait\s+' + func + r'\(', func + '(', content)
content = content.replace(
    'WG_SERVER_IP = "95.85.235.189"',
    'from bot.config import SERVER_IP as WG_SERVER_IP'
)
with open(filepath, "w") as f:
    f.write(content)
print("vpn_manager.py updated")


# === vless_manager.py ===
filepath = "/root/security-scanner/bot/vless_manager.py"
with open(filepath, "r") as f:
    content = f.read()
content = content.replace(
    'self.server_ip = os.getenv("VLESS_SERVER_IP", "95.85.235.189")',
    'from bot.config import SERVER_IP\n        self.server_ip = SERVER_IP'
)
with open(filepath, "w") as f:
    f.write(content)
print("vless_manager.py updated")


# === payments.py ===
filepath = "/root/security-scanner/bot/payments.py"
with open(filepath, "r") as f:
    content = f.read()
for func in db_funcs:
    content = re.sub(r'\bawait\s+' + func + r'\(', func + '(', content)
with open(filepath, "w") as f:
    f.write(content)
print("payments.py updated")


# === handlers/user.py ===
filepath = "/root/security-scanner/bot/handlers/user.py"
with open(filepath, "r") as f:
    content = f.read()
for func in db_funcs:
    content = re.sub(r'\bawait\s+' + func + r'\(', func + '(', content)
with open(filepath, "w") as f:
    f.write(content)
print("handlers/user.py updated")


# === config.py - add SERVER_IP ===
filepath = "/root/security-scanner/bot/config.py"
with open(filepath, "r") as f:
    content = f.read()
if "SERVER_IP = os.getenv" not in content:
    content = content.replace(
        'WG_SERVER_IP = os.getenv("WG_SERVER_IP", "95.85.235.189")',
        'WG_SERVER_IP = os.getenv("WG_SERVER_IP", "95.85.235.189")\nSERVER_IP = os.getenv("VLESS_SERVER_IP", "95.85.235.189")'
    )
with open(filepath, "w") as f:
    f.write(content)
print("config.py updated")


# === malware_detector.py - import SERVER_IP from config ===
filepath = "/root/security-scanner/analysis/malware_detector.py"
with open(filepath, "r") as f:
    content = f.read()
content = content.replace(
    'SERVER_IP = os.getenv("VLESS_SERVER_IP", "95.85.235.189")',
    'import sys as _sys\n_sys.path.insert(0, "/root/security-scanner")\nfrom bot.config import SERVER_IP'
)
with open(filepath, "w") as f:
    f.write(content)
print("malware_detector.py updated")


print("\nAll caller fixes applied!")
