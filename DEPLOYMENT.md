# Sweat Dupe Bot - Deployment Guide

## 🚀 Deploy to Render.com (FREE)

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Add web server for Render deployment"
git push
```

### Step 2: Create Web Service on Render
1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Click **"New +"** → **"Web Service"**
4. Connect your repo
5. Configure:
   - **Name:** `sweatdupe-bot`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python web_server.py`
   - **Plan:** Select **"Free"**

### Step 3: Add Environment Variables
In the "Environment" section:
- `TELEGRAM_BOT_TOKEN` = your bot token
- `WHITELIST` = CincoDeMayo13,canliddatmeh

### Step 4: Deploy
Click **"Create Web Service"**

After deployment, you'll get a URL like:
`https://sweatdupe-bot.onrender.com`

### Step 5: Keep Bot Awake (Important!)

Free tier sleeps after 15 minutes. Keep it awake using **UptimeRobot**:

1. Go to [uptimerobot.com](https://uptimerobot.com)
2. Sign up (free)
3. Click **"Add New Monitor"**
4. Settings:
   - **Monitor Type:** HTTP(s)
   - **Friendly Name:** Sweat Dupe Bot
   - **URL:** `https://sweatdupe-bot.onrender.com/health`
   - **Monitoring Interval:** 5 minutes
5. Click **"Create Monitor"**

✅ Your bot now stays awake 24/7 for free!

## 🧪 Test Deployment

Visit your Render URL in browser:
- `https://sweatdupe-bot.onrender.com` → Should show "🤖 Sweat Dupe Bot is running!"
- `https://sweatdupe-bot.onrender.com/health` → Should show "OK"

Check Render logs to see:
```
🤖 Telegram bot started in background thread
🌐 Starting web server on port 10000
🤖 Sweat Dupe Bot is running...
```

## 📱 Test Telegram Bot

Send to your bot:
```
/start
```

Should work same as local testing!

---

**Cost: $0/month** 🎉
