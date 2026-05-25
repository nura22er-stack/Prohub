# Render Deploy

Bu loyiha Render'da **Web Service** sifatida ishlaydi:

- `python run.py` Telegram botni ishga tushiradi.
- `api/app.py` Render bergan `PORT` ga bind bo'ladi.
- `/health` endpoint Render health check uchun javob beradi.

## 1. GitHub'ga yuklash

Loyihani GitHub repositoriyga push qiling.

## 2. Render Blueprint

Render Dashboard -> **New** -> **Blueprint** ni tanlang va repo'ni ulang. `render.yaml` avtomatik topiladi.

Render so'ragan secret qiymatlarni kiriting:

```env
BOT_TOKEN=BotFather bergan token
BOT_USERNAME=@bot_username
REQUIRED_CHANNEL=@kanal_username
CHANNEL_ID=-1001234567890
ADMIN_ID=sizning_telegram_id
```

## 3. Manual Web Service

Agar Blueprint ishlatmasangiz:

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
python run.py
```

Environment variables:

```env
PYTHON_VERSION=3.11.9
BOT_TOKEN=...
BOT_USERNAME=...
REQUIRED_CHANNEL=...
CHANNEL_ID=...
ADMIN_ID=...
APPS_PER_PAGE=10
DATA_FILE=/var/data/bot_data.json
```

Health check path:

```text
/health
```

## Muhim

`.env` fayl Render'ga yuklanmaydi. Render Dashboard ichidagi **Environment** bo'limiga qiymatlarni qo'ying.

Bot admin paneldan qo'shilgan ilovalar va foydalanuvchilarni JSON faylga yozadi. Ma'lumotlar yo'qolmasligi uchun persistent disk kerak. Blueprint `disk` ni `/var/data` ga ulaydi va bot `DATA_FILE=/var/data/bot_data.json` orqali shu diskka yozadi.
