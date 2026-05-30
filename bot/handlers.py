import requests
from telegram import ChatAction, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from .config import BOT_USERNAME
from .database import Database

db = Database()


def check_subscription(user_id: int, context: CallbackContext) -> bool:
    """Check if user is subscribed to required channel"""
    channels = db.get_required_channels()
    if not channels:
        return True

    for channel in channels:
        try:
            member = context.bot.get_chat_member(channel["id"], user_id)
            if member.status not in ['member', 'administrator', 'creator']:
                return False
        except:
            return False
    return True


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Get main menu keyboard"""
    keyboard = [
        [InlineKeyboardButton("📱 Barcha ilovalar", callback_data="list_apps_1")],
        [InlineKeyboardButton("🔥 Eng ko'p yuklanganlar", callback_data="top_apps")],
        [InlineKeyboardButton("🎲 Tasodifiy ilova", callback_data="random_app")],
        [InlineKeyboardButton("🔍 Qidirish", callback_data="search_app")],
        [InlineKeyboardButton("📥 Mening yuklamalarim", callback_data="my_downloads")],
        [InlineKeyboardButton("👥 Referal havola", callback_data="referral_link")],
        [InlineKeyboardButton("ℹ️ Yordam", callback_data="help")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_admin_menu_keyboard() -> InlineKeyboardMarkup:
    """Get admin panel keyboard"""
    keyboard = [
        [InlineKeyboardButton("➕ Ilova qo'shish", callback_data="admin_add_app")],
        [InlineKeyboardButton("📊 Statistika", callback_data="admin_stats")],
        [InlineKeyboardButton("📦 Ilovalar ro'yxati", callback_data="admin_list_apps")],
        [InlineKeyboardButton("🗑 Ilova o'chirish", callback_data="admin_delete_app")],
        [InlineKeyboardButton("👮 Adminlar", callback_data="admin_manage_admins")],
        [InlineKeyboardButton("📢 Majburiy kanallar", callback_data="admin_manage_channels")],
        [InlineKeyboardButton("📢 Reklama yuborish", callback_data="admin_broadcast")],
        [InlineKeyboardButton("📁 Data fayl", callback_data="admin_data_file")],
        [InlineKeyboardButton("❌ Chiqish", callback_data="admin_logout")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_subscription_keyboard() -> InlineKeyboardMarkup:
    """Get subscription keyboard"""
    keyboard = []
    for idx, channel in enumerate(db.get_required_channels(), 1):
        username = channel.get("username")
        if username:
            keyboard.append([
                InlineKeyboardButton(
                    f"📢 Kanal {idx}",
                    url=f"https://t.me/{username.lstrip('@')}"
                )
            ])
    keyboard.append([InlineKeyboardButton("✅ Obunani tekshirish", callback_data="check_subscription")])
    return InlineKeyboardMarkup(keyboard)


def get_apps_keyboard(apps: list, page: int, total_pages: int) -> InlineKeyboardMarkup:
    """Get apps list keyboard"""
    keyboard = []
    
    for app in apps:
        keyboard.append([InlineKeyboardButton(
            f"📦 {app['name']} ({app['downloads']} 📥)",
            callback_data=f"download_{app['code']}"
        )])
    
    # Pagination buttons
    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton("◀️ Oldingi", callback_data=f"list_apps_{page-1}"))
    nav_buttons.append(InlineKeyboardButton(f"{page}/{total_pages}", callback_data="pages"))
    if page < total_pages:
        nav_buttons.append(InlineKeyboardButton("Keyingi ▶️", callback_data=f"list_apps_{page+1}"))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    keyboard.append([InlineKeyboardButton("⬅️ Bosh menyu", callback_data="main_menu")])
    
    return InlineKeyboardMarkup(keyboard)


def get_back_button() -> InlineKeyboardMarkup:
    """Get back to main menu button"""
    keyboard = [
        [InlineKeyboardButton("⬅️ Bosh menyu", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def send_typing_action(context: CallbackContext, chat_id: int):
    """Send typing action"""
    context.bot.send_chat_action(chat_id, ChatAction.TYPING)


def send_document_action(context: CallbackContext, chat_id: int):
    """Send upload_document action"""
    context.bot.send_chat_action(chat_id, ChatAction.UPLOAD_DOCUMENT)


def generate_referral_link(user_id: int) -> str:
    """Generate referral link for user"""
    return f"https://t.me/{BOT_USERNAME.lstrip('@')}?start=ref_{user_id}"


def parse_referral_code(deep_link: str) -> int:
    """Parse referral code from deep link"""
    if deep_link.startswith("ref_"):
        try:
            return int(deep_link[4:])
        except ValueError:
            return None
    return None


def send_to_channel(context: CallbackContext, app: dict) -> bool:
    """Send app announcement to channel"""
    channels = db.get_required_channels()
    sent = False
    try:
        caption = f"🆕 Yangi ilova!\n\n📱 <b>{app['name']}</b>\n\n🔑 Kod: <code>{app['code']}</code>\n\n"
        caption += f"/get_{app['code']} - ilovani yuklash uchun\n"
        caption += f"\nYoki botdan: @{BOT_USERNAME.lstrip('@')}"

        for channel in channels:
            try:
                context.bot.send_photo(
                    chat_id=channel["id"],
                    photo=app['image'],
                    caption=caption,
                    parse_mode='HTML'
                )
                sent = True
            except Exception as e:
                print(f"Error sending to channel {channel['id']}: {e}")
        return sent
    except Exception as e:
        print(f"Error sending to channel: {e}")
        return False
