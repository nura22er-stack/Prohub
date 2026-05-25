import logging
import random
from telegram import Update, File, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler

from .config import BOT_TOKEN, APPS_PER_PAGE
from .database import Database
from .handlers import (
    check_subscription, get_main_menu_keyboard, get_admin_menu_keyboard,
    get_subscription_keyboard, get_apps_keyboard, get_back_button,
    generate_referral_link, parse_referral_code, send_to_channel,
    send_typing_action, send_document_action
)

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Database
db = Database()

# Conversation states
WAITING_FOR_APP_NAME, WAITING_FOR_APP_IMAGE, WAITING_FOR_APP_FILE = range(3)
WAITING_FOR_DELETE_CODE, WAITING_FOR_BROADCAST_MESSAGE, WAITING_FOR_SEARCH = range(3, 6)


def get_admin_back_keyboard() -> InlineKeyboardMarkup:
    """Get back to admin menu button"""
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Orqaga", callback_data="admin_menu")]])


def parse_channel_input(text: str) -> tuple:
    """Parse channel input: '<id> @username' or '@username'"""
    parts = text.strip().split()
    if not parts:
        return None, None

    if len(parts) == 1:
        value = parts[0]
        if value.startswith("-100") or value.lstrip("-").isdigit():
            return value, None
        return value, value

    return parts[0], parts[1]


# ==================== START COMMAND ====================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    message = update.message
    
    # Add user to database
    db.add_user(user.id, user.username, user.first_name)
    
    # Check for referral
    if context.args:
        referral_code = context.args[0]
        referrer_id = parse_referral_code(referral_code)
        if referrer_id:
            db.set_referrer(user.id, referrer_id)
    
    # Check subscription
    is_subscribed = await check_subscription(user.id, context)
    
    if not is_subscribed:
        await message.reply_text(
            f"👋 Salom, {user.first_name}!\n\n"
            "🔐 Botdan foydalanish uchun avval kanalga obuna bo'lishingiz kerak.",
            reply_markup=get_subscription_keyboard()
        )
    else:
        await message.reply_text(
            f"👋 Salom, {user.first_name}! 🎉\n\n"
            "Premium va MOD ilovalarni bepul yuklash botiga xush kelibsiz!",
            reply_markup=get_main_menu_keyboard()
        )


# ==================== MAIN MENU ====================
async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show main menu"""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🏠 <b>Asosiy menyu</b>\n\n"
        "Quyidagi tugmalardan biri tanlang:",
        reply_markup=get_main_menu_keyboard(),
        parse_mode='HTML'
    )


# ==================== LIST APPS ====================
async def list_apps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show apps with pagination"""
    query = update.callback_query
    
    # Extract page number from callback data
    callback_data = query.data
    page = int(callback_data.split('_')[-1])
    
    await query.answer()
    
    apps, total_pages = db.get_apps_paginated(page, APPS_PER_PAGE)
    
    if not apps:
        await query.edit_message_text(
            "❌ Ilovalar topilmadi.",
            reply_markup=get_back_button()
        )
        return
    
    text = "📱 <b>Barcha ilovalar</b>\n\n"
    for app in apps:
        text += f"🔹 <b>{app['name']}</b> (📥 {app['downloads']})\n"
    
    await query.edit_message_text(
        text,
        reply_markup=get_apps_keyboard(apps, page, total_pages),
        parse_mode='HTML'
    )


