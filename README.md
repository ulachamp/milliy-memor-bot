# MILLIY ME'MOR GROUP — Telegram + Web Admin

## Render Web Service
- Build Command: `pip install -r requirements.txt`
- Start Command: `python bot.py`
- Environment: `BOT_TOKEN`, `ADMIN_ID`, `ADMIN_PASSWORD`, `SESSION_SECRET`, `WEBHOOK_SECRET`
- `SESSION_SECRET`: uzun, tasodifiy maxfiy matn; `WEBHOOK_SECRET`: faqat A-Z a-z 0-9 _ - belgilaridan iborat tasodifiy maxfiy matn.
- Render `PORT` va `RENDER_EXTERNAL_URL` ni avtomatik beradi.
- Telegram `/admin` — faqat `ADMIN_ID`ga.
- Web admin: `https://<render-host>/admin`; Telegram ID va parol bilan kirish.
- Botdagi `/start`, `/myid`, Instagram, Telegram, aloqa, murojaat qoldirish mavjud.
- Foydalanuvchi va murojaat ma'lumotlari hozir SQLite'da. Render Free ephemeral disk sababli bu **doimiy saqlash emas**. Ishlab chiqarish uchun PostgreSQL kabi tashqi bazaga o'tkazish kerak.
- Render Free uxlab qolishi mumkin; xabarlarga javob kechikadi, 24/7 kafolatlanmaydi.
- Oldingi `run_webhook()` botini boshqa joyda bir vaqtda ishlatmang.
- Admin login uchun HTTPS ishlating; token/parollarni GitHub'ga yuklamang.
