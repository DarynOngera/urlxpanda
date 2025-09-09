# URLXpanda Deployment Guide

## 🚀 Netlify Deployment (Recommended - Free)

### Prerequisites
- GitHub account
- Netlify account (free at [netlify.com](https://netlify.com))

### Step-by-Step Instructions

1. **Fork the Repository**
   ```bash
   # Go to https://github.com/DarynOngera/urlxpanda
   # Click "Fork" in the top right
   ```

2. **Connect to Netlify**
   - Login to [netlify.com](https://netlify.com)
   - Click "New site from Git"
   - Choose "GitHub" as your Git provider
   - Authorize Netlify to access your GitHub account
   - Select your forked `urlxpanda` repository

3. **Configure Build Settings**
   ```
   Build command: cd web && ./build.sh
   Publish directory: web
   Functions directory: netlify/functions
   ```

4. **Environment Variables** (Optional)
   ```
   CORS_ORIGIN=*
   MAX_REDIRECTS=10
   REQUEST_TIMEOUT=10
   ```

5. **Deploy**
   - Click "Deploy site"
   - Netlify will automatically build and deploy
   - Your site will be available at `https://random-name.netlify.app`

6. **Custom Domain** (Optional)
   - Go to Site settings → Domain management
   - Add your custom domain
   - Configure DNS records as instructed

### Build Process
The Netlify build will:
1. Install Rust and wasm-pack
2. Compile the WASM module
3. Generate JavaScript bindings
4. Deploy static files and serverless functions

### Troubleshooting

**Build Fails:**
- Check build logs in Netlify dashboard
- Ensure `build.sh` has execute permissions
- Verify Rust/wasm-pack installation

**Functions Not Working:**
- Check Functions tab in Netlify dashboard
- Verify `netlify/functions/expand.py` exists
- Check function logs for errors

**WASM Loading Issues:**
- Ensure proper CORS headers in `netlify.toml`
- Check browser console for errors
- Verify WASM files are generated in `pkg/`

## 🔄 Vercel Deployment (Alternative)

### Quick Deploy
1. Fork the repository
2. Go to [vercel.com](https://vercel.com)
3. Click "New Project"
4. Import your GitHub repository
5. Vercel auto-detects `vercel.json` configuration
6. Deploy!

## 🏠 Local Development

### Setup
```bash
git clone https://github.com/DarynOngera/urlxpanda.git
cd urlxpanda
cd web
./build.sh
python3 serve.py
```

### Development Workflow
1. Make changes to Rust code in `crates/`
2. Rebuild WASM: `cd web && ./build.sh`
3. Refresh browser to see changes
4. Test browser extension locally

## 📱 Mobile App Deployment

### Android
```bash
cd mobile
cargo tauri android build --release
# APK generated in src-tauri/gen/android/app/build/outputs/apk/release/
```

### iOS (macOS only)
```bash
cd mobile
cargo tauri ios build --release
# Follow Xcode signing and App Store submission process
```

## 🔧 Advanced Configuration

### Custom Backend
If you want to use a different backend:

1. Update WASM module:
   ```rust
   // In crates/urlxpanda-wasm/src/lib.rs
   let api_url = format!("https://your-api.com/expand?url={}", url);
   ```

2. Rebuild WASM:
   ```bash
   cd web && ./build.sh
   ```

### Performance Optimization
- Enable gzip compression in hosting provider
- Use CDN for static assets
- Optimize WASM bundle size with `wee_alloc`
- Implement service worker for caching

### Security Headers
Ensure your hosting provider sets:
```
Cross-Origin-Embedder-Policy: require-corp
Cross-Origin-Opener-Policy: same-origin
Content-Security-Policy: default-src 'self' 'unsafe-inline' 'unsafe-eval' data: blob:
```

## 📊 Monitoring

### Netlify Analytics
- Enable in Site settings → Analytics
- Monitor page views, performance, and errors

### Error Tracking
- Check browser console for JavaScript errors
- Monitor Netlify function logs
- Set up uptime monitoring (UptimeRobot, etc.)

## 🚀 Production Checklist

- [ ] Custom domain configured
- [ ] HTTPS enabled (automatic with Netlify)
- [ ] Open Graph image uploaded (`og.jpg`)
- [ ] Favicon files generated
- [ ] Analytics configured
- [ ] Error monitoring setup
- [ ] Performance tested
- [ ] Mobile responsiveness verified
- [ ] Browser extension tested
- [ ] Social media sharing tested

## 🆘 Support

If you encounter issues:
1. Check the [troubleshooting section](#troubleshooting)
2. Review build logs in your hosting provider
3. Open an issue on [GitHub](https://github.com/DarynOngera/urlxpanda/issues)
4. Check browser console for client-side errors

---

**Happy deploying! 🎉**
