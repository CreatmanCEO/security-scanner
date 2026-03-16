with open("/root/security-scanner/bot/config.py", "r") as f:
    content = f.read()

# === FIX 5: Fix privacy policy link ===
content = content.replace("t.me/phone_guard_ru/2", "t.me/phone_guard_ru/7")

# === FIX 4: Add warnings to scan_started message ===
old_scan_started = '''    "scan_started": """
⏳ <b>Сканирование запущено!</b>

Ваша VPN-ссылка готова. Скопируйте и импортируйте в:
• <b>Android:</b> Hiddify, v2rayNG
• <b>iPhone:</b> Streisand, Hiddify

⏱ Длительность: <b>{duration} минут</b>

После завершения вы получите детальный отчёт.

🔐 <i>Мы не читаем содержимое вашего трафика. Анализируются только метаданные: к каким серверам подключается устройство, через какие порты и в каком объёме.</i>
""",'''

new_scan_started = '''    "scan_started": """
⏳ <b>Сканирование запущено!</b>

Ваша VPN-ссылка готова. Скопируйте и импортируйте в:
• <b>Android:</b> Hiddify, v2rayNG
• <b>iPhone:</b> Streisand, Hiddify

⏱ Длительность: <b>{duration} минут</b>

⚠️ <b>Важно:</b>
• Если подключение не произойдёт в течение 5 минут — ключ будет удалён
• После получения отчёта отключитесь от VPN
• При включённом VPN НЕ используйте: Госуслуги, банковские приложения, приложения операторов (МТС, Билайн, Мегафон, Теле2)

После завершения вы получите детальный отчёт.

🔐 <i>Мы не читаем содержимое вашего трафика. Анализируются только метаданные: к каким серверам подключается устройство, через какие порты и в каком объёме.</i>
""",'''

content = content.replace(old_scan_started, new_scan_started, 1)

with open("/root/security-scanner/bot/config.py", "w") as f:
    f.write(content)

print("config.py patched successfully")
