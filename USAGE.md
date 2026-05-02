# ProHub Bot - Foydalanish Qo'llanmasi

## 👤 Foydalanuvchi Uchun

### Bot Bilan Ishlash

1. **Botni Ishga Tushirish**
   ```
   Telegram da @BotUsername ni qidirib, /start yuboring
   ```

2. **Kanalga Obuna Bo'lish**
   - Agar kanalga obuna bo'lmagansiz, "📢 Kanalga o'tish" tugmasini bosing
   - "✅ Obunani tekshirish" tugmasini bosing

3. **Ilovalarni Ko'rish**
   - **📱 Barcha ilovalar** - Barcha ilovalarni sahifalab ko'rish
   - **🔥 Eng ko'p yuklanganlar** - TOP 5 ilovalar
   - **🎲 Tasodifiy ilova** - Random ilova tavsiyasi

4. **Ilovani Yuklash**
   - Ilovalar ro'yxatidan "📦 YUKLASH" tugmasini bosing
   - Fayl to'g'ridan-to'g'ri sizga yuboriladi

5. **Qidiruv**
   - "🔍 Qidirush" tugmasini bosing
   - Ilova nomi yoki kodini kiriting
   - Natija ko'rsatiladi

6. **Referal Havola**
   - "👥 Referal havola" tugmasini bosing
   - O'z havolangizni do'stlaringizga yuboring
   - 2 ta do'st taklif qilganda qimmatli ilovalar ochiladi

7. **Foydalanuvchi ID**
   - `/id` komandasini yuboring
   - ID ko'rsatiladi

### Komandalari

| Komanda | Funksiya |
|---------|----------|
| `/start` | Botni ishga tushirish |
| `/id` | Sizning Telegram ID sini ko'rsatish |
| `/get_KOD` | Kod orqali ilovani yuklash (masalan: `/get_1`) |

**Misollar:**
```
/get_1         → Code 1 orqali ilovani yuklash
/get_123       → Code 123 orqali ilovani yuklash
```

## 🔧 Admin Uchun

### Admin Panelga Kirish

1. Bot adminiga `/admin` komandasini yuboring
2. Admin paneli ochiladi

### Admin Tugmalari

1. **➕ Ilova Qo'shish**
   - Rasm yuboring (PNG/JPG)
   - Ilova nomini kiriting
   - APK/ZIP faylni yuboring
   - Avtomatik kod beriladi
   - Kanalga post yuboriladi

2. **📊 Statistika**
   - Jami ilovalar soni
   - Jami foydalanuvchilar soni
   - Jami yuklanishlar soni

3. **📦 Ilovalar Ro'yxati**
   - Barcha ilovalar ro'yxati
   - Kod va yuklanish soni ko'rsatiladi

4. **🗑 Ilova O'chirish**
   - O'chirmoqchi bo'lgan ilovaning kodini kiriting
   - Ilova o'chiriladi (inactive bo'lib qoladi)

5. **📢 Reklama Yuborish**
   - Barcha foydalanuvchilarga xabar yuboring
   - Xabar kiritib yuboring
   - Jami yuborilgan users soni ko'rsatiladi

6. **📁 Data Fayl**
   - JSON data faylini ko'rish
   - Bot_data.json ichidagi ma'lumotlar

7. **❌ Chiqish**
   - Admin sessiyasini tugatib, chiqing

### Admin Komandalari

| Komanda | Funksiya |
|---------|----------|
| `/admin` | Admin panelga kirish |
| `/id` | ID ni ko'rsatish |

### Ilova Qo'shish Jarayoni

```
1. /admin → Admin paneli
2. ➕ Ilova qo'shish → Button bosing
3. 📸 Rasm yuboring → PNG/JPG fayl
4. 📝 Nom kiriting → Masalan: "Instagram MOD"
5. 📦 Fayl yuboring → APK/ZIP fayl
6. ✅ Ilova qo'shildi!
   - Avtomatik kod beriladi
   - Kanalga post yuboriladi
   - Barcha userslarga bildiriladi
```

## 💻 Developer Uchun

### Environment Setup

```bash
# Virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows

# Dependencies
pip install -r requirements.txt

# Configuration
cp .env.example .env
# .env ni configure qiling
```

### Bot Ishga Tushirish

**Yo'l 1: Alohida Terminallar**
```bash
# Terminal 1
python bot/main.py

# Terminal 2
python api/app.py

# Terminal 3
python website/api_app.py
```

**Yo'l 2: Start Script (Windows)**
```bash
start.bat
```

**Yo'l 3: Start Script (Linux/Mac)**
```bash
chmod +x start.sh
./start.sh
```

### Database Bilan Ishlash

