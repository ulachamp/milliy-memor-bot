
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

# BOT SOZLAMALARI
TOKEN = os.environ["BOT_TOKEN"]
ADMIN_ID = int(os.environ["ADMIN_ID"])
ADMIN_PASSWORD = os.environ["ADMIN_PASSWORD"]

# IJTIMOIY TARMOQLAR
INSTAGRAM = "https://instagram.com/milliymemorgroup"
TELEGRAM = "https://t.me/milliymemorgoup"
ADMIN_LINK = "https://t.me/u777zzzz"

# MUTAXASSISLAR
PHONES = [
    ("1-mutaxassis", "+998938181516"),
    ("2-mutaxassis", "+998938177100"),
    ("3-mutaxassis", "+998902404546"),
]

WAIT_PASSWORD = 1

# ODDIY MENYU
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


# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["is_admin"] = False

    welcome = (
        "🏛 MILLIY ME’MOR GROUP\n\n"
        "Assalomu alaykum! 👋\n\n"
        "Milliy Me’mor Group rasmiy Telegram botiga "
        "xush kelibsiz!\n\n"
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
        welcome,
        reply_markup=MAIN_MENU
    )


# TELEGRAM ID NI BILISH
async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🆔 Sizning Telegram ID: {update.effective_user.id}"
    )


# ADMIN PANELGA KIRISH
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        await update.message.reply_text(
            "🔒 Admin panelga shaxsiy chat orqali kiring."
        )
        return ConversationHandler.END

    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text(
            "⛔ Sizda admin huquqi yo‘q!\n\n"
            "ID'ingizni bilish uchun /myid yozing."
        )
        return ConversationHandler.END

    await update.message.reply_text(
        "🔐 Admin maxfiy kodini kiriting:"
    )
    return WAIT_PASSWORD


# MAXFIY KODNI TEKSHIRISH
async def check_password(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if update.effective_user.id != ADMIN_ID:
        return ConversationHandler.END

    password = update.message.text

    correct = hmac.compare_digest(
        password.encode("utf-8"),
        ADMIN_PASSWORD.encode("utf-8")
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


# TUGMALAR
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text

    is_admin = (
        update.effective_user.id == ADMIN_ID
        and context.user_data.get("is_admin", False)
    )

    if is_admin:
        if message == "📊 Statistika":
            await update.message.reply_text(
                "📊 STATISTIKA\n\n"
                "Bu bo‘lim hozircha demo.\n"
                "Statistika bazasi hali ulanmagan."
            )
            return

        elif message == "📩 Murojaatlar":
            await update.message.reply_text(
                "📩 MUROJAATLAR\n\n"
                "Bu bo‘lim hozircha demo.\n"
                "Murojaatlarni saqlash tizimi hali ulanmagan."
            )
            return

        elif message == "🚪 Admin paneldan chiqish":
            context.user_data["is_admin"] = False

            await update.message.reply_text(
                "🔒 Admin panel yopildi.",
                reply_markup=MAIN_MENU
            )
            return

    if message == "📸 Instagram":
        await update.message.reply_text(
            "📸 Instagram sahifamiz:\n\n"
            f'<a href="{INSTAGRAM}">'
            "Instagram sahifasiga o‘tish</a>",
            parse_mode="HTML",
            disable_web_page_preview=True
        )

    elif message == "✈️ Telegram":
        await update.message.reply_text(
            "✈️ Telegram kanalimiz:\n\n"
            f'<a href="{TELEGRAM}">'
            "Telegram kanaliga o‘tish</a>",
            parse_mode="HTML",
            disable_web_page_preview=True
        )

    elif message == "📞 Biz bilan bog‘lanish":
        text = (
            "🏛 <b>MILLIY ME’MOR GROUP</b>\n\n"
            "📞 <b>BIZ BILAN BOG‘LANISH</b>\n\n"
            "👨‍💼 <b>Administrator:</b>\n"
            f'<a href="{ADMIN_LINK}">@u777zzzz</a>\n\n'
            "👷 <b>Mutaxassislarimiz:</b>\n\n"
        )

        for name, phone in PHONES:
            text += (
                f"📱 {html.escape(name)}: "
                f"{html.escape(phone)}\n"
            )

        text += "\n💎 Kelajak uchun sifatli makon!"

        await update.message.reply_text(
            text,
            parse_mode="HTML",
            disable_web_page_preview=True
        )


# BOTNI ISHGA TUSHIRISH
def main():
    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .concurrent_updates(False)
        .build()
    )

    admin_login = ConversationHandler(
        entry_points=[
            CommandHandler("admin", admin)
        ],
        states={
            WAIT_PASSWORD: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    check_password
                )
            ]
        },
        fallbacks=[
            CommandHandler("start", start)
        ],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("myid", myid))
    app.add_handler(admin_login)

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            buttons
        )
    )

    print("MILLIY ME’MOR GROUP BOT ISHLAYAPTI!")
    app.run_polling()


if __name__ == "__main__":
    main()