# ==================== TOP APPS ====================
async def top_apps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show top downloaded apps"""
    query = update.callback_query
    await query.answer()
    
    apps = db.get_top_apps(5)
    
    if not apps:
        await query.edit_message_text(
            "❌ Ilovalar topilmadi.",
            reply_markup=get_back_button()
        )
        return
    
    text = "🔥 <b>Eng ko'p yuklanganlar</b>\n\n"
    for idx, app in enumerate(apps, 1):
        text += f"{idx}. <b>{app['name']}</b> - 📥 {app['downloads']}\n"
    
    keyboard = []
    for app in apps:
        keyboard.append([
            InlineKeyboardButton(
                f"📦 {app['name']}",
                callback_data=f"download_{app['code']}"
            )
        ])
    keyboard.append([InlineKeyboardButton("⬅️ Bosh menyu", callback_data="main_menu")])
    
    from telegram import InlineKeyboardMarkup
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )


# ==================== RANDOM APP ====================
async def random_app(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send random app suggestion"""
    query = update.callback_query
    await query.answer()
    
    apps = db.get_all_apps()
    
    if not apps:
        await query.edit_message_text(
            "❌ Ilovalar topilmadi.",
            reply_markup=get_back_button()
        )
        return
    
    app = random.choice(apps)
    
    text = f"🎲 <b>Tasodifiy ilova</b>\n\n"
    text += f"📱 <b>{app['name']}</b>\n"
    text += f"📥 Yuklanishlar: {app['downloads']}\n"
    text += f"🔑 Kod: <code>{app['code']}</code>"
    
    from telegram import InlineKeyboardMarkup
    keyboard = [
        [InlineKeyboardButton("📥 Yuklash", callback_data=f"download_{app['code']}")],
        [InlineKeyboardButton("🎲 Yana biri", callback_data="random_app")],
        [InlineKeyboardButton("⬅️ Bosh menyu", callback_data="main_menu")]
    ]
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )


# ==================== DOWNLOAD ====================
async def download_app(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Download app"""
    query = update.callback_query
    
    # Extract app code from callback data
    app_code = query.data.split('_')[-1]
    app = db.get_app_by_code(app_code)
    
    if not app:
        await query.answer("❌ Ilova topilmadi!")
        return

    is_subscribed = await check_subscription(query.from_user.id, context)
    if not is_subscribed:
        await query.answer("❌ Avval majburiy kanallarga obuna bo'ling!", show_alert=True)
        await query.edit_message_text(
            "🔐 Botdan foydalanish uchun avval majburiy kanallarga obuna bo'lishingiz kerak.",
            reply_markup=get_subscription_keyboard()
        )
        return
    
    await query.answer()
    await send_document_action(context, query.from_user.id)
    
    # Increment download count
    db.increment_download(app_code, query.from_user.id)
    
    # Send file
    try:
        await context.bot.send_document(
            chat_id=query.from_user.id,
            document=app['file_id'],
            caption=f"✅ <b>{app['name']}</b> yuklandi!\n\n"
                   f"📊 Jami yuklanishlar: {db.get_app_by_code(app_code)['downloads']}",
            parse_mode='HTML'
        )
        await query.edit_message_text(
            f"✅ Fayl yuborildi!\n\n"
            f"📱 <b>{app['name']}</b> yuklab olinmoqda...\n"
            f"Fayl to'g'ridan-to'g'ri sizga yuborildi.",
            reply_markup=get_back_button(),
            parse_mode='HTML'
        )
    except Exception as e:
        logger.error(f"Error sending file: {e}")
        await query.edit_message_text(
            "❌ Xato! Fayl yuborilmadi.",
            reply_markup=get_back_button()
        )


# ==================== SEARCH ====================
async def search_app(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start search process"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "🔍 <b>Qidiruv</b>\n\n"
        "Ilova nomini yoki kodini kiriting:",
        reply_markup=get_back_button(),
        parse_mode='HTML'
    )
    
    # Set user state to waiting for search query
    db.set_user_state(query.from_user.id, {"action": "waiting_for_search"})


async def handle_search_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle search input"""
    message = update.message
    user_state = db.get_user_state(message.from_user.id)
    
    if not user_state or user_state.get("action") != "waiting_for_search":
        return
    
    search_query = message.text.strip()
    
    # Search by code first
    app = db.get_app_by_code(search_query)
    if app:
        await send_typing_action(context, message.from_user.id)
        text = f"📱 <b>Qidiruv natijasi</b>\n\n"
        text += f"📦 <b>{app['name']}</b>\n"
        text += f"📥 Yuklanishlar: {app['downloads']}\n"
        text += f"🔑 Kod: <code>{app['code']}</code>"
        
        from telegram import InlineKeyboardMarkup
        keyboard = [
            [InlineKeyboardButton("📥 Yuklash", callback_data=f"download_{app['code']}")],
            [InlineKeyboardButton("⬅️ Bosh menyu", callback_data="main_menu")]
        ]
        
        await message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )
        db.clear_user_state(message.from_user.id)
        return
    
    # Search by name
    apps = db.get_app_by_name(search_query)
    
    if not apps:
        await message.reply_text(
            f"❌ \"{search_query}\" bo'yicha ilovalar topilmadi.",
            reply_markup=get_back_button()
        )
        db.clear_user_state(message.from_user.id)
        return
    
    text = f"🔍 <b>Qidiruv natijasi: {len(apps)} ta ilova topildi</b>\n\n"
    
    from telegram import InlineKeyboardMarkup
    keyboard = []
    for app in apps[:10]:  # Show first 10 results
        keyboard.append([
            InlineKeyboardButton(
                f"📦 {app['name']} ({app['downloads']} 📥)",
                callback_data=f"download_{app['code']}"
            )
        ])
    keyboard.append([InlineKeyboardButton("⬅️ Bosh menyu", callback_data="main_menu")])
    
    await message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )
    
    db.clear_user_state(message.from_user.id)