```python
from bot.database import Database

db = Database()

# Users
db.add_user(123456789, "username", "First Name")
user = db.get_user(123456789)
users = db.get_all_users()

# Apps
app_code = db.add_app("App Name", "file_id", "file.apk", "image_id")
app = db.get_app_by_code("1")
apps = db.get_all_apps()
db.increment_download("1", 123456789)

# Stats
stats = db.get_stats()
# {'total_apps': 3, 'total_users': 10, 'total_downloads': 150}

# Search
results = db.get_app_by_name("Instagram")
top_apps = db.get_top_apps(5)
```

### API Bilan Ishlash

```bash
# Stats
curl http://localhost:5000/api/stats

# Apps
curl http://localhost:5000/api/apps?page=1&per_page=10

# Top apps
curl http://localhost:5000/api/top-apps?limit=5

# Search
curl "http://localhost:5000/api/apps/search?q=Instagram"

# Health
curl http://localhost:5000/health
```

### Custom Handler Qo'shish

```python
# main.py da
async def my_custom_handler(update, context):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Salom!")

# Handler ro'yxatiga qo'shish
app.add_handler(CallbackQueryHandler(my_custom_handler, pattern="^my_pattern$"))
```

## 📱 Telegram Commands Reference

### Inline Buttons (Tugmalar)

**Main Menu**
```
📱 Barcha ilovalar
🔥 Eng ko'p yuklanganlar
🎲 Tasodifiy ilova
🔍 Qidirush
📥 Mening yuklamalarim
👥 Referal havola
ℹ️ Yordam
```

**Apps List**
```
📦 App Name (downloads count)
◀️ Oldingi | Page/Total | Keyingi ▶️
⬅️ Bosh menyu
```

**Admin Menu**
```
➕ Ilova qo'shish
📊 Statistika
📦 Ilovalar ro'yxati
🗑 Ilova o'chirish
📢 Reklama yuborish
📁 Data fayl
❌ Chiqish
```

## 🔍 Troubleshooting

### Bot Javob Bermayapti

**Yechim:**
1. BOT_TOKEN to'g'ri ekanligini tekshiring
2. @BotFather da `/mybots` → token
3. Bot active ekanligini tekshiring

### Admin Panel Ishga Tushmuyor

**Yechim:**
1. ADMIN_ID ni tekshiring (`/id` komandasidan)
2. .env da to'g'ri ID bo'lsin
3. Admin session timeout bo'lgan bo'lishi mumkin (`/admin` qayta bosing)

### Ilovalar Kanalga Post Bolmayapti

**Yechim:**
1. CHANNEL_ID ni tekshiring (minus bilan boshlangan bo'lishi kerak)
2. Bot kanalda admin ekanligini tekshiring
3. Channel ID: `https://t.me/c/1001234567890` → `-1001234567890`

### API Ishga Tushmuyor

**Yechim:**
1. Port 5000 band emasligini tekshiring
2. Flask o'rnatilganligini tekshiring: `pip list | grep Flask`
3. Localhost da: `http://localhost:5000/health`

### Database Xatosi

**Yechim:**
1. `data/` papka mavjud ekanligini tekshiring
2. `bot_data.json` ruxsatlari tekshiring
3. JSON faylning formatini tekshiring (valid JSON bo'lsin)

## 📚 Foydaliy Linklar

- 🤖 [Telegram Bot API](https://core.telegram.org/bots/api)
- 🐍 [python-telegram-bot](https://python-telegram-bot.readthedocs.io/)
- 🍶 [Flask Docs](https://flask.palletsprojects.com/)
- 📖 [Python Docs](https://docs.python.org/3/)

## 💡 Tips & Tricks

### Tez Debugging

```python
# Logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Print user info
print(f"User: {update.effective_user.id}")
print(f"Message: {update.message.text}")
print(f"Callback: {update.callback_query.data}")
```

### Bot Testing

```bash
# Health check
curl -s http://localhost:5000/health | jq .

# Stats
curl -s http://localhost:5000/api/stats | jq .

# User count
curl -s http://localhost:5000/api/users/count | jq .
```

### Database Backup

```bash
# JSON faylni nusxalash
cp data/bot_data.json data/bot_data.backup.json

# Eski version qaytarish
cp data/bot_data.backup.json data/bot_data.json
```

## 🚀 Performance Tips

1. **Pagination** - 10 ilova/sahifa to'g'ri
2. **Caching** - Website statistika har 30 soniyada refresh bo'ladi
3. **Database** - JSON optimal small-scale uchun, SQL scale uchun
4. **API** - CORS enabled, lightweight endpoints

---

**Last Updated:** 2024-01-20  
**Version:** 1.0
