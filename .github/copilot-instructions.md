# ProHub Bot Copilot Instructions

## Project Overview

ProHub Bot is a comprehensive Telegram bot for distributing premium and modded applications to users. It includes:

- **Telegram Bot** (python-telegram-bot) with inline keyboards
- **REST API** (Flask) for data access
- **Website** (Flask + HTML/CSS/JS) with glassmorphism design
- **JSON Database** for data persistence
- **Admin Panel** for app management
- **Referral System** for user engagement

## Technology Stack

- **Language:** Python 3.8+
- **Bot Framework:** python-telegram-bot 20.3
- **Web Framework:** Flask 3.0.0
- **Database:** JSON file (data/bot_data.json)
- **Frontend:** HTML5, CSS3 (Glassmorphism), Vanilla JavaScript

## Project Structure

```
ProHub-Bot/
├── bot/                 # Telegram bot module
│   ├── config.py       # Configuration
│   ├── database.py     # JSON database handler
│   ├── handlers.py     # Helper functions
│   ├── main.py         # Bot entry point
│   └── __init__.py
├── api/                 # REST API server
│   ├── app.py          # Flask API
│   └── __init__.py
├── website/            # Website
│   ├── static/         # CSS, JS
│   ├── templates/      # HTML
│   ├── app.py          # Website entry
│   ├── api_app.py      # Website + API
│   └── __init__.py
├── data/               # Data storage
│   └── bot_data.json   # User & app data
├── .env.example        # Configuration template
├── requirements.txt    # Python dependencies
├── README.md           # Main documentation
├── SETUP.md            # Setup instructions
├── USAGE.md            # Usage guide
├── ARCHITECTURE.md     # Technical architecture
├── start.bat           # Windows startup script
└── start.sh            # Linux/Mac startup script
```

## Key Files and Their Purposes

### Core Bot Files

- **bot/config.py** - Load environment variables, define constants
- **bot/database.py** - Handle all JSON database operations (CRUD for apps, users, stats)
- **bot/handlers.py** - Keyboard layouts, helper functions, Telegram utilities
- **bot/main.py** - Bot handlers, command processing, callback management

### API & Website

- **api/app.py** - RESTful API endpoints for bot data
- **website/api_app.py** - Flask app combining website + API
- **website/templates/index.html** - Main website page
- **website/static/style.css** - Glassmorphism styling
- **website/static/script.js** - Frontend data loading

## Common Tasks

### Adding a New Feature

1. **Database**: Add method to `bot/database.py`
2. **Handler**: Add logic to `bot/handlers.py`
3. **Bot**: Add callback handler to `bot/main.py`
4. **API**: Add endpoint to `api/app.py`
5. **Website**: Update HTML/CSS/JS as needed

### Debugging

- Enable logging in `bot/main.py`
- Check `data/bot_data.json` for data consistency
- Use `/health` endpoint for API health check
- Review Python traceback in terminal

### Deployment

- Install dependencies: `pip install -r requirements.txt`
- Configure `.env` file with Telegram credentials
- Run `python bot/main.py` for bot
- Run `python api/app.py` for API
- Run `python website/api_app.py` for website

## Database Schema

### apps
```json
{
  "code": "1",                      // Unique app ID
  "name": "Instagram MOD",          // App name
  "file_id": "AgACAgIA...",        // Telegram file ID
  "file_name": "instagram.apk",    // Original filename
  "image": "AgACAgIA...",          // Telegram image ID
  "downloads": 100,                // Download count
  "active": true,                  // Active status
  "added_at": "2024-01-01T00:00:00Z"  // Added timestamp
}
```

### users
```json
{
  "id": "123456789",               // Telegram user ID
  "username": "john_doe",          // Telegram username
  "first_name": "John",            // User's first name
  "joined_at": "2024-01-01T00:00:00Z",  // Join date
  "last_active": "2024-01-01T00:00:00Z",  // Last activity
  "downloads": ["1", "2"],         // Downloaded app codes
  "referred_by": "987654321"       // Referrer user ID
}
```

## API Endpoints

### Statistics
- `GET /api/stats` - Total apps, users, downloads

### Applications
- `GET /api/apps?page=1&per_page=10` - Paginated apps
- `GET /api/apps/<code>` - Single app by code
- `GET /api/apps/search?q=query` - Search apps
- `GET /api/top-apps?limit=5` - Top downloaded

### Utility
- `GET /api/stats/downloads` - Download statistics
- `GET /api/users/count` - User count
- `GET /health` - API health check

## Configuration (.env)

```env
BOT_TOKEN=your_bot_token           # From @BotFather
BOT_USERNAME=@your_bot             # Bot username
REQUIRED_CHANNEL=@your_channel     # Subscription channel
CHANNEL_ID=-1001234567890          # Channel ID (with -100)
ADMIN_ID=123456789                 # Admin's Telegram ID
APPS_PER_PAGE=10                   # Apps per page
API_PORT=5000                      # API server port
API_HOST=0.0.0.0                   # API host
```

## Coding Standards

- Use type hints: `def func(user_id: int) -> bool:`
- Add docstrings: `"""Function description"""`
- Keep functions small and focused
- Use async/await for Telegram API calls
- Validate user input before processing
- Handle exceptions gracefully

## Testing

```bash
# Health check
curl http://localhost:5000/health

# Get stats
curl http://localhost:5000/api/stats

# Search apps
curl "http://localhost:5000/api/apps/search?q=Instagram"
```

## Performance Considerations

- JSON database is adequate for small-scale (< 10K users)
- Pagination limits data transfer (10 apps/page default)
- Bot uses inline keyboards for quick responses
- API includes CORS for cross-origin requests
- Website refreshes stats every 30 seconds

## Security Notes

- Admin ID verified for admin commands
- Admin sessions timeout after 1 hour
- Subscription check mandatory for users
- User state cleared after processing
- No sensitive data in logs
- File uploads through Telegram API (secure)

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Bot not responding | Check BOT_TOKEN, verify @BotFather |
| Admin panel denied | Verify ADMIN_ID matches your ID |
| No posts to channel | Check CHANNEL_ID format, bot is admin |
| API 404 error | Check endpoint URL, verify Flask running |
| Database error | Check data/bot_data.json permissions |

## Future Enhancement Ideas

1. **SQL Database** - Replace JSON with PostgreSQL
2. **Bot Analytics** - Advanced statistics dashboard
3. **Payment Integration** - Premium features
4. **Multi-language** - Language selection
5. **Admin Dashboard** - Web-based admin panel
6. **Notification System** - Push notifications
7. **Search Optimization** - Full-text search
8. **Rate Limiting** - API rate limits

## Useful Commands

```bash
# Run bot
python bot/main.py

# Run API
python api/app.py

# Run website
python website/api_app.py

# Install dev dependencies
pip install -r requirements-dev.txt

# Format code
black .

# Check code style
flake8 .

# Test database
python -c "from bot.database import Database; db = Database(); print(db.get_stats())"
```

## Documentation Files

- **README.md** - Project overview and features
- **SETUP.md** - Installation and configuration
- **USAGE.md** - User and admin guides
- **ARCHITECTURE.md** - Technical architecture details
- **This file** - Development guidelines

## Contact & Support

- Report bugs: GitHub Issues
- Suggest features: GitHub Discussions
- Ask questions: Telegram @ProHubBot

---

**Last Updated:** 2024-01-20  
**Version:** 1.0  
**Status:** Production Ready