# ==================== MY DOWNLOADS ====================
async def my_downloads(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user's download history"""
    query = update.callback_query
    await query.answer()
    
    user = db.get_user(query.from_user.id)
    
    if not user or not user["downloads"]:
        await query.edit_message_text(
            "📥 Hali ilovalar yuklab olmagansiz.",
            reply_markup=get_back_button()
        )
        return
    
    text = "📥 <b>Mening yuklamalarim</b>\n\n"
    
    from telegram import InlineKeyboardMarkup
    keyboard = []
    for code in user["downloads"]:
        app = db.get_app_by_code(code)
        if app:
            text += f"✅ {app['name']}\n"
            keyboard.append([
                InlineKeyboardButton(
                    f"📥 {app['name']}",
                    callback_data=f"download_{app['code']}"
                )
            ])
    
    keyboard.append([InlineKeyboardButton("⬅️ Bosh menyu", callback_data="main_menu")])
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )


# ==================== REFERRAL ====================
async def referral_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show referral link"""
    query = update.callback_query
    await query.answer()
    
    referral_link = generate_referral_link(query.from_user.id)
    referrals = db.get_referrals(query.from_user.id)
    
    text = f"👥 <b>Referal havola</b>\n\n"
    text += f"🔗 Sizning havolangiz:\n"
    text += f"<code>{referral_link}</code>\n\n"
    text += f"📊 Taklif qilgan foydalanuvchilar: {len(referrals)}/2\n\n"
    text += f"💡 2 ta do'st taklif qilgandan keyin qimmatli ilovalar ochiladi!"
    
    from telegram import InlineKeyboardMarkup
    keyboard = [
        [InlineKeyboardButton("📋 Nusxa olish", callback_data="copy_referral")],
        [InlineKeyboardButton("⬅️ Bosh menyu", callback_data="main_menu")]
    ]
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )


# ==================== HELP ====================
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help"""
    query = update.callback_query
    await query.answer()
    
    text = "ℹ️ <b>Yordam</b>\n\n"
    text += "<b>Bot haqida:</b>\n"
    text += "ProHub Bot - premium va MOD ilovalarni bepul yuklash botı.\n\n"
    text += "<b>Komandalari:</b>\n"
    text += "/start - Botni ishga tushirish\n"
    text += "/id - Sizning ID ingizni ko'rsatish\n"
    text += "/get_KOD - Kod orqali ilovani yuklash\n"
    text += "/admin - Admin panelga kirish (faqat admin)\n\n"
    text += "<b>Qo'shimcha:</b>\n"
    text += "• Qanday ilova topasiz? 🔍 Qidiruv tugmasidan foydalaning\n"
    text += "• Do'stlaringizni taklif qiling 👥 va qimmatli ilovalarni oching!\n"
    text += "• Bot haqida masalalar? Ruxsat etuvchi bilan bog'lanish.\n"
    
    await query.edit_message_text(
        text,
        reply_markup=get_back_button(),
        parse_mode='HTML'
    )


