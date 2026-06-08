import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

def load_config():
    if not os.path.exists(CONFIG_PATH):
        return {}
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(data):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def get_token():
    cfg = load_config()
    return cfg.get("token")

def set_token(token):
    cfg = load_config()
    cfg["token"] = token
    save_config(cfg)

def get_webhook_url():
    cfg = load_config()
    return cfg.get("webhook_url")

def set_webhook_url(url):
    cfg = load_config()
    cfg["webhook_url"] = url
    save_config(cfg)
