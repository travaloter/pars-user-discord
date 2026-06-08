import asyncio
import time
import requests
import discord

API_BASE = "https://discord.com/api/v10"

class DiscordClient:
    def __init__(self, token):
        self.token = token
        self.s = requests.Session()
        self.s.headers.update({
            "Authorization": token,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

    def check_token(self):
        try:
            r = self.s.get(f"{API_BASE}/users/@me", timeout=10)
            return r.status_code == 200
        except requests.exceptions.ConnectionError:
            return "no_connection"
        except requests.exceptions.Timeout:
            return "timeout"
        except:
            return "no_connection"

    def get_guild_and_role(self, guild_id, role_id):
        r = self.s.get(f"{API_BASE}/guilds/{guild_id}")
        if r.status_code != 200:
            return None, None
        data = r.json()
        guild_name = data.get("name")
        role_name = None
        for role in data.get("roles", []):
            if role["id"] == role_id:
                role_name = role["name"]
                break
        return guild_name, role_name

    def create_channel(self, guild_id, name, ch_type=0, parent_id=None):
        data = {"name": name, "type": ch_type}
        if parent_id:
            data["parent_id"] = parent_id
        r = self.s.post(f"{API_BASE}/guilds/{guild_id}/channels", json=data)
        if r.status_code == 201:
            return r.json().get("id")
        return None

    def send_message(self, channel_id, content):
        r = self.s.post(f"{API_BASE}/channels/{channel_id}/messages", json={
            "content": content
        })
        return r.status_code == 200

    def get_members_with_role(self, guild_id, role_id):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(self._fetch(guild_id, role_id))
            return result
        finally:
            try:
                pending = asyncio.all_tasks(loop)
                for task in pending:
                    task.cancel()
                if pending:
                    loop.run_until_complete(asyncio.wait(pending, timeout=2))
            except:
                pass
            loop.close()

    async def _fetch(self, guild_id, role_id):
        client = discord.Client(self_bot=True, chunk_guilds_at_startup=False)
        result = []

        @client.event
        async def on_ready():
            nonlocal result

            guild = client.get_guild(int(guild_id))
            if not guild:
                await client.close()
                return

            try:
                await guild.chunk()
                for m in guild.members:
                    if any(r.id == int(role_id) for r in m.roles):
                        result.append({
                            "id": str(m.id),
                            "username": m.name,
                            "global_name": m.global_name,
                            "nickname": m.nick,
                            "discriminator": m.discriminator
                        })
            except:
                try:
                    members = await guild.fetch_members(force_scraping=True, delay=0.1, cache=True)
                    for m in members:
                        if not m:
                            continue
                        user = getattr(m, "user", m)
                        if any(r.id == int(role_id) for r in getattr(m, "roles", [])):
                            result.append({
                                "id": str(getattr(user, "id", "")),
                                "username": getattr(user, "name", ""),
                                "global_name": getattr(user, "global_name", None),
                                "nickname": getattr(m, "nick", None),
                                "discriminator": getattr(user, "discriminator", None)
                            })
                except:
                    pass

            await client.close()

        try:
            await client.start(self.token)
        except:
            pass

        return result
