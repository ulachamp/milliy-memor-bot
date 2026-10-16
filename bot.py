import os
import hmac
import html
import sqlite3
import asyncio
import secrets
from pathlib import Path
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from urllib.parse import quote

import uvicorn
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.environ['BOT_TOKEN']
ADMIN_ID = int(os.environ['ADMIN_ID'])
ADMIN_PASSWORD = os.environ['ADMIN_PASSWORD']
SESSION_SECRET = os.environ['SESSION_SECRET']
BASE_URL = os.environ.get('RENDER_EXTERNAL_URL', 'http://localhost:10000').rstrip('/')
PORT = int(os.environ.get('PORT', '10000'))
DB_PATH = os.environ.get('DB_PATH', 'memor.db')
WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET', '')
if not WEBHOOK_SECRET:
    raise RuntimeError('WEBHOOK_SECRET environment variable is required')

INSTAGRAM = 'https://instagram.com/milliymemorgroup'
CHANNEL = 'https://t.me/milliymemorgoup'
ADMIN_LINK = 'https://t.me/u777zzzz'
PHONES = ['+998938181516', '+998938177100', '+998902404546']
MENU = ReplyKeyboardMarkup([['📸 Instagram', '✈️ Telegram'], ['📞 Biz bilan bog‘lanish', '📝 Murojaat qoldirish']], resize_keyboard=True)
serializer = URLSafeTimedSerializer(SESSION_SECRET, salt='memor-admin')
templates = Jinja2Templates(directory=str(Path(__file__).parent / 'templates'))
telegram_app = ApplicationBuilder().token(TOKEN).concurrent_updates(False).build()


def db():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with db() as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, first_seen TEXT, last_seen TEXT)')
        conn.execute('CREATE TABLE IF NOT EXISTS inquiries (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, name TEXT, message TEXT, status TEXT DEFAULT "Yangi", created TEXT)')


def save_user(update):
    if not update.effective_user:
        return
    user = update.effective_user
    now = datetime.now(timezone.utc).isoformat(timespec='seconds')
    with db() as conn:
        conn.execute('INSERT INTO users (id,name,first_seen,last_seen) VALUES (?,?,?,?) ON CONFLICT(id) DO UPDATE SET name=excluded.name,last_seen=excluded.last_seen', (user.id, user.full_name, now, now))


def counts():
    with db() as conn:
        u = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
        i = conn.execute('SELECT COUNT(*) FROM inquiries').fetchone()[0]
        n = conn.execute('SELECT COUNT(*) FROM inquiries WHERE status="Yangi"').fetchone()[0]
    return {'users': u, 'inquiries': i, 'new': n}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    save_user(update)
    context.user_data.pop('awaiting_inquiry', None)
    await update.message.reply_text('🏛 MILLIY ME’MOR GROUP\n\nAssalomu alaykum! Rasmiy botimizga xush kelibsiz.\n\n📐 Arxitektura va loyihalash\n🏡 Zamonaviy uy loyihalari\n🏗 Qurilish yechimlari\n📍 Sirdaryo viloyati, Boyovut tumani\n\n👇 Bo‘limni tanlang:', reply_markup=MENU)


async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f'🆔 Telegram ID: {update.effective_user.id}')


async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != 'private' or update.effective_user.id != ADMIN_ID:
        await update.message.reply_text('⛔ Sizda admin huquqi yo‘q. /myid orqali ID’ingizni tekshiring.')
        return
    s = counts()
    await update.message.reply_text(
        f'🟢 MILLIY ME’MOR • ADMIN\n\n👥 Foydalanuvchilar: {s["users"]}\n📩 Murojaatlar: {s["inquiries"]}\n🆕 Yangi: {s["new"]}',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton('🌐 Web Dashboard', url=f'{BASE_URL}/admin')],
            [InlineKeyboardButton('📊 Yangilash', callback_data='stats'), InlineKeyboardButton('📩 Murojaatlar', callback_data='inquiries')],
        ])
    )


async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    if q.from_user.id != ADMIN_ID:
        await q.answer('Ruxsat yo‘q', show_alert=True)
        return
    await q.answer()
    if q.data == 'stats':
        s = counts()
        await q.message.reply_text(f'📊 Statistika\n👥 {s["users"]} foydalanuvchi\n📩 {s["inquiries"]} murojaat\n🆕 {s["new"]} yangi')
    elif q.data == 'inquiries':
        with db() as conn:
            rows = conn.execute('SELECT id,name,message,status FROM inquiries ORDER BY id DESC LIMIT 5').fetchall()
        if not rows:
            await q.message.reply_text('📭 Hozircha murojaat yo‘q.')
        else:
            lines = [f'#{r["id"]} — {r["name"]} [{r["status"]}]\n{r["message"][:250]}' for r in rows]
            await q.message.reply_text('\n\n'.join(lines))