# ==================== ADMIN PANEL ====================
async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /admin command"""
    message = update.message
    user_id = message.from_user.id
    
    if not db.is_admin(user_id):
        await message.reply_text("❌ Siz admin emassiz!")
        return
    
    # Set admin session
    from .config import ADMIN_SESSION_TIMEOUT
    db.set_admin_session(user_id, ADMIN_SESSION_TIMEOUT)
    
    await message.reply_text(
        "🔧 <b>Admin Panel</b>\n\n"
        "Xush kelibsiz, admin!",
        reply_markup=get_admin_menu_keyboard(),
        parse_mode='HTML'
    )


async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show admin menu"""
    query = update.callback_query
    user_id = query.from_user.id
    
    if not db.is_admin(user_id):
        await query.answer("❌ Siz admin emassiz!", show_alert=True)
        return
    
    if not db.is_admin_authenticated(user_id):
        await query.answer("⏱ Sessiya tugadi! /admin bilan qayta kiringi", show_alert=True)
        return
    
    await query.answer()
    await query.edit_message_text(
        "🔧 <b>Admin Panel</b>",
        reply_markup=get_admin_menu_keyboard(),
        parse_mode='HTML'
    )


async def admin_add_app(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start adding new app"""
    query = update.callback_query
    user_id = query.from_user.id
    
    if not db.is_admin(user_id) or not db.is_admin_authenticated(user_id):
        await query.answer("⏱ Sessiya tugadi!", show_alert=True)
        return
    
    await query.answer()
    await query.edit_message_text(
        "📸 Rasm yuborish:\n\n"
        "Ilova uchun rasmini yuboring (PNG/JPG)",
        reply_markup=get_admin_back_keyboard()
    )
    
    db.set_user_state(user_id, {"action": "waiting_for_app_image"})


async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show admin statistics"""
    query = update.callback_query
    user_id = query.from_user.id
    
    if not db.is_admin(user_id) or not db.is_admin_authenticated(user_id):
        await query.answer("⏱ Sessiya tugadi!", show_alert=True)
        return
    
    await query.answer()
    
    stats = db.get_stats()
    text = f"📊 <b>Bot Statistikasi</b>\n\n"
    text += f"📱 Jami ilovalar: {stats['total_apps']}\n"
    text += f"👥 Jami foydalanuvchilar: {stats['total_users']}\n"
    text += f"📥 Jami yuklanishlar: {stats['total_downloads']}\n"
    text += f"👮 Adminlar: {stats['total_admins']}\n"
    text += f"📢 Majburiy kanallar: {stats['total_required_channels']}"
    
    await query.edit_message_text(
        text,
        reply_markup=get_admin_back_keyboard(),
        parse_mode='HTML'
    )


async def admin_list_apps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all apps"""
    query = update.callback_query
    user_id = query.from_user.id
    
    if not db.is_admin(user_id) or not db.is_admin_authenticated(user_id):
        await query.answer("⏱ Sessiya tugadi!", show_alert=True)
        return
    
    await query.answer()
    
    apps = db.get_all_apps()
    
    if not apps:
        await query.edit_message_text(
            "❌ Ilovalar topilmadi.",
            reply_markup=get_admin_back_keyboard()
        )
        return
    
    text = f"📦 <b>Barcha ilovalar ({len(apps)})</b>\n\n"
    for app in apps:
        text += f"🔑 <code>{app['code']}</code> - {app['name']} (📥 {app['downloads']})\n"
    
    await query.edit_message_text(
        text,
        reply_markup=get_admin_back_keyboard(),
        parse_mode='HTML'
    )


async def admin_manage_admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show admin management panel"""
    query = update.callback_query
    user_id = query.from_user.id

    if not db.is_admin(user_id) or not db.is_admin_authenticated(user_id):
        await query.answer("⏱ Sessiya tugadi!", show_alert=True)
        return

    await query.answer()
    admins = db.get_admins()
    text = f"👮 <b>Adminlar ({len(admins)})</b>\n\n"
    for admin_id in admins:
        text += f"• <code>{admin_id}</code>\n"

    keyboard = [
        [InlineKeyboardButton("➕ Admin qo'shish", callback_data="admin_add_admin")],
        [InlineKeyboardButton("➖ Admin olish", callback_data="admin_remove_admin")],
        [InlineKeyboardButton("⬅️ Orqaga", callback_data="admin_menu")]
    ]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )


