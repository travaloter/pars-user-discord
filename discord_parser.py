import os
import sys
import time
import re
import random
import string
from config import get_token, set_token, get_webhook_url, set_webhook_url
from discord_api import DiscordClient
from formatter import format_txt, format_json, send_webhook

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def splash():
    clear()
    print("=" * 40)
    print("   Discord Member Parser")
    print("   Created by diablo")
    print("=" * 40)
    time.sleep(2)

def safe_name(name):
    clean = re.sub(r'[^a-zA-Z0-9_-]', '_', str(name)).strip('_')[:80] or 'unknown'
    return clean.lower()

def wait_and_clear():
    input("\nНажми Enter чтобы продолжить...")
    clear()

def main_menu():
    splash()
    while True:
        clear()
        token = get_token()
        token_status = "[OK] Установлен" if token else "[NO] Не установлен"
        webhook = get_webhook_url()
        webhook_status = f"[OK] {webhook[:40]}..." if webhook else "[NO] Не установлен"

        print("=== Discord Member Parser ===")
        print(f"1. Токен аккаунта — {token_status}")
        print(f"2. Webhook URL — {webhook_status}")
        print("3. Запустить парсинг")
        print("4. Выход")

        choice = input("\nВыбери пункт: ").strip()

        if choice == "1":
            token_menu()
        elif choice == "2":
            webhook_menu()
        elif choice == "3":
            parse_menu()
        elif choice == "4":
            print("Выход...")
            break

def token_menu():
    clear()
    print("=== Токен аккаунта ===")
    current = get_token()
    if current:
        print(f"Текущий токен: {current[:20]}...{current[-5:]}")
    token = input("Введи новый токен (или оставь пустым для отмены): ").strip()
    if token:
        set_token(token)
        print("Токен сохранён!")
    wait_and_clear()

def webhook_menu():
    clear()
    print("=== Webhook URL ===")
    current = get_webhook_url()
    if current:
        print(f"Текущий URL: {current}")
    url = input("Введи новый webhook URL (или оставь пустым для отмены): ").strip()
    if url:
        set_webhook_url(url)
        print("Webhook URL сохранён!")
    wait_and_clear()

def parse_menu():
    clear()
    token = get_token()
    if not token:
        print("Сначала установи токен!")
        wait_and_clear()
        return

    client = DiscordClient(token)

    check = client.check_token()
    if check == "no_connection":
        print("Нет подключения к интернету! Проверь соединение.")
        wait_and_clear()
        return
    elif check == "timeout":
        print("Таймаут соединения. Проверь интернет.")
        wait_and_clear()
        return
    elif not check:
        print("Токен невалидный!")
        wait_and_clear()
        return

    print("Токен валидный\n")

    guild_id = input("Введи ID сервера: ").strip()
    role_id = input("Введи ID роли: ").strip()

    if not guild_id or not role_id:
        print("ID сервера и роли обязательны!")
        wait_and_clear()
        return

    print("\nПолучаю информацию...")
    guild_name, role_name = client.get_guild_and_role(guild_id, role_id)
    if not role_name:
        print("Не удалось получить роль. Проверь ID.")
        wait_and_clear()
        return

    print(f"Сервер: {guild_name}")
    print(f"Роль: @{role_name}")
    print("Получаю участников...")
    members = client.get_members_with_role(guild_id, role_id)

    if not members:
        print("Никого с такой ролью не найдено.")
        wait_and_clear()
        return

    print(f"Найдено участников: {len(members)}\n")

    tag = f"{safe_name(guild_name)}_{safe_name(role_name)}_{''.join(random.choices(string.ascii_lowercase, k=4))}"

    print("Формат вывода:")
    print("1. TXT файл")
    print("2. JSON файл")
    print("3. Webhook")
    print("4. Консоль")
    print("5. Создать канал и разослать пинги")
    fmt = input("Выбери (1/2/3/4/5): ").strip()

    if fmt == "1":
        os.makedirs("history/txt", exist_ok=True)
        text = format_txt(members, role_name)
        filename = f"history/txt/{tag}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Сохранено в {filename}")

    elif fmt == "2":
        os.makedirs("history/json", exist_ok=True)
        data = format_json(members, role_name)
        filename = f"history/json/{tag}.json"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(data)
        print(f"Сохранено в {filename}")

    elif fmt == "3":
        webhook_url = get_webhook_url()
        if not webhook_url:
            webhook_url = input("Введи webhook URL: ").strip()
            if webhook_url:
                set_webhook_url(webhook_url)

        if webhook_url:
            send_webhook(webhook_url, members, role_name)
            print("Отправлено в вебхук!")
        else:
            print("Webhook URL не указан.")

    elif fmt == "4":
        print()
        print(format_txt(members, role_name))

    elif fmt == "5":
        target_guild = input("ID сервера куда создать каналы: ").strip()
        if not target_guild:
            print("ID сервера не указан.")
            wait_and_clear()
            return

        cat_name = safe_name(guild_name)
        print(f"Создаю категорию {cat_name}...")
        cat_id = client.create_channel(target_guild, cat_name, ch_type=4)
        if not cat_id:
            print("Нет прав на создание категории.")
            wait_and_clear()
            return

        created = 0
        for m in members:
            uid = m["id"]
            ch_name = safe_name(f"id-{uid}")
            print(f"Создаю канал #{ch_name}...")
            ch_id = client.create_channel(target_guild, ch_name, parent_id=cat_id)
            if not ch_id:
                print(f"  нет прав, пропускаю {uid}")
                continue
            time.sleep(0.5)
            ok = client.send_message(ch_id, f"<@{uid}> — `{uid}`")
            if ok:
                created += 1
                print(f"  готово")
            time.sleep(0.5)

        print(f"Создано каналов: {created}/{len(members)}")

    else:
        print("Неверный выбор.")

    wait_and_clear()

if __name__ == "__main__":
    main_menu()
