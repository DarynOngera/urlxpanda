# Railway to Render Migration Guide

## 🎯 Quick Migration Checklist

- [ ] Create Render account
- [ ] Connect GitHub repository to Render
- [ ] Deploy using Blueprint (render.yaml)
- [ ] Verify deployment is working
- [ ] Update DNS records (if using custom domain)
- [ ] Test all functionality
- [ ] Delete Railway service

## 📋 Detailed Migration Steps

### Step 1: Prepare Your Render Account

1. Go to [render.com](https://render.com)
2. Sign up or log in (can use GitHub OAuth)
3. Connect your GitHub account if not already connected

### Step 2: Deploy to Render

#### Option A: Using Blueprint (Recommended)

1. In Render dashboard, click **"New +"** → **"Blueprint"**
2. Select your repository: `urlxpanda`
3. Render will detect `render.yaml` automatically
4. Review the configuration:
   - Service name: `urlxpanda`
   - Build command: `cd web && ./build.sh`
   - Start command: `cd web && python3 serve.py`
   - Environment variables (auto-configured)
5. Click **"Apply"** to create the service
6. Wait for the build to complete (5-10 minutes)

#### Option B: Manual Web Service Creation

1. Click **"New +"** → **"Web Service"**
2. Connect your repository
3. Configure manually:
   - **Name**: `urlxpanda`
   - **Runtime**: `Python 3`
   - **Build Command**: `cd web && ./build.sh`
   - **Start Command**: `cd web && python3 serve.py`
   - **Plan**: Free (or your preferred plan)
4. Add environment variables:
   ```
   PORT=10000
   CORS_ORIGIN=*
   MAX_REDIRECTS=10
   REQUEST_TIMEOUT=10
   PYTHON_VERSION=3.11
   ```
5. Click **"Create Web Service"**

### Step 3: Verify Deployment

1. Wait for the build to complete
2. Click on the service URL (e.g., `https://urlxpanda.onrender.com`)
3. Test the web interface
4. Test the API endpoint:
   ```bash
   curl "https://urlxpanda.onrender.com/api/expand?url=https://bit.ly/example"
   ```

### Step 4: Update DNS (If Using Custom Domain)

#### On Render:
1. Go to your service → **Settings** → **Custom Domain**
2. Click **"Add Custom Domain"**
3. Enter your domain (e.g., `urlxpanda.com`)
4. Render will provide DNS records

#### Update Your DNS Provider:
1. Add CNAME record pointing to Render
   ```
   Type: CNAME
   Name: @ (or www)
   Value: urlxpanda.onrender.com
   ```
2. Wait for DNS propagation (can take up to 48 hours, usually faster)

### Step 5: Update Application Configuration

If you have any hardcoded Railway URLs in your code:

1. Search for Railway URLs:
   ```bash
   grep -r "railway.app" .
   ```

2. Replace with Render URLs:
   - Old: `https://urlxpanda.up.railway.app`
   - New: `https://urlxpanda.onrender.com`

3. Commit and push changes (Render will auto-deploy)

### Step 6: Test Everything

- [ ] Web interface loads correctly
- [ ] URL expansion works
- [ ] API endpoint responds
- [ ] CORS is working (test from browser extension)
- [ ] Custom domain resolves (if applicable)
- [ ] SSL certificate is active

### Step 7: Clean Up Railway

1. Go to Railway dashboard
2. Select your `urlxpanda` project
3. Go to **Settings** → **Danger Zone**
4. Click **"Delete Project"**
5. Confirm deletion

## 🔄 Key Differences: Railway vs Render

| Feature | Railway | Render |
|---------|---------|--------|
| **Free Tier** | $5 credit/month | 750 hours/month |
| **Sleep Policy** | No sleep | Sleeps after 15 min inactivity |
| **Build Time** | Fast | Similar |
| **Custom Domains** | Yes | Yes |
| **Auto-Deploy** | Yes | Yes |
| **Configuration** | railway.json, nixpacks.toml | render.yaml |
| **Pricing** | Usage-based | Fixed plans |

## ⚠️ Important Notes

### Free Tier Limitations

**Render Free Tier:**
- Services spin down after 15 minutes of inactivity
- First request after sleep takes 30+ seconds
- 750 hours/month (enough for one always-on service)
- No credit card required

**Railway Free Tier:**
- $5 credit/month
- No sleep policy
- Credit card required after trial

### Performance Considerations

1. **Cold Starts**: Render free tier has cold starts. Consider:
   - Upgrading to paid tier ($7/month) for always-on
   - Using a cron job to ping your service every 14 minutes
   - Accepting the cold start delay

2. **Build Time**: First build may take 5-10 minutes due to:
   - Rust toolchain installation
   - WASM compilation
   - Subsequent builds are faster (cached dependencies)

### Environment Variables

Your `render.yaml` already includes all necessary environment variables:
- `PORT=10000` (Render uses this)
- `CORS_ORIGIN=*` (allows all origins)
- `MAX_REDIRECTS=10`
- `REQUEST_TIMEOUT=10`
- `PYTHON_VERSION=3.11`

## 🐛 Troubleshooting

### Build Fails

**Error: "Permission denied: build.sh"**
```bash
# Fix locally and commit
chmod +x web/build.sh
git add web/build.sh
git commit -m "Make build.sh executable"
git push
```

**Error: "wasm-pack not found"**
- Check build logs - `build.sh` should install wasm-pack
- Verify Rust installation in logs

### Service Won't Start

**Error: "Port already in use"**
- Render automatically sets PORT environment variable
- Ensure `serve.py` uses `os.environ.get("PORT", 8000)`

**Error: "Module not found"**
- Check if `requirements.txt` exists and has dependencies
- Your project uses only Python stdlib, so this shouldn't occur

### Slow Response Times

**First request is very slow:**
- This is normal for free tier (cold start)
- Service spins down after 15 minutes of inactivity
- Consider upgrading to paid tier or using a keep-alive service

### CORS Errors

**Browser console shows CORS errors:**
- Verify `CORS_ORIGIN=*` in environment variables
- Check `serve.py` CORS headers are being sent
- Test with curl to isolate client vs server issue

## 📊 Cost Comparison

### Railway
- Free: $5/month credit
- Hobby: $5/month + usage
- Pro: $20/month + usage

### Render
- Free: $0/month (with limitations)
- Starter: $7/month (always-on)
- Standard: $25/month (more resources)

**Recommendation**: Start with Render free tier, upgrade to Starter ($7/month) if you need always-on service.

## 🚀 Next Steps

After successful migration:

1. **Monitor Performance**
   - Check Render dashboard for metrics
   - Monitor response times
   - Watch for errors in logs

2. **Set Up Alerts** (Paid plans)
   - Configure email alerts for downtime
   - Set up health check monitoring

3. **Optimize Build**
   - Consider caching Rust toolchain
   - Optimize WASM build size

4. **Documentation**
   - Update README with new deployment URL
   - Update API documentation

## 📚 Resources

- [Render Documentation](https://render.com/docs)
- [Render Blueprint Spec](https://render.com/docs/blueprint-spec)
- [Render Python Guide](https://render.com/docs/deploy-python)
- [URLXpanda Deployment Guide](./DEPLOYMENT.md)

## 🆘 Need Help?

If you encounter issues:
1. Check Render build logs
2. Review this migration guide
3. Check [Render Community](https://community.render.com)
4. Open an issue on GitHub

---

**Happy migrating! 🎉**
