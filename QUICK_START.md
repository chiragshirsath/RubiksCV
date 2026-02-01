# ⚡ Quick Start Guide

Get your Rubik's Cube Solver web app running in minutes!

## 🚀 Local Development

### Option 1: Using the start script (Recommended)
```bash
./start.sh
```

### Option 2: Manual setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py

# Open http://localhost:5001 in your browser
# (Note: Port 5001 is used to avoid conflict with macOS AirPlay on port 5000)
```

## 🌐 Using the Web App

1. **Start Camera**
   - Click "Start Camera" button
   - Allow camera access when prompted

2. **Scan Faces**
   - Position your cube so the center sticker is visible
   - Click the face button (U, R, F, D, L, B) to scan that face
   - Repeat for all 6 faces
   - Scanned faces will show a green badge

3. **Solve**
   - Once all 6 faces are scanned, click "Solve Cube"
   - The solution will appear below

4. **Follow Solution**
   - Click "Next Move" to see the next move
   - Click "Apply Move" after performing the move
   - The cube state will update automatically
   - Continue until solved!

## 📦 Deploy to Production

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions on:
- Heroku
- Render
- Railway
- PythonAnywhere

## 🎯 Tips

- **Lighting**: Use good, even lighting for better color detection
- **Positioning**: Center the cube face in the camera view
- **Calibration**: If colors are detected incorrectly, adjust HSV values in `app.py`

## 🐛 Troubleshooting

**Camera not working?**
- Make sure you're using HTTPS in production (required by browsers)
- Check browser permissions
- Try a different browser

**Colors detected incorrectly?**
- Adjust the `classify_hue()` function in `app.py`
- Use better lighting
- Ensure cube is well-lit and centered

**App won't start?**
- Check that all dependencies are installed: `pip install -r requirements.txt`
- Ensure Python 3.8+ is installed
- Check the console for error messages

---

Happy solving! 🧊✨
