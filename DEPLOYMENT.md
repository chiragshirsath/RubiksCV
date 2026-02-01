# 🚀 Deployment Guide

This guide will help you deploy the Rubik's Cube Solver web application to various hosting platforms.

## Prerequisites

- Python 3.8 or higher
- Git repository of this project
- Account on your chosen hosting platform

---

## 🌐 Platform-Specific Instructions

### Heroku

1. **Install Heroku CLI**
   ```bash
   # macOS
   brew tap heroku/brew && brew install heroku
   
   # Or download from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Login to Heroku**
   ```bash
   heroku login
   ```

3. **Create a new app**
   ```bash
   heroku create your-app-name
   ```

4. **Deploy**
   ```bash
   git push heroku main
   # or
   git push heroku master
   ```

5. **Open your app**
   ```bash
   heroku open
   ```

**Note**: Heroku requires HTTPS, which is perfect for camera access!

---

### Render

1. **Sign up** at [render.com](https://render.com)

2. **Create a new Web Service**
   - Connect your GitHub repository
   - Select the repository and branch

3. **Configure the service**
   - **Name**: Your app name
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Free tier available

4. **Deploy**
   - Click "Create Web Service"
   - Render will automatically build and deploy

5. **Access your app**
   - Your app will be available at `https://your-app-name.onrender.com`

---

### Railway

1. **Sign up** at [railway.app](https://railway.app)

2. **Create a new project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"

3. **Configure**
   - Railway auto-detects Flask apps
   - It will automatically use `requirements.txt`

4. **Deploy**
   - Railway will build and deploy automatically
   - Your app will be live in minutes!

5. **Custom domain** (optional)
   - Add your own domain in project settings

---

### PythonAnywhere

1. **Sign up** at [pythonanywhere.com](https://www.pythonanywhere.com)

2. **Upload files**
   - Use the Files tab to upload your project files
   - Or use Git: `git clone https://github.com/your-username/your-repo.git`

3. **Create a web app**
   - Go to Web tab
   - Click "Add a new web app"
   - Select Flask and Python 3.10

4. **Configure**
   - Set source code directory to your project folder
   - Set WSGI file to `app.py`
   - Set working directory to your project folder

5. **Install dependencies**
   - Go to Bash console
   - Run: `pip3.10 install --user -r requirements.txt`

6. **Reload**
   - Click the green "Reload" button
   - Your app will be live at `yourusername.pythonanywhere.com`

---

### Local Development

For local testing before deployment:

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the server**
   ```bash
   python app.py
   ```

3. **Access locally**
   - Open `http://localhost:5000` in your browser
   - Note: Camera access works on `localhost` without HTTPS

---

## 🔒 HTTPS Requirements

**Important**: Most browsers require HTTPS for camera access on production sites.

- ✅ Heroku provides HTTPS automatically
- ✅ Render provides HTTPS automatically
- ✅ Railway provides HTTPS automatically
- ✅ PythonAnywhere provides HTTPS automatically

For local development, `localhost` works without HTTPS.

---

## 🐛 Troubleshooting

### Camera not working
- Ensure you're using HTTPS (required for production)
- Check browser permissions for camera access
- Try a different browser (Chrome, Firefox, Edge)

### Build fails
- Check that all dependencies are in `requirements.txt`
- Ensure Python version is 3.8+
- Check build logs for specific errors

### App crashes on startup
- Check server logs
- Ensure `app.py` is in the root directory
- Verify all imports are available

### Color detection inaccurate
- Adjust HSV values in `app.py` (function `classify_hue`)
- Use better lighting conditions
- Ensure cube is well-lit and centered

---

## 📝 Environment Variables

You can set environment variables for configuration:

- `PORT`: Server port (default: 5000)
- `FLASK_ENV`: Set to `production` for production mode

Example (Heroku):
```bash
heroku config:set FLASK_ENV=production
```

---

## 🔄 Updating Your Deployment

After making changes:

1. **Commit changes**
   ```bash
   git add .
   git commit -m "Your changes"
   ```

2. **Push to your hosting platform**
   ```bash
   # Heroku
   git push heroku main
   
   # Render/Railway (if connected to GitHub)
   git push origin main
   # Platform will auto-deploy
   ```

---

## 💡 Tips

- Test locally before deploying
- Use the free tiers to test deployment
- Monitor your app's logs for errors
- Consider using a custom domain for production
- Keep your dependencies updated

---

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review server logs
3. Test locally first
4. Check platform-specific documentation

Happy deploying! 🎉
