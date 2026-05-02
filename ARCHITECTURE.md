# ProHub Bot - Arxitektura va Tuzilish

## 📐 Umumi Arxitektura

```
┌─────────────────────────────────────────────┐
│         Telegram Bot Server                 │
│  (python-telegram-bot / bot/main.py)        │
└────────────┬────────────────────────────────┘
             │ Callback Queries & Messages
             ├─────────────────────────────┐
             │                             │
    ┌────────▼────────┐      ┌────────────▼──────────┐
    │  User Input     │      │   Admin Input        │
    │  Handlers       │      │   Handlers           │
    └────────┬────────┘      └────────────┬─────────┘
             │                           │
             └───────────────┬───────────┘
                            │
                    ┌───────▼────────┐
                    │  bot/handlers  │
                    │  (Logic)       │
                    └───────┬────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
   ┌────▼──────┐   ┌───────▼────────┐   ┌──────▼─────────┐
   │  Database │   │  Telegram API  │   │  Channel Posts │
   │  JSON     │   │  (send/recv)   │   │  Notifications │
   └────┬──────┘   └────────────────┘   └────────────────┘
        │
   ┌────▼────────────────────────────────┐
   │  data/bot_data.json                 │
   │  ├─ apps[]                          │
   │  ├─ users[]                         │
   │  ├─ admin_session{}                 │
   │  └─ state{}                         │
   └─────────────────────────────────────┘

         ┌──────────────────────────────┐
         │     API Server               │
         │  (Flask / api/app.py)        │
         └──────────┬───────────────────┘
                    │
         ┌──────────▼──────────────┐
         │  REST Endpoints         │
         │  /api/stats             │
         │  /api/apps              │
         │  /api/top-apps          │
         │  /api/search            │
         └──────────┬──────────────┘
                    │
         ┌──────────▼──────────────┐
         │  Database Access        │
         │  bot/database.py        │
         └─────────────────────────┘

    ┌───────────────────────────────────┐
    │    Website Server                 │
    │  (Flask / website/api_app.py)    │
    └────────────┬──────────────────────┘
                 │
    ┌────────────▼──────────────┐
    │  HTML/CSS/JS             │
    │  ├─ templates/index.html │
    │  ├─ static/style.css     │
    │  └─ static/script.js     │
    └─────────────────────────┘
```

## 📁 Fayl Tuzilishi

### bot/ - Asosiy Bot Modul

#### config.py
- Telegram bot tokenini va sozlamalarini saqlaydi
- Environment variables dan o'qiydi (.env dan)
- Constants: ADMIN_ID, CHANNEL_ID, APPS_PER_PAGE, etc.

```python
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID'))
DATA_FILE = 'data/bot_data.json'
```

#### database.py
Ma'lumotlar bazasi bilan ishlash:
- JSON fayldan o'qish/yozish
- User management (add, get, referral)
- App management (add, delete, search, paginate)
- Admin session management
- User state management
- Statistics

**Asosiy methodlar:**
```python
db.add_user(user_id, username, first_name)
db.get_user(user_id)
db.add_app(name, file_id, file_name, image_id)
db.get_app_by_code(code)
db.get_all_apps()
db.increment_download(code, user_id)
db.get_stats()
```

#### handlers.py
Helper funksiyalar va inline tugmalar:
- `check_subscription()` - Kanal obunasini tekshiring
- `get_main_menu_keyboard()` - Asosiy menyu
- `get_admin_menu_keyboard()` - Admin paneli
- `get_apps_keyboard()` - Ilovalar ro'yxati
- `generate_referral_link()` - Referal link
- `parse_referral_code()` - Referal kodni parse qilish
- `send_to_channel()` - Kanalga post yuboring

#### main.py
Asosiy bot fayli:
- Telegram Application yaratish va konfiguratsiya
- Command handlers (/start, /admin, /id, /get_CODE)
- Callback query handlers (inline button clicks)
- Message handlers (user text input)
- Bot polling start

**Asosiy funktsiyalar:**
```python
start_command()          # /start
admin_command()          # /admin
list_apps()              # Ilovalar ro'yxati
download_app()           # Ilovani yuklash
search_app()             # Qidiruv
my_downloads()           # Mening yuklamalarim
referral_link()          # Referal link
top_apps()               # Eng ko'p yuklanganlar
random_app()             # Random ilova
admin_add_app()          # Ilova qo'shish
admin_stats()            # Statistika
admin_list_apps()        # Ilovalar ro'yxati (admin)
admin_delete_app()       # Ilova o'chirish
admin_broadcast()        # Reklama yuborish
```

### api/ - REST API Server

#### app.py
Flask asosida REST API:

**Endpoints:**
```
GET /api/stats              - Statistika (apps, users, downloads)
GET /api/apps               - Barcha ilovalar (pagination)
GET /api/apps/<code>        - Kod orqali ilova
GET /api/apps/search?q=     - Qidiruv
GET /api/top-apps           - Eng ko'p yuklanganlar
GET /api/stats/downloads    - Yuklanish statistikasi
GET /api/users/count        - Foydalanuvchilar soni
GET /health                 - Health check
```

### website/ - Veb-sayt

#### app.py / api_app.py
Flask asosida veb-sayt:
- HTML template bilan indeks sahifasi
- API bilan integratsiya
- Glassmorphism dizayn

#### templates/index.html
Asosiy veb-sahifa:
- Hero section
- Statistics cards
- Top apps grid
- Features section
- About section
- Footer