async def messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    save_user(update)
    text = update.message.text.strip()
    if context.user_data.get('awaiting_inquiry'):
        context.user_data['awaiting_inquiry'] = False
        if len(text) > 1500:
            await update.message.reply_text('Xabar juda uzun. 1500 belgidan kamroq yozing.')
            return
        with db() as conn:
            cur = conn.execute('INSERT INTO inquiries (user_id,name,message,created) VALUES (?,?,?,?)', (update.effective_user.id, update.effective_user.full_name, text, datetime.now(timezone.utc).isoformat(timespec='seconds')))
            inquiry_id = cur.lastrowid
        await update.message.reply_text(f'✅ Murojaatingiz qabul qilindi! Raqam: #{inquiry_id}', reply_markup=MENU)
        try:
            await context.bot.send_message(ADMIN_ID, f'📩 Yangi murojaat #{inquiry_id}\n👤 {update.effective_user.full_name}\n🆔 {update.effective_user.id}\n\n{text[:1500]}')
        except Exception:
            pass
        return
    if text == '📸 Instagram':
        await update.message.reply_text(f'<a href="{INSTAGRAM}">📸 Instagram sahifamiz</a>', parse_mode='HTML', disable_web_page_preview=True)
    elif text == '✈️ Telegram':
        await update.message.reply_text(f'<a href="{CHANNEL}">✈️ Telegram kanalimiz</a>', parse_mode='HTML', disable_web_page_preview=True)
    elif text == '📞 Biz bilan bog‘lanish':
        numbers = '\n'.join(f'📞 {p}' for p in PHONES)
        await update.message.reply_text(f'🏛 MILLIY ME’MOR GROUP\n\n👨‍💼 Administrator: <a href="{ADMIN_LINK}">@u777zzzz</a>\n\n{html.escape(numbers)}\n\n📍 Boyovut tumani', parse_mode='HTML', disable_web_page_preview=True)
    elif text == '📝 Murojaat qoldirish':
        context.user_data['awaiting_inquiry'] = True
        await update.message.reply_text('📝 Loyihangiz yoki savolingizni bitta xabarda yozing. Bekor qilish uchun /start bosing.')


telegram_app.add_handler(CommandHandler('start', start))
telegram_app.add_handler(CommandHandler('myid', myid))
telegram_app.add_handler(CommandHandler('admin', admin))
telegram_app.add_handler(__import__('telegram.ext', fromlist=['CallbackQueryHandler']).CallbackQueryHandler(admin_callback, pattern='^(stats|inquiries)$'))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, messages))


@asynccontextmanager
async def lifespan(app):
    init_db()
    await telegram_app.initialize()
    await telegram_app.start()
    await telegram_app.bot.set_webhook(f'{BASE_URL}/telegram', secret_token=WEBHOOK_SECRET, drop_pending_updates=False)
    yield
    await telegram_app.bot.delete_webhook()
    await telegram_app.stop()
    await telegram_app.shutdown()


api = FastAPI(lifespan=lifespan)


@api.get('/')
async def home():
    return HTMLResponse('<h2>MILLIY ME’MOR GROUP</h2><p>Telegram bot serveri ishlayapti.</p>')


@api.post('/telegram')
async def webhook(request: Request):
    if not hmac.compare_digest(request.headers.get('X-Telegram-Bot-Api-Secret-Token', ''), WEBHOOK_SECRET):
        raise HTTPException(403)
    data = await request.json()
    await telegram_app.update_queue.put(Update.de_json(data, telegram_app.bot))
    return {'ok': True}


def is_admin(request: Request):
    token = request.cookies.get('memor_admin', '')
    try:
        return serializer.loads(token, max_age=8 * 3600) == str(ADMIN_ID)
    except (BadSignature, SignatureExpired):
        return False


@api.get('/admin', response_class=HTMLResponse)
async def dashboard(request: Request):
    if not is_admin(request):
        return templates.TemplateResponse('login.html', {'request': request, 'error': ''})
    with db() as conn:
        inquiries = [dict(r) for r in conn.execute('SELECT * FROM inquiries ORDER BY id DESC LIMIT 100')]
        users = [dict(r) for r in conn.execute('SELECT * FROM users ORDER BY last_seen DESC LIMIT 100')]
    csrf = secrets.token_urlsafe(24)
    response = templates.TemplateResponse('dashboard.html', {'request': request, 'stats': counts(), 'inquiries': inquiries, 'users': users, 'csrf': csrf})
    response.set_cookie('memor_csrf', csrf, secure=BASE_URL.startswith('https://'), httponly=True, samesite='lax')
    return response


@api.post('/admin/login')
async def login(request: Request, admin_id: str = Form(''), password: str = Form('')):
    if not (hmac.compare_digest(admin_id, str(ADMIN_ID)) and hmac.compare_digest(password, ADMIN_PASSWORD)):
        return templates.TemplateResponse('login.html', {'request': request, 'error': 'ID yoki parol noto‘g‘ri'}, status_code=401)
    response = RedirectResponse('/admin', status_code=303)
    response.set_cookie('memor_admin', serializer.dumps(str(ADMIN_ID)), max_age=8*3600, secure=BASE_URL.startswith('https://'), httponly=True, samesite='lax')
    return response


@api.post('/admin/status/{inquiry_id}')
async def change_status(request: Request, inquiry_id: int, status: str = Form(...), csrf: str = Form(...)):
    if not is_admin(request):
        raise HTTPException(403)
    if not hmac.compare_digest(csrf, request.cookies.get('memor_csrf', '')):
        raise HTTPException(403, 'CSRF check failed')
    if status not in ('Yangi', 'Ko‘rilmoqda', 'Yakunlangan'):
        raise HTTPException(400)
    with db() as conn:
        conn.execute('UPDATE inquiries SET status=? WHERE id=?', (status, inquiry_id))
    return RedirectResponse('/admin', status_code=303)


@api.post('/admin/logout')
async def logout(request: Request, csrf: str = Form(...)):
    if not is_admin(request) or not hmac.compare_digest(csrf, request.cookies.get('memor_csrf', '')):
        raise HTTPException(403)
    response = RedirectResponse('/admin', status_code=303)
    response.delete_cookie('memor_admin')
    response.delete_cookie('memor_csrf')
    return response


if __name__ == '__main__':
    uvicorn.run(api, host='0.0.0.0', port=PORT)
