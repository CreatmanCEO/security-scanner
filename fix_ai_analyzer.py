with open("/root/security-scanner/analysis/ai_analyzer.py", "r") as f:
    content = f.read()

# === FIX 9: Add ip_enrichment to AI prompt ДАННЫЕ section ===
old_prompt_line = "- device_manufacturer: производитель устройства"
new_prompt_line = """- device_manufacturer: производитель устройства
- ip_enrichment: для каждого IP указана организация-владелец (Google, Fastly CDN, Apple, VK и т.д.). Если is_known_service=True — это легитимный сервис, НЕ угроза."""

content = content.replace(old_prompt_line, new_prompt_line, 1)

# Also pass ip_enrichment in the traffic_info dict sent to AI
old_traffic_info_end = '''            "tls_sni": list(set(t.get("sni", "") for t in suricata_data.get("tls", [])[:50] if isinstance(t, dict) and t.get("sni"))),
        }'''
new_traffic_info_end = '''            "tls_sni": list(set(t.get("sni", "") for t in suricata_data.get("tls", [])[:50] if isinstance(t, dict) and t.get("sni"))),
            "ip_enrichment": data.get("ip_enrichment", {}),
        }'''

content = content.replace(old_traffic_info_end, new_traffic_info_end, 1)

with open("/root/security-scanner/analysis/ai_analyzer.py", "w") as f:
    f.write(content)

print("ai_analyzer.py patched successfully")