#### static/style.css
Stillar:
- Glassmorphism effekti
- Responsive design
- Dark theme
- Animations

#### static/script.js
Frontend JavaScript:
- API dan ma'lumotlarni yuklash
- DOM yangilash
- Smooth scrolling
- Interval refresh

## 🔄 Ish Jarayonlari

### 1. Bot Ishga Tushirish

```
User /start qo'shnadi
     ↓
check_subscription(user_id)
     ↓
Obuna qilgan?
     ├─ Ha → main_menu()
     └─ Yo'q → subscription_keyboard()
```

### 2. Ilova Qo'shish (Admin)

```
admin /admin qo'shnadi
     ↓
db.set_admin_session(admin_id)
     ↓
admin_menu() ko'rsatish
     ↓
"➕ Ilova qo'shish" bosildi
     ↓
admin_add_app() - waiting_for_app_image
     ↓
Rasm yuborildi
     ↓
waiting_for_app_name
     ↓
Nom kiritildi
     ↓
waiting_for_app_file
     ↓
Fayl yuborildi
     ↓
db.add_app(name, file_id, file_name, image_id)
     ↓
Avtomatik kod beriladi
     ↓
send_to_channel(app) - kanalga post
     ↓
✅ Ilova qo'shildi
```

### 3. Ilovani Yuklash

```
User "📦 YUKLASH" bosildi
     ↓
download_app(app_code)
     ↓
db.get_app_by_code(app_code)
     ↓
db.increment_download(app_code, user_id)
     ↓
context.bot.send_document(file_id)
     ↓
✅ Fayl yuborildi
```

### 4. Referal Tizim

```
User botni ref_ID bilan ishga tushirdi
     ↓
parse_referral_code(ref_ID)
     ↓
db.set_referrer(user_id, referrer_id)
     ↓
referral_link() -> ko'rsatish
     ↓
db.get_referrals(user_id) -> count
     ↓
2 ta taklif qilsa → 🎉
```

## 💾 Ma'lumotlar Bazasi

### JSON Tuzilishi

```json
{
  "apps": [
    {
      "code": "1",
      "name": "App Name",
      "file_id": "AgACAgIA...",
      "file_name": "app.apk",
      "image": "AgACAgIA...",
      "downloads": 100,
      "active": true,
      "added_at": "2024-01-01T00:00:00Z"
    }
  ],
  "users": [
    {
      "id": "123456789",
      "username": "user",
      "first_name": "Name",
      "joined_at": "2024-01-01T00:00:00Z",
      "last_active": "2024-01-01T00:00:00Z",
      "downloads": ["1", "2"],
      "referred_by": null
    }
  ],
  "admin_session": {
    "123456789": {"expires": 1234567890}
  },
  "state": {
    "123456789": {"action": "waiting_for_search"}
  }
}
```

## 🔐 Xavfsizlik

### Admin Session
- Faqat ADMIN_ID bilan ishlaydi
- 1 soatlik sessiya timeout
- `is_admin_authenticated()` bilan tekshiriladi
- Sessiya tugasa `/admin` qayta kirishga majbur

### Obuna Tekshiruvi
- `check_subscription()` kanal obunasini tekshiradi
- Status: member, administrator, creator
- Obuna bo'lmaganlarga "Kanalga o'tish" tugmasi ko'rsatiladi

### Malicious Input
- Callback data validation
- User state management
- Admin session verification

## 📊 Performance

### Database
- JSON fayldan o'qish/yozish (small-scale uchun yetarli)
- Pagination (10 ilova/sahifa default)
- Caching through state management

### Bot
- Inline keyboards (tez javob)
- Callback queries (minimal traffic)
- User state tracking (efficient)

### API
- Flask lightweight
- CORS enabled
- Health check endpoint

## 🛠 Kengaytirish

### Yangi Feature Qo'shish

1. **Database method** → database.py da qo'shish
2. **Handler function** → handlers.py da qo'shish
3. **Main bot callback** → main.py da handler qo'shish
4. **API endpoint** → api/app.py da endpoint qo'shish
5. **Website UI** → HTML/CSS/JS yangilash

### Misollar

**Yangi Button Qo'shish:**
```python
# handlers.py
keyboard.append([InlineKeyboardButton("🆕 Yangi tugma", callback_data="new_button")])

# main.py
app.add_handler(CallbackQueryHandler(new_button_handler, pattern="^new_button$"))

async def new_button_handler(update, context):
    # Logic here
    pass
```

**Yangi API Endpoint:**
```python
# api/app.py
@app.route('/api/new-endpoint', methods=['GET'])
def new_endpoint():
    data = db.get_something()
    return jsonify(data)
```

## 🐛 Debug

### Bot Debug
- Logging enabled in main.py
- Print statements o'shiring
- Message/callback data verify qiling

### Database Debug
- data/bot_data.json ni to'g'ridan-to'g'ri tekshiring
- db.load_data() bilan verify qiling

### API Debug
- http://localhost:5000/health request yuboring
- Chrome DevTools Network tab-iga qarang

## 📈 Scale Qilish

### SQL Database
1. SQLite/PostgreSQL o'rnatish
2. database.py ni SQL adapter yozish
3. Connection pooling qo'shish

### Distributed Bot
1. Redis session storage
2. Message queue (RabbitMQ, Celery)
3. Load balancing

### Kubernetes
1. Docker image yaratish
2. K8s deployment configs
3. Helm charts

---

**Version:** 1.0  
**Last Updated:** 2024-01-20  
**Maintainer:** ProHub Bot Team
