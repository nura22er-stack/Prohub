# ProHub Bot - Setup Instructions

## 🚀 Tez o'rnatish (Quick Start)

### Windows
1. `.env.example` ni nusxalang va `.env` qilib o'zgartiring
2. `.env` faylida ma'lumotlarni to'ldiring (BOT_TOKEN, ADMIN_ID, CHANNEL_ID)
3. `start.bat` ni ishga tushiring (Double click)

### Linux/Mac
```bash
# .env.example ni nusxalang
cp .env.example .env

# .env faylida ma'lumotlarni to'ldiring
nano .env

# Skriptni executable qiling
chmod +x start.sh

# Botni ishga tushiring
./start.sh
```

## 📋 O'rnatish bosqichlari

### 1️⃣ Requirements o'rnatish
```bash
pip install -r requirements.txt
```

### 2️⃣ .env konfiguratsiyasi

`.env.example` ni `.env` ga nusxalang va quyidagi ma'lumotlarni to'ldiring:

```
BOT_TOKEN=123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijk
BOT_USERNAME=@your_bot_username
REQUIRED_CHANNEL=@your_channel_username
CHANNEL_ID=-1001234567890
ADMIN_ID=123456789
APPS_PER_PAGE=10
API_PORT=5000
```

**Qayerdan olish:**
- `BOT_TOKEN`: [@BotFather](https://t.me/BotFather) dan `/newbot` bilan
- `ADMIN_ID`: `/id` komandasidan
- `CHANNEL_ID`: Kanalga post yuboring va `@raw.github.io` da ID sini oling

### 3️⃣ Bot ishga tushirish

Har bir komponent alohida terminal/CMD windowda ishga tushing:

**Terminal 1 - Bot:**
```bash
python bot/main.py
```

**Terminal 2 - API:**
```bash
python api/app.py
```

**Terminal 3 - Website:**
```bash
python website/api_app.py
```

## 🔧 Konfiguratsiya

### config.py
Bot konfiguratsiyasi `bot/config.py` da:
- BOT_TOKEN: Telegram bot tokeni
- ADMIN_ID: Admin ID raqami
- CHANNEL_ID: Kanal ID raqami
- APPS_PER_PAGE: Sahifada ko'rsatilgan ilovalar soni

### Database
Ma'lumotlar `data/bot_data.json` da saqlanadi.

## ✅ Tekshirish

Bot ishga tushgani to'g'ri-yo'q tekshirish:

1. `@BotFather` ga `/start` yuboring
2. Botga `/start` yuboring
3. `/id` komandasini sinab ko'ring
4. Admin bo'lsangiz `/admin` ni sinab ko'ring

## 🚨 Muammolar

### "BotCommandError" xatosi
- BOT_TOKEN to'g'ri ekanligini tekshiring
- Token hali active ekanligini tekshiring

### Kanalga post bolmayapti
- CHANNEL_ID ni tekshiring (minus bilan boshlangan bo'lishi kerak)
- Bot kanalda admin ekanligini tekshiring

### API ishga tushmuyor
- Port 5000 band emasligini tekshiring
- `netstat -an | grep 5000` (Linux/Mac) yoki `netstat -an | findstr 5000` (Windows)

## 📚 Qo'shimcha ma'lumot

- [python-telegram-bot hujjati](https://python-telegram-bot.readthedocs.io/)
- [Flask hujjati](https://flask.palletsprojects.com/)
- [Telegram Bot API](https://core.telegram.org/bots/api)

## 🆘 Yordamga muhtoj?

Masalalar va takliflar uchun GitHub Issues ochib qo'ying.