async def admin_add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start add admin process"""
    query = update.callback_query
    user_id = query.from_user.id

    if not db.is_admin(user_id) or not db.is_admin_authenticated(user_id):
        await query.answer("⏱ Sessiya tugadi!", show_alert=True)
        return

    await query.answer()
    await query.edit_message_text(
        "Yangi adminning Telegram ID raqamini yuboring:",
        reply_markup=get_admin_back_keyboard()
    )
    db.set_user_state(user_id, {"action": "waiting_for_add_admin_id"})


async def admin_remove_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start remove admin process"""
    query = update.callback_query
    user_id = query.from_user.id

    if not db.is_admin(user_id) or not db.is_admin_authenticated(user_id):
        await query.answer("⏱ Sessiya tugadi!", show_alert=True)
        return

    await query.answer()
    await query.edit_message_text(
        "Olib tashlanadigan adminning Telegram ID raqamini yuboring:",
        reply_markup=get_admin_back_keyboard()
    )
    db.set_user_state(user_id, {"action": "waiting_for_remove_admin_id"})


async def admin_manage_channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show required channel management panel"""
    query = update.callback_query
    user_id = query.from_user.id

    if not db.is_admin(user_id) or not db.is_admin_authenticated(user_id):
        await query.answer("⏱ Sessiya tugadi!", show_alert=True)
        return

    await query.answer()
    channels = db.get_required_channels()
    text = f"📢 <b>Majburiy kanallar ({len(channels)})</b>\n\n"
    if channels:
        for channel in channels:
            username = channel.get("username") or "username yo'q"
            text += f"• <code>{channel['id']}</code> - {username}\n"
    else:
        text += "Hozir majburiy kanal yo'q.\n"

    keyboard = [
        [InlineKeyboardButton("➕ Kanal qo'shish", callback_data="admin_add_channel")],
        [InlineKeyboardButton("➖ Kanalni olib tashlash", callback_data="admin_remove_channel")],
        [InlineKeyboardButton("⬅️ Orqaga", callback_data="admin_menu")]
    ]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )


async def admin_add_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start add required channel process"""
    query = update.callback_query
    user_id = query.from_user.id

    if not db.is_admin(user_id) or not db.is_admin_authenticated(user_id):
        await query.answer("⏱ Sessiya tugadi!", show_alert=True)
        return

    await query.answer()
    await query.edit_message_text(
        "Kanal ID va username yuboring.\n\n"
        "Masalan: <code>-1001234567890 @kanal_username</code>\n"
        "Public kanal bo'lsa faqat <code>@kanal_username</code> ham bo'ladi.",
        reply_markup=get_admin_back_keyboard(),
        parse_mode='HTML'
    )
    db.set_user_state(user_id, {"action": "waiting_for_add_channel"})


async def admin_remove_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start remove required channel process"""
    query = update.callback_query
    user_id = query.from_user.id

    if not db.is_admin(user_id) or not db.is_admin_authenticated(user_id):
        await query.answer("⏱ Sessiya tugadi!", show_alert=True)
        return

    await query.answer()
    await query.edit_message_text(
        "Olib tashlanadigan kanal ID yoki username yuboring:",
        reply_markup=get_admin_back_keyboard()
    )
    db.set_user_state(user_id, {"action": "waiting_for_remove_channel"})


async def admin_delete_app(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start delete app process"""
    query = update.callback_query
    user_id = query.from_user.id
    
    if not db.is_admin(user_id) or not db.is_admin_authenticated(user_id):
        await query.answer("⏱ Sessiya tugadi!", show_alert=True)
        return
    
    await query.answer()
    await query.edit_message_text(
        "Ilova kodini kiriting (o'chirish uchun):",
        reply_markup=get_admin_back_keyboard()
    )
    
    db.set_user_state(user_id, {"action": "waiting_for_delete_code"})


