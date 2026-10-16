
import os
import hmac
import html

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# ==============================
# MILLIY ME'MOR GROUP BOT
# ==============================

BOT_TOKEN = os.environ["BOT_TOKEN"]
ADMIN_ID = int(os.environ["ADMIN_ID"])
ADMIN_PASSWORD = os.environ["ADMIN_PASSWORD"]

PORT = int(os.environ.get("PORT", "10000"))

WEBHOOK_URL = os.environ.get(
    "RENDER_EXTERNAL_URL",
    "https://milliy-memor-bot.onrender.com"
).rstrip("/")

# IJTIMOIY TARMOQLAR

INSTAGRAM_URL = "https://instagram.com/milliymemorgroup"
TELEGRAM_URL = "https://t.me/milliymemorgoup"
ADMIN_URL = "https://t.me/u777zzzz"

# TELEFON RAQAMLAR

PHONES = [
    ("1-mutaxassis", "+998938181516"),
    ("2-mutaxassis", "+998938177100"),
    ("3-mutaxassis", "+998902404546"),
]

WAIT_PASSWORD = 1

# ASOSIY MENYU

MAIN_MENU = ReplyKeyboardMarkup(
    [
        ["📸 Instagram", "✈️ Telegram"],
        ["📞 Biz bilan bog‘lanish"],
    ],
    resize_keyboard=True,
)

# ADMIN MENYU

ADMIN_MENU = ReplyKeyboardMarkup(
    [
        ["📊 Statistika", "📩 Murojaatlar"],
        ["🚪 Admin paneldan chiqish"],
    ],
    resize_keyboard=True,
)


# ==============================
# START
# ==============================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    context.user_data["is_admin"] = False

    text = (
        "🏛 MILLIY ME’MOR GROUP\n\n"
        "Assalomu alaykum! 👋\n\n"
        "Milliy Me’mor Group rasmiy Telegram "
        "botiga xush kelibsiz!\n\n"
        "🏡 Orzuyingizdagi uy — bizning loyihamiz!\n\n"
        "📐 Arxitektura va loyihalash\n"
        "🏠 Zamonaviy uy loyihalari\n"
        "🏢 Jamoat binolari\n"
        "🏗 Qurilish yechimlari\n\n"
        "📍 Sirdaryo viloyati, Boyovut tumani\n\n"
        "💎 Kelajak uchun sifatli makon!\n\n"
        "👇 Kerakli bo‘limni tanlang:"
    )

    await update.message.reply_text(
        text,
        reply_markup=MAIN_MENU
    )


# ==============================
# TELEGRAM ID
# ==============================

async def myid(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    user_id = update.effective_user.id

    await update.message.reply_text(
        f"🆔 Sizning Telegram ID: {user_id}"
    )


# ==============================
# ADMIN LOGIN
# ==============================

async def admin(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    user_id = update.effective_user.id

    if update.effective_chat.type != "private":
        await update.message.reply_text(
            "🔒 Admin panelga shaxsiy chatdan kiring."
        )
        return ConversationHandler.END

    if user_id != ADMIN_ID:
        await update.message.reply_text(
            "⛔ Sizda admin huquqi yo‘q!\n\n"
            "ID'ingizni /myid orqali tekshiring."
        )
        return ConversationHandler.END

    await update.message.reply_text(
        "🔐 Admin maxfiy kodini kiriting:"
    )

    return WAIT_PASSWORD


# ==============================
# ADMIN PAROL TEKSHIRISH
# ==============================

async def check_password(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    user_id = update.effective_user.id
    password = update.message.text

    correct = (
        user_id == ADMIN_ID
        and hmac.compare_digest(
            password,
            ADMIN_PASSWORD
        )
    )

    # Parol xabarini o‘chirishga urinish
    try:
        await update.message.delete()
    except Exception:
        pass

    if correct:
        context.user_data["is_admin"] = True

        await update.effective_chat.send_message(
            "✅ Xush kelibsiz, Administrator!\n\n"
            "🏛 MILLIY ME’MOR GROUP\n"
            "🔐 Admin panel ochildi.",
            reply_markup=ADMIN_MENU
        )

    else:
        await update.effective_chat.send_message(
            "❌ Maxfiy kod noto‘g‘ri!"
        )

    return ConversationHandler.END


# ==============================
# TUGMALAR
# ==============================

async def buttons(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    message = update.message.text

    is_admin = (
        update.effective_user.id == ADMIN_ID
        and context.user_data.get("is_admin", False)
    )

    # ADMIN TUGMALARI

    if is_admin:

        if message == "📊 Statistika":
            await update.message.reply_text(
                "📊 STATISTIKA\n\n"
                "Bu bo‘lim hozircha demo."
            )
            return

        if message == "📩 Murojaatlar":
            await update.message.reply_text(
                "📩 MUROJAATLAR\n\n"
                "Bu bo‘lim hozircha demo."
            )
            return

        if message == "🚪 Admin paneldan chiqish":
            context.user_data["is_admin"] = False

            await update.message.reply_text(
                "🔒 Admin panel yopildi.",
                reply_markup=MAIN_MENU
            )
            return

    # INSTAGRAM

    if message == "📸 Instagram":
        await update.message.reply_text(
            "📸 Bizning Instagram sahifamiz:\n\n"
            f'<a href="{INSTAGRAM_URL}">'
            "Instagram sahifasiga o‘tish</a>",
            parse_mode="HTML",
            disable_web_page_preview=True
        )

    # TELEGRAM

    elif message == "✈️ Telegram":
        await update.message.reply_text(
            "✈️ Bizning Telegram kanalimiz:\n\n"
            f'<a href="{TELEGRAM_URL}">'
            "Telegram kanaliga o‘tish</a>",
            parse_mode="HTML",
            disable_web_page_preview=True
        )

    # BIZ BILAN BOG‘LANISH

    elif message == "📞 Biz bilan bog‘lanish":

        text = (
            "🏛 <b>MILLIY ME’MOR GROUP</b>\n\n"
            "📞 <b>BIZ BILAN BOG‘LANISH</b>\n\n"
            "👨‍💼 <b>Administrator:</b>\n"
            f'<a href="{ADMIN_URL}">@u777zzzz</a>\n\n'
            "👷 <b>Mutaxassislarimiz:</b>\n"
        )

        for name, phone in PHONES:
            text += (
                f"\n📱 {html.escape(name)}: "
                f"{html.escape(phone)}"
            )

        text += (
            "\n\n📍 Sirdaryo viloyati, "
            "Boyovut tumani\n\n"
            "💎 Kelajak uchun sifatli makon!"
        )

        await update.message.reply_text(
            text,
            parse_mode="HTML",
            disable_web_page_preview=True
        )


# ==============================
# RENDER WEBHOOK
# ==============================

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("myid", myid))

    admin_handler = ConversationHandler(
        entry_points=[CommandHandler("admin", admin)],
        states={
            WAIT_PASSWORD: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    check_password
                )
            ]
        },
        fallbacks=[]
    )

    app.add_handler(admin_handler)

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            buttons
        )
    )

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path="telegram",
        webhook_url=f"{WEBHOOK_URL}/telegram",
        drop_pending_updates=True
    )


if __name__ == "__main__":
    main()
