# 🎤 Speecher React Frontend

Modern React frontend for Speecher with real microphone recording capabilities.

## ✨ Features

- 🎙️ **Real-time microphone recording** - Works directly in browser
- 🌊 **Waveform visualization** - See your audio as you record
- 🔄 **Live transcription** - Send audio to backend for processing  
- 💾 **Multiple export formats** - TXT, JSON, SRT
- 🎨 **Beautiful UI** - Modern, responsive design
- ⚙️ **Configurable settings** - Choose provider, language, speakers

## 🚀 Quick Start

### Install dependencies
```bash
cd src/react-frontend
npm install
```

### Start development server
```bash
npm start
```

The app will open at http://localhost:3000

### Build for production
```bash
npm run build
```

## 🔧 Configuration

### Backend URL
By default, the app connects to `http://localhost:8000`. To change:

```bash
# .env file
REACT_APP_API_URL=http://your-backend-url:8000
```

## 🎯 How to Use

1. **Allow Microphone Access**
   - Click "Start Recording"
   - Allow microphone when browser asks

2. **Record Audio**
   - Speak into your microphone
   - Watch the timer and waveform
   - Click "Stop Recording" when done

3. **Review Recording**
   - Play back your recording
   - See the waveform visualization
   - Download or clear if needed

4. **Transcribe**
   - Click "Transcribe" button
   - Wait for backend processing
   - View results with speaker diarization

5. **Export Results**
   - Copy to clipboard
   - Download as TXT, JSON, or SRT
   - View speaker segments

## 🛠️ Technology Stack

- **React 18** - UI framework
- **WaveSurfer.js** - Audio waveform visualization
- **MediaRecorder API** - Browser audio recording
- **Axios** - HTTP client
- **Lucide React** - Icons
- **CSS3** - Styling with animations

## 📁 Project Structure

```
src/
├── components/
│   ├── AudioRecorder.js    # Microphone recording logic
│   ├── TranscriptionResults.js # Display results
│   └── Settings.js         # Configuration panel
├── services/
│   └── api.js             # Backend API calls
├── App.js                 # Main application
└── index.js              # React entry point
```

## 🔌 API Endpoints Used

- `POST /transcribe` - Submit audio for transcription
- `GET /history` - Get transcription history
- `GET /transcription/{id}` - Get specific transcription
- `DELETE /transcription/{id}` - Delete transcription
- `GET /stats` - Get usage statistics
- `GET /health` - Check backend health

## 🐛 Troubleshooting

### Microphone not working
- Check browser permissions (Settings → Privacy → Microphone)
- Ensure HTTPS or localhost (required for MediaRecorder)
- Try different browser (Chrome/Edge recommended)

### Backend connection failed
- Ensure backend is running on port 8000
- Check CORS settings in backend
- Verify network connectivity

### Audio format issues
- Modern browsers record in WebM format
- Backend should accept WebM or convert to WAV
- Check supported MIME types

## 🚢 Deployment

### Docker
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
RUN npm install -g serve
CMD ["serve", "-s", "build", "-l", "3000"]
```

### Nginx
```nginx
server {
    listen 80;
    location / {
        root /usr/share/nginx/html;
        try_files $uri /index.html;
    }
    location /api {
        proxy_pass http://backend:8000;
    }
}
```

## 📝 License

MIT