import json
import logging
from typing import Dict, Any

import requests

from .config import AI_API_KEY, AI_API_BASE_URL, AI_MODEL, AI_TIMEOUT, BOT_USERNAME

logger = logging.getLogger(__name__)


def _fallback_app_copy(app_name: str, app_code: str) -> Dict[str, str]:
    caption = (
        "Yangi premium ilova tayyor!\n\n"
        f"<b>{app_name}</b>\n\n"
        f"Kod: <code>{app_code}</code>\n"
        f"Yuklab olish uchun botga <code>{app_code}</code> kodini yuboring.\n\n"
        f"Bot: @{BOT_USERNAME.lstrip('@')}"
    )
    return {"name": app_name, "caption": caption}


def improve_app_copy(app_name: str, app_code: str, source_text: str = "") -> Dict[str, str]:
    """Create a clean Uzbek app name and Telegram HTML caption."""
    if not AI_API_KEY:
        return _fallback_app_copy(app_name, app_code)

    prompt = (
        "Telegram kanal uchun uzbek tilida qisqa, chiroyli app posti yozing. "
        "Spamga o'xshamasin, yolgon va noqonuniy vadalar bermang. "
        "HTML faqat <b> va <code> taglaridan foydalaning. "
        "JSON qaytaring: {\"name\":\"...\", \"caption\":\"...\"}. "
        f"Bot username: @{BOT_USERNAME.lstrip('@')}. "
        f"App kodi: {app_code}. Taxminiy nom: {app_name}. "
        f"Manba matn: {source_text[:1200]}"
    )

    try:
        response = requests.post(
            f"{AI_API_BASE_URL.rstrip('/')}/chat/completions",
            headers={
                "Authorization": f"Bearer {AI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": AI_MODEL,
                "messages": [
                    {"role": "system", "content": "You write concise Uzbek Telegram channel posts."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.5,
                "response_format": {"type": "json_object"},
            },
            timeout=AI_TIMEOUT,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        data: Dict[str, Any] = json.loads(content)
        name = str(data.get("name") or app_name).strip()[:80]
        caption = str(data.get("caption") or "").strip()
        if not caption:
            return _fallback_app_copy(name, app_code)
        if f"<code>{app_code}</code>" not in caption:
            caption += f"\n\nKod: <code>{app_code}</code>"
        return {"name": name, "caption": caption[:1000]}
    except Exception as exc:
        logger.warning("AI copy generation failed: %s", exc)
        return _fallback_app_copy(app_name, app_code)


def build_stats_insights(stats: Dict[str, Any]) -> str:
    """Return a short stats analysis for admins."""
    total_apps = stats.get("total_apps", 0)
    users = stats.get("total_users", 0)
    downloads = stats.get("total_downloads", 0)
    avg = downloads / total_apps if total_apps else 0

    lines = [
        "<b>AI tahlil</b>",
        f"Har bir ilovaga o'rtacha yuklanish: <b>{avg:.1f}</b>",
    ]
    if total_apps == 0:
        lines.append("Avval 3-5 ta sifatli app joylang, keyin top ilovalarni reklama qiling.")
    elif users < 100:
        lines.append("Hozir asosiy maqsad: kanal va botga yangi foydalanuvchi olib kelish.")
    elif avg < 5:
        lines.append("Postlarda app foydasini aniqroq yozing va eng yaxshi ilovalarni tepaga chiqaring.")
    else:
        lines.append("Yuklanish yaxshi. Top app postlarini qayta joylash foyda beradi.")
    return "\n".join(lines)
