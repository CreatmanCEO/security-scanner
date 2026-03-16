with open("/root/security-scanner/reports/generator.py", "r") as f:
    content = f.read()

# === FIX 3: Fix unique_ips count in Suricata fallback stats ===
# The problem: ext_ips from suricata_data.get("external_ips", []) may be filtered/incomplete
# Fix: count unique dest IPs from all flows + xray destinations
old_unique_ips = '''            traffic_stats = {
                "total_connections": total_flows + total_tls + total_dns,
                "total_bytes_mb": round(total_bytes / 1024 / 1024, 1),
                "unique_ips": len(ext_ips) if isinstance(ext_ips, (list, set)) else 0,
                "duration_seconds": 1800,
                "by_port": by_port
            }'''

new_unique_ips = '''            # Count unique IPs from all flows (not just ext_ips which may be filtered)
            all_dest_ips = set()
            for f in flows:
                if isinstance(f, dict):
                    dest = f.get("dest_ip", "")
                    if dest and not dest.startswith(("127.", "10.", "192.168.", "0.0.")):
                        all_dest_ips.add(dest)
            # Also count from ext_ips if available
            if isinstance(ext_ips, (list, set)):
                for eip in ext_ips:
                    if eip:
                        all_dest_ips.add(eip)

            traffic_stats = {
                "total_connections": total_flows + total_tls + total_dns,
                "total_bytes_mb": round(total_bytes / 1024 / 1024, 1),
                "unique_ips": len(all_dest_ips) if all_dest_ips else (len(ext_ips) if isinstance(ext_ips, (list, set)) else 0),
                "duration_seconds": 1800,
                "by_port": by_port
            }'''

content = content.replace(old_unique_ips, new_unique_ips, 1)

with open("/root/security-scanner/reports/generator.py", "w") as f:
    f.write(content)

print("generator.py patched successfully")
