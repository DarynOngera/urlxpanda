# Render Quick Start Guide

## 🚀 Deploy in 5 Minutes

### 1. Create Render Account
- Go to [render.com](https://render.com)
- Sign up with GitHub

### 2. Deploy with Blueprint
1. Click **"New +"** → **"Blueprint"**
2. Select your `urlxpanda` repository
3. Click **"Apply"**
4. Wait 5-10 minutes for build

### 3. Access Your App
- URL: `https://urlxpanda.onrender.com`
- API: `https://urlxpanda.onrender.com/api/expand?url=<URL>`

## ✅ That's It!

Your URLXpanda is now live on Render.

## 📝 What Happens During Deployment?

1. Render reads `render.yaml`
2. Installs Python 3.11
3. Runs `build.sh` (installs Rust, builds WASM)
4. Starts Python server on port 10000
5. Assigns public URL

## 🔧 Configuration Files

- **render.yaml** - Deployment configuration
- **web/build.sh** - Build script (installs Rust, builds WASM)
- **web/serve.py** - Python server
- **Dockerfile** - Optional Docker deployment

## 🆓 Free Tier Notes

- **750 hours/month** (enough for one service)
- **Sleeps after 15 min** of inactivity
- **30s wake-up time** on first request
- **No credit card** required

## 💰 Upgrade to Always-On

**Starter Plan: $7/month**
- No sleep
- Instant response
- Better performance

To upgrade:
1. Go to your service
2. Click **Settings** → **Plan**
3. Select **Starter**

## 🌐 Custom Domain

1. Service → **Settings** → **Custom Domain**
2. Add your domain
3. Update DNS:
   ```
   Type: CNAME
   Name: @
   Value: urlxpanda.onrender.com
   ```

## 🐛 Troubleshooting

**Build fails?**
- Check build logs in Render dashboard
- Ensure `build.sh` is executable

**Service won't start?**
- Check service logs
- Verify PORT environment variable

**Slow first request?**
- Normal for free tier (cold start)
- Upgrade to Starter plan for always-on

## 📚 More Info

- [Full Migration Guide](./RAILWAY_TO_RENDER_MIGRATION.md)
- [Deployment Guide](./DEPLOYMENT.md)
- [Render Docs](https://render.com/docs)

## 🆘 Need Help?

1. Check [Render Community](https://community.render.com)
2. Review build/service logs
3. Open GitHub issue

---

**Enjoy your deployment! 🎉**