async def admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start broadcast message"""
    query = update.callback_query
    user_id = query.from_user.id
    
    if not db.is_admin(user_id) or not db.is_admin_authenticated(user_id):
        await query.answer("⏱ Sessiya tugadi!", show_alert=True)
        return
    
    await query.answer()
    await query.edit_message_text(
        "📢 Xabar yuboring (barcha foydalanuvchilarga):",
        reply_markup=get_admin_back_keyboard()
    )
    
    db.set_user_state(user_id, {"action": "waiting_for_broadcast"})


async def admin_logout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Logout admin"""
    query = update.callback_query
    user_id = query.from_user.id
    
    if not db.is_admin(user_id):
        await query.answer("❌ Xato!", show_alert=True)
        return
    
    db.clear_admin_session(user_id)
    await query.answer("✅ Siz chiqib ketdingiz!", show_alert=True)
    await query.edit_message_text("❌ Sessiya tugadi.")


# ==================== ADMIN FILE HANDLERS ====================
async def handle_admin_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin inputs (image, file, etc.)"""
    message = update.message
    user_id = message.from_user.id
    user_state = db.get_user_state(user_id)
    
    if not user_state:
        return
    
    action = user_state.get("action")

    if action != "waiting_for_search" and (not db.is_admin(user_id) or not db.is_admin_authenticated(user_id)):
        await message.reply_text("⏱ Admin sessiya tugadi. /admin bilan qayta kiring.")
        db.clear_user_state(user_id)
        return

    text_required_actions = {
        "waiting_for_app_name",
        "waiting_for_delete_code",
        "waiting_for_broadcast",
        "waiting_for_add_admin_id",
        "waiting_for_remove_admin_id",
        "waiting_for_add_channel",
        "waiting_for_remove_channel",
    }
    if action in text_required_actions and not message.text:
        await message.reply_text("❌ Iltimos, matn yuboring.")
        return
    
    # Image upload for app
    if action == "waiting_for_app_image":
        if not message.photo:
            await message.reply_text("❌ Rasm yuboring!")
            return
        
        image = message.photo[-1]
        new_state = user_state.copy()
        new_state["image_id"] = image.file_id
        new_state["action"] = "waiting_for_app_name"
        db.set_user_state(user_id, new_state)
        
        await message.reply_text("📝 Ilova nomini kiriting:")
        
    # App name
    elif action == "waiting_for_app_name":
        new_state = user_state.copy()
        new_state["app_name"] = message.text
        new_state["action"] = "waiting_for_app_file"
        db.set_user_state(user_id, new_state)
        
        await message.reply_text("📦 APK/ZIP faylini yuboring:")
        
    # App file
    elif action == "waiting_for_app_file":
        if not message.document:
            await message.reply_text("❌ Fayl yuboring!")
            return
        
        document = message.document
        app_name = user_state.get("app_name")
        image_id = user_state.get("image_id")
        
        # Add app to database
        app_code = db.add_app(app_name, document.file_id, document.file_name, image_id)
        
        # Get the app to send to channel
        app = db.get_app_by_code(app_code)
        
        # Send to channel
        await send_to_channel(context, app)
        
        await message.reply_text(
            f"✅ Ilova qo'shildi!\n\n"
            f"📱 Nom: {app_name}\n"
            f"🔑 Kod: <code>{app_code}</code>\n"
            f"📢 Kanalga post yuborildi!",
            parse_mode='HTML',
            reply_markup=get_admin_menu_keyboard()
        )
        
        db.clear_user_state(user_id)
        
    # Delete code
    elif action == "waiting_for_delete_code":
        code = message.text.strip()
        if db.delete_app(code):
            await message.reply_text(
                f"✅ Ilova <code>{code}</code> o'chirildi!",
                parse_mode='HTML',
                reply_markup=get_admin_menu_keyboard()
            )
        else:
            await message.reply_text(
                f"❌ Ilova <code>{code}</code> topilmadi!",
                parse_mode='HTML'
            )
        db.clear_user_state(user_id)
        
    # Broadcast message
    elif action == "waiting_for_broadcast":
        broadcast_message = message.text
        users = db.get_all_users()
        sent = 0
        
        for user in users:
            try:
                await context.bot.send_message(
                    chat_id=int(user["id"]),
                    text=f"📢 <b>Admin xabari:</b>\n\n{broadcast_message}",
                    parse_mode='HTML'
                )
                sent += 1
            except:
                pass
        
        await message.reply_text(
            f"✅ Xabar {sent} ta foydalanuvchiga yuborildi!",
            reply_markup=get_admin_menu_keyboard()
        )
        db.clear_user_state(user_id)

    # Add admin
    elif action == "waiting_for_add_admin_id":
        admin_id_text = message.text.strip()
        if not admin_id_text.isdigit():
            await message.reply_text("❌ Admin ID faqat raqamlardan iborat bo'lishi kerak.")
            return

        if db.add_admin(int(admin_id_text)):
            await message.reply_text(
                f"✅ <code>{admin_id_text}</code> admin qilib qo'shildi!",
                parse_mode='HTML',
                reply_markup=get_admin_menu_keyboard()
            )
        else:
            await message.reply_text(
                f"ℹ️ <code>{admin_id_text}</code> allaqachon admin.",
                parse_mode='HTML',
                reply_markup=get_admin_menu_keyboard()
            )
        db.clear_user_state(user_id)

    # Remove admin
    elif action == "waiting_for_remove_admin_id":
        admin_id_text = message.text.strip()
        if not admin_id_text.isdigit():
            await message.reply_text("❌ Admin ID faqat raqamlardan iborat bo'lishi kerak.")
            return

        if db.remove_admin(int(admin_id_text)):
            await message.reply_text(
                f"✅ <code>{admin_id_text}</code> adminlardan olindi!",
                parse_mode='HTML',
                reply_markup=get_admin_menu_keyboard()
            )
        else:
            await message.reply_text(
                "❌ Admin topilmadi yoki asosiy adminni olib tashlab bo'lmaydi.",
                reply_markup=get_admin_menu_keyboard()
            )
        db.clear_user_state(user_id)

    # Add required channel
    elif action == "waiting_for_add_channel":
        chat_id, username = parse_channel_input(message.text)
        if not chat_id:
            await message.reply_text("❌ Kanal ID yoki username yuboring.")
            return

        if db.add_required_channel(chat_id, username):
            await message.reply_text(
                "✅ Majburiy kanal qo'shildi!\n\n"
                f"ID: <code>{chat_id}</code>\n"
                f"Username: {username or 'yoq'}",
                parse_mode='HTML',
                reply_markup=get_admin_menu_keyboard()
            )
        else:
            await message.reply_text(
                "ℹ️ Bu kanal allaqachon ro'yxatda bor.",
                reply_markup=get_admin_menu_keyboard()
            )
        db.clear_user_state(user_id)

    # Remove required channel
    elif action == "waiting_for_remove_channel":
        identifier = message.text.strip()
        if db.remove_required_channel(identifier):
            await message.reply_text(
                "✅ Majburiy kanal olib tashlandi!",
                reply_markup=get_admin_menu_keyboard()
            )
        else:
            await message.reply_text(
                "❌ Kanal topilmadi.",
                reply_markup=get_admin_menu_keyboard()
            )
        db.clear_user_state(user_id)


async def check_subscription_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check subscription"""
    query = update.callback_query
    user_id = query.from_user.id
    
    is_subscribed = await check_subscription(user_id, context)
    
    if is_subscribed:
        await query.answer("✅ Obuna bo'lgansiz!", show_alert=True)
        await query.edit_message_text(
            "✅ Obunangiz tasdiqlandi! Botdan foydalanishni davom ettiring.",
            reply_markup=get_main_menu_keyboard()
        )
    else:
        await query.answer("❌ Hali obuna bo'lmagansiz!", show_alert=True)


