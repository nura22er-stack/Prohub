# ProHub Bot - Telegram Premium App Distribution Bot

Foydalanuvchilarga premium va MOD ilovalarni bepul yuklab olish imkoniyatini beruvchi Telegram boti.

## 🎯 Xususiyatlari

- **Majburiy obuna tizimi** - Foydalanuvchilar botni ishlatishdan oldin belgilangan kanalga obuna bo'lishi kerak
- **Asosiy menyu** - 7 ta asosiy tugma (barcha ilovalar, eng ko'p yuklanganlar, random, qidiruv, yuklamalarim, referal, yordam)
- **Qidiruv tizimi** - Ilova nomi yoki kod orqali qidirish
- **Referal tizim** - Do'st taklif qilish uchun link, 2 ta do'st taklif qilgandan keyin qimmatli ilovalar ochiladi
- **Admin panel** - Ilova qo'shish, o'chirish, statistika, reklama yuborish
- **Statistika** - Jami ilovalar, foydalanuvchilar, yuklanishlar
- **Veb-sayt** - Glassmorphism dizaynli website
- **API** - RESTful API bilan integratsiya

## 📦 Loyiha Tuzilishi

```
ProHub-Bot/
├── bot/
│   ├── __init__.py
│   ├── config.py          # Konfiguratsiya
│   ├── database.py        # Ma'lumotlar bazasi
│   ├── handlers.py        # Handler funksiyalari
│   └── main.py            # Asosiy bot fayli
├── api/
│   ├── __init__.py
│   └── app.py             # API server
├── website/
│   ├── static/
│   │   ├── style.css      # Uslublar
│   │   └── script.js      # JavaScript
│   ├── templates/
│   │   └── index.html     # Asosiy sahifa
│   └── app.py             # Web server
├── data/
│   └── bot_data.json      # Ma'lumotlar faylı
├── .env.example           # Konfiguratsiya shabloni
├── requirements.txt       # Dependency
└── README.md             # Bu fayl
```

## 🚀 O'rnatish

### 1. Repositoriyani klonlash
```bash
git clone https://github.com/your-repo/ProHub-Bot.git
cd ProHub-Bot
```

### 2. Virtual muhitni yaratish
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Dependency o'rnatish
```bash
pip install -r requirements.txt
```

### 4. Konfiguratsiyani o'rnatish
```bash
# .env.example ni .env ga nusxalang
cp .env.example .env

# .env faylini o'zingizning ma'lumotlari bilan to'ldiring:
# - BOT_TOKEN: Telegram Bot Token (@BotFather dan)
# - ADMIN_ID: Admin Telegram ID
# - CHANNEL_ID: Kanal ID (skaityish uchun -100 qo'shish kerak)
# - Boshqa sozlamalar
```

## 🤖 Botni ishga tushirish

### Asosiy bot
```bash
python bot/main.py
```

### API Server
```bash
python api/app.py
```

### Website
```bash
python website/api_app.py
```

## 📋 Telegram Bot Komandalari

| Komanda | Funksiya |
|---------|----------|
| `/start` | Botni ishga tushirish |
| `/admin` | Admin panelga kirish (faqat admin) |
| `/id` | Foydalanuvchi ID sini ko'rsatish |
| `/get_KOD` | Kod orqali ilovani yuklash |

## 🎮 Bot Tugmalari

### Asosiy menyu
- 📱 **Barcha ilovalar** - Ilovalarni sahifalab ko'rsatish
- 🔥 **Eng ko'p yuklanganlar** - TOP 5 ilovalar
- 🎲 **Tasodifiy ilova** - Random ilova tavsiyasi
- 🔍 **Qidirish** - Ilova nomi yoki kod bilan qidirish
- 📥 **Mening yuklamalarim** - Foydalanuvchi yuklagan ilovalar tarixi
- 👥 **Referal havola** - Do'st taklif qilish uchun link
- ℹ️ **Yordam** - Botdan foydalanish bo'yicha ma'lumot

### Admin panel
- ➕ **Ilova qo'shish** - Yangi ilova qo'shish (rasm + fayl)
- 📊 **Statistika** - Bot statistikasi
- 📦 **Ilovalar ro'yxati** - Barcha ilovalar ro'yxati
- 🗑 **Ilova o'chirish** - Kod orqali ilova o'chirish
- 📢 **Reklama yuborish** - Barcha foydalanuvchilarga xabar
- 📁 **Data fayl** - Ma'lumotlar haqida

## 📊 Ma'lumotlar Bazasi Tuzilishi

### apps
```json
{
  "code": "1",
  "name": "Ilova nomi",
  "file_id": "Telegram fayl ID",
  "file_name": "fayl.apk",
  "image": "rasm_file_id",
  "downloads": 0,
  "active": true,
  "added_at": "2024-01-01T00:00:00Z"
}
```

### users
```json
{
  "id": "123456789",
  "username": "user",
  "first_name": "Ism",
  "joined_at": "2024-01-01T00:00:00Z",
  "last_active": "2024-01-01T00:00:00Z",
  "downloads": ["1", "2"],
  "referred_by": "987654321"
}
```

## 🔗 API Endpoints

### Statistika
- `GET /api/stats` - Bot statistikasi

### Ilovalar
- `GET /api/apps` - Barcha ilovalar (pagination)
- `GET /api/apps/<code>` - Kod orqali ilova
- `GET /api/apps/search?q=query` - Qidiruv
- `GET /api/top-apps` - Eng ko'p yuklanganlar

### Yuklanishlar
- `GET /api/stats/downloads` - Yuklanish statistikasi
- `GET /api/users/count` - Jami foydalanuvchilar

## 🛠 Konfiguratsiya (.env)

```env
BOT_TOKEN=your_telegram_bot_token_here
BOT_USERNAME=@your_bot_username
REQUIRED_CHANNEL=@your_channel_username
CHANNEL_ID=-1001234567890
ADMIN_ID=your_admin_telegram_id
APPS_PER_PAGE=10
API_PORT=5000
API_HOST=0.0.0.0
```

## 📲 Sayt

Website `http://localhost:5000` da ishga tushmaydi, API `5000` portda ishga tushadi.

Website uchun:
```bash
python website/app.py  # Port 5001 da
```

## 🔐 Xavfsizlik

- Admin sessiya 1 soat uchun amal qiladi
- Foydalanuvchi ID bilan kirish
- Admin ID tekshiriladi

## 🐛 Muammoni bartaraf etish

### Bot Telegram bilan bog'lanayotgani yo'q
- `BOT_TOKEN` ni tekshiring
- Internetga bog'lanish bor-yo'q tekshiring
- Bot @BotFather bilan faolmi tekshiring

### Admin panelga kirilmayapti
- `ADMIN_ID` o'zingizning ID ingiz ekanligini tekshiring
- `/id` komandasidan foydalaning

### Ilovalar kanalga post bolmayapti
- `CHANNEL_ID` ni tekshiring (- bilan boshlangan bo'lishi kerak)
- Bot kanalda adminmi tekshiring

## 📝 Litsenziya

MIT

## 👨‍💻 Muallif

ProHub Bot Development Team

## 📞 Bog'lanish

- Telegram: [@ProHubBot](https://t.me/ProHubBot)
- Kanal: [@ProHubChannel](https://t.me/ProHubChannel)

---

**Izohlar**: Bu loyiha tahrirlash uchun tayyor. O'zingizning talablaringizga muvofiq tahrir qiling.
