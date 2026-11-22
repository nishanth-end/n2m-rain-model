# N²M Flood Prediction Model — Cloud Deployment Guide

This document provides step-by-step instructions for deploying the **N²M Flood Prediction Model** to free-tier cloud platforms.

---

## 1. Architecture Overview

```
                                      +------------------------------------+
                                      |         Vercel (Free Tier)         |
                                      |   React 18 + Vite SPA Frontend     |
                                      |   Static Cartographic Interface    |
                                      +-----------------+------------------+
                                                        |
                                          HTTPS REST    | VITE_API_BASE_URL
                                          Requests      v
+-----------------------+             +-----------------+------------------+
| Telegram Cloud Servers|<----------->|         Render (Free Tier)         |
| (Inbound Webhook &    |  HTTPS API  |   Python 3.10 + FastAPI Backend    |
| Outbound Demo Alerts) |             |   XGBoost Model & 24-Day Replay    |
+-----------------------+             +------------------------------------+
```

- **Frontend**: Hosted on [Vercel](https://vercel.com) as a modern React Single Page Application (SPA).
- **Backend**: Hosted on [Render](https://render.com) as a Python Web Service running with `uvicorn`.
- **Machine Learning & Replay Assets**: Bundled within the backend repository (`handover_member3/`, ~1.9 MB total footprint; ~15 MB resident memory, well below Render's 512 MB free-tier limit).
- **Telegram Bot Service**: Runs inside the FastAPI backend (routes `/api/telegram/*`), interacting securely with Telegram's Bot API.

---

## 2. Prerequisites

1. A **GitHub** account containing this repository.
2. A free **Render** account ([render.com](https://render.com)).
3. A free **Vercel** account ([vercel.com](https://vercel.com)).
4. *(Optional for Telegram)*: A bot token from [@BotFather](https://t.me/BotFather) and your personal Telegram user/chat ID.

---

## 3. Backend Deployment (Render)

### Step 3.1: Create Web Service on Render
1. Log in to the [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** → **Web Service**.
3. Connect your GitHub repository (`n2m-rain-predictive-model`).
4. Configure the service settings:
   - **Name**: `n2m-flood-prediction-api` (or a name of your choice)
   - **Region**: Choose the closest region to your users (e.g., *Singapore* or *Frankfurt*)
   - **Branch**: `main`
   - **Root Directory**: *(Leave blank — uses repository root)*
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: `Free`

### Step 3.2: Configure Environment Variables
Under the **Environment Variables** section, add the following keys:

| Key | Recommended Value | Purpose |
| :--- | :--- | :--- |
| `PYTHON_VERSION` | `3.10.12` | Ensures consistent Python build environment |
| `MODE` | `historical_replay` | Designates primary research mode |
| `CORS_ORIGINS` | `*` *(or your Vercel URL)* | Allows decoupled frontend to make API calls |
| `ENABLE_EXPERIMENTAL_LIVE_PIPELINE` | `false` | Keeps experimental live pipeline isolated |
| `TELEGRAM_ENABLED` | `true` *(or `false`)* | Activates Telegram demo bot functionality |
| `TELEGRAM_BOT_TOKEN` | `YOUR_BOT_TOKEN` | Bot API token from @BotFather *(Optional)* |
| `TELEGRAM_CHAT_ID` | `YOUR_CHAT_ID` | Your personal numeric chat ID *(Optional)* |
| `TELEGRAM_AUTHORIZED_CHAT_IDS`| `YOUR_CHAT_ID` | Comma-separated whitelist of allowed evaluators |
| `TELEGRAM_BOT_USERNAME` | `N2M_Flood_Bot` | Display handle of your Telegram bot |

### Step 3.3: Health Check
Render will prompt for a health check path:
- **Health Check Path**: `/health`

Click **Deploy Web Service**. Render will install the dependencies, load the ML holdout model and parquet replay datasets, and expose your service at:
`https://<your-render-app-name>.onrender.com`

Verify the backend deployment in your terminal:
```bash
curl https://<your-render-app-name>.onrender.com/health
```
Expected output:
```json
{"status":"ok","project":"Bengaluru Flood Susceptibility Model (Historical Replay API)","version":"1.0.0"}
```

---

## 4. Frontend Deployment (Vercel)

### Step 4.1: Import Project on Vercel
1. Log in to the [Vercel Dashboard](https://vercel.com/).
2. Click **Add New...** → **Project**.
3. Select your GitHub repository.
4. In the configuration screen:
   - **Framework Preset**: `Vite`
   - **Root Directory**: Click *Edit* and select `frontend` *(Note: if left as root, the included root `vercel.json` will automatically build the `frontend` directory).*
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

### Step 4.2: Configure Frontend Environment Variables
Expand **Environment Variables** and add:

| Key | Value | Notes |
| :--- | :--- | :--- |
| `VITE_API_BASE_URL` | `https://<your-render-app-name>.onrender.com` | **No trailing slash**. Points React to your deployed Render backend. |

Click **Deploy**. Vercel will build the frontend and provide your production URL:
`https://<your-project>.vercel.app`

---

## 5. Telegram Demonstration Bot Integration in Cloud

Once your backend is live on Render:

### Outbound Demo Alerts ("Send Demo Alert" from Web UI)
Outbound messages require **no public webhook**. As long as `TELEGRAM_ENABLED="true"`, `TELEGRAM_BOT_TOKEN`, and `TELEGRAM_CHAT_ID` are configured in Render environment variables, clicking the button in the frontend will immediately dispatch an alert to your chat.

### Inbound Slash Commands (`/start`, `/help`, `/status`, `/demo`)
To allow authorized evaluators to chat directly with the bot on Telegram:
1. Register Render's public webhook with Telegram:
   ```bash
   curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=https://<your-render-app-name>.onrender.com/api/telegram/webhook"
   ```
2. Verify webhook registration:
   ```bash
   curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo"
   ```

---

## 6. Free-Tier Characteristics & Limitations

### 1. Render Inactivity Spin-Down (Cold Starts)
- **Behavior**: Free-tier web services on Render spin down to 0 instances after **15 minutes of inactivity**.
- **Cold Start Latency**: When a sleeping service receives an incoming request (from Vercel or Telegram), it takes **30–50 seconds** to boot.
- **Handling**: 
  - The React frontend displays an offline badge or retry state while the backend boots up.
  - In Telegram, if the bot is cold, a slash command may experience a 30-second delay on the first message before replying instantly on subsequent messages.

### 2. Memory Footprint
- Render Free Tier allocates **512 MB RAM**.
- The N²M backend uses an ultra-lightweight memory strategy:
  - 3,026 static cells: ~268 KB
  - 24-day replay parquet: ~921 KB
  - XGBoost holdout tree structure: ~214 KB
  - Total resident RAM during execution: **~15–20 MB** (less than 4% of total allowance).

### 3. Vercel Bandwidth & Build Time
- The React + Leaflet frontend builds in under **1 second** (`npm run build`).
- Total compressed build assets: **~120 KB gzip**. Well within Vercel's 100 GB monthly bandwidth allowance.

---

## 7. Troubleshooting

| Symptom | Cause | Solution |
| :--- | :--- | :--- |
| `CORS Error: No 'Access-Control-Allow-Origin' header` | Frontend origin is blocked by backend | Ensure `CORS_ORIGINS` in Render contains your Vercel URL (e.g. `https://my-app.vercel.app`) or is set to `*`. |
| Map tiles show gray or don't load | Unstable tile provider | We use OpenStreetMap tiles directly without API keys. Check device network connection. |
| Telegram returns `400: chat not found` | Bot hasn't been started by user | Open the bot in Telegram and tap **"Start"** from your authorized account before sending alerts. |
| Telegram command responds with `Access Restricted` | User's chat ID is not whitelisted | Add your numeric chat ID to `TELEGRAM_AUTHORIZED_CHAT_IDS` in Render environment settings. |
| Frontend shows "API Offline" | Render backend is sleeping | Wait 30 seconds for Render's free instance to wake up, then refresh the page. |