async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Route text messages by saved user state"""
    user_state = db.get_user_state(update.message.from_user.id)
    if not user_state:
        return

    if user_state.get("action") == "waiting_for_search":
        if not update.message.text:
            await update.message.reply_text("❌ Qidirish uchun matn yuboring.")
            return
        await handle_search_input(update, context)
    else:
        await handle_admin_input(update, context)


async def id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user ID"""
    message = update.message
    await message.reply_text(f"🆔 Sizning ID: <code>{message.from_user.id}</code>", parse_mode='HTML')


async def get_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get app by code (/get_CODE)"""
    message = update.message
    
    # Check subscription
    is_subscribed = await check_subscription(message.from_user.id, context)
    if not is_subscribed:
        await message.reply_text(
            "❌ Kanalga obuna bo'lish kerak!",
            reply_markup=get_subscription_keyboard()
        )
        return
    
    # Extract code from command
    if not context.args:
        await message.reply_text("❌ Kod kiriting: /get_1")
        return
    
    app_code = context.args[0]
    app = db.get_app_by_code(app_code)
    
    if not app:
        await message.reply_text(f"❌ Ilova kod <code>{app_code}</code> topilmadi!", parse_mode='HTML')
        return
    
    await send_document_action(context, message.from_user.id)
    db.increment_download(app_code, message.from_user.id)
    
    try:
        await context.bot.send_document(
            chat_id=message.from_user.id,
            document=app['file_id'],
            caption=f"✅ <b>{app['name']}</b>\n\n📥 Jami yuklanishlar: {db.get_app_by_code(app_code)['downloads']}",
            parse_mode='HTML'
        )
    except Exception as e:
        logger.error(f"Error: {e}")
        await message.reply_text("❌ Xato!")


def build_application():
    """Build and configure the Telegram bot application."""
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("admin", admin_command))
    app.add_handler(CommandHandler("id", id_command))
    app.add_handler(CommandHandler("get", get_command, has_args=True))
    
    # Callbacks
    app.add_handler(CallbackQueryHandler(main_menu, pattern="^main_menu$"))
    app.add_handler(CallbackQueryHandler(list_apps, pattern="^list_apps_\\d+$"))
    app.add_handler(CallbackQueryHandler(top_apps, pattern="^top_apps$"))
    app.add_handler(CallbackQueryHandler(random_app, pattern="^random_app$"))
    app.add_handler(CallbackQueryHandler(search_app, pattern="^search_app$"))
    app.add_handler(CallbackQueryHandler(my_downloads, pattern="^my_downloads$"))
    app.add_handler(CallbackQueryHandler(referral_link, pattern="^referral_link$"))
    app.add_handler(CallbackQueryHandler(help_command, pattern="^help$"))
    app.add_handler(CallbackQueryHandler(download_app, pattern="^download_"))
    app.add_handler(CallbackQueryHandler(check_subscription_button, pattern="^check_subscription$"))
    
    # Admin callbacks
    app.add_handler(CallbackQueryHandler(admin_menu, pattern="^admin_menu$"))
    app.add_handler(CallbackQueryHandler(admin_add_app, pattern="^admin_add_app$"))
    app.add_handler(CallbackQueryHandler(admin_stats, pattern="^admin_stats$"))
    app.add_handler(CallbackQueryHandler(admin_list_apps, pattern="^admin_list_apps$"))
    app.add_handler(CallbackQueryHandler(admin_delete_app, pattern="^admin_delete_app$"))
    app.add_handler(CallbackQueryHandler(admin_manage_admins, pattern="^admin_manage_admins$"))
    app.add_handler(CallbackQueryHandler(admin_add_admin, pattern="^admin_add_admin$"))
    app.add_handler(CallbackQueryHandler(admin_remove_admin, pattern="^admin_remove_admin$"))
    app.add_handler(CallbackQueryHandler(admin_manage_channels, pattern="^admin_manage_channels$"))
    app.add_handler(CallbackQueryHandler(admin_add_channel, pattern="^admin_add_channel$"))
    app.add_handler(CallbackQueryHandler(admin_remove_channel, pattern="^admin_remove_channel$"))
    app.add_handler(CallbackQueryHandler(admin_broadcast, pattern="^admin_broadcast$"))
    app.add_handler(CallbackQueryHandler(admin_logout, pattern="^admin_logout$"))
    
    # Message handlers
    app.add_handler(MessageHandler((filters.TEXT | filters.PHOTO | filters.Document.ALL) & ~filters.COMMAND, handle_text_input))

    return app


def main():
    """Start the bot with polling for local development."""
    app = build_application()
    
    # Start polling
    app.run_polling()


if __name__ == '__main__':
    main()
