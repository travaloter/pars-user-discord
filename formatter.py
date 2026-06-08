import json
import requests

def display_name(member):
    nick = member.get("nickname")
    username = member.get("username")
    global_name = member.get("global_name")

    if nick:
        return f"{username} ({nick})"
    return username

def format_txt(members, role_name):
    lines = []
    lines.append(f"Участники с ролью: {role_name}")
    lines.append("=" * 50)

    for m in members:
        name = display_name(m)
        lines.append(f"{name} | ID: {m['id']} | @{role_name}")

    lines.append("")
    lines.append(f"Всего: {len(members)}")
    return "\n".join(lines)

def format_json(members, role_name):
    data = []
    for m in members:
        data.append({
            "id": m["id"],
            "username": m["username"],
            "global_name": m.get("global_name"),
            "nickname": m.get("nickname"),
            "role": role_name
        })
    return json.dumps(data, indent=2, ensure_ascii=False)

def send_webhook(webhook_url, members, role_name):
    total = len(members)
    MAX_FIELDS = 25
    embeds = []

    for i in range(0, total, MAX_FIELDS):
        chunk = members[i:i + MAX_FIELDS]
        embed = {
            "title": f"Участники с ролью @{role_name}" if i == 0 else None,
            "color": 0x5865F2,
            "fields": [],
            "footer": {"text": f"Страница {i // MAX_FIELDS + 1} / {(total - 1) // MAX_FIELDS + 1} | Всего: {total}"}
        }

        for m in chunk:
            name = display_name(m)
            embed["fields"].append({
                "name": name,
                "value": f"ID: `{m['id']}`",
                "inline": True
            })

        embeds.append(embed)

    payload = {"embeds": embeds}
    r = requests.post(webhook_url, json=payload)
    return r.status_code == 204
