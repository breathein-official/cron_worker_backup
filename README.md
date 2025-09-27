# BlockScroll YouTube Auto-Uploader

🎬 **Automated video generation and YouTube uploads with IST scheduling**

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup YouTube API:**
   - Download `client_secret.json` from Google Cloud Console
   - Place it in the project root directory

3. **Authenticate:**
   ```bash
   python youtube_uploader.py
   ```

4. **Start the app:**
   ```bash
   python main_app.py start
   ```

## ⏰ Scheduled Uploads

The app automatically uploads videos at:
- **7:30 AM IST** - Morning Motivation
- **12:00 PM IST** - Midday Reality Check  
- **7:30 PM IST** - Evening Wake-up Call

## 🎯 Key Features

✅ **Automatic Video Generation** - Creates motivational videos using your existing `app.py`  
✅ **YouTube API Integration** - Seamless uploads with proper metadata  
✅ **IST Timezone Handling** - Accurate scheduling regardless of server timezone  
✅ **Auto-Cleanup** - Videos are deleted after successful upload to save disk space  
✅ **Comprehensive Logging** - Detailed CSV logs with all video information  
✅ **Error Handling** - Robust error recovery and logging  
✅ **Statistics Tracking** - Upload success rates and performance metrics  

## 📊 Video Management

- **Generated videos are automatically deleted** after successful YouTube upload
- **All details logged to CSV** including YouTube URLs, file hashes, and metadata
- **No local storage bloat** - only logs and temporary files remain

## 📝 Logging & Monitoring

### CSV Log (`video_upload_log.csv`)
Contains detailed information for each video:
- Timestamp and upload time slot
- Video filename, size, and duration  
- YouTube video ID and URL
- Title and description preview
- Upload status and error messages
- File hash for verification

### Commands
```bash
# View recent uploads
python main_app.py log

# View upload statistics  
python main_app.py stats

# Advanced log viewing
python view_logs.py view 20
python view_logs.py stats
python view_logs.py export
```

## 🛠️ Available Commands

```bash
python main_app.py start        # Start scheduled uploads
python main_app.py test-video   # Test video generation
python main_app.py test-upload  # Test YouTube upload
python main_app.py test-all     # Run all tests
python main_app.py status       # Show current status
python main_app.py log [N]      # View recent upload log
python main_app.py stats        # Show upload statistics
python main_app.py help         # Show help
```

## 📁 File Structure

```
pythonSocialMediaUploader/
├── app.py                    # Video generation logic
├── youtube_uploader.py       # YouTube API integration
├── youtube_scheduler.py      # Scheduling and timezone handling
├── main_app.py              # Main application
├── view_logs.py             # Log viewer utility
├── client_secret.json       # YouTube API credentials
├── requirements.txt         # Python dependencies
├── video_upload_log.csv     # Upload details log
├── bg_images/              # Background images
├── music/                  # Background music
├── icons/                  # App icons
└── outputVideos/           # Temporary video output
```

## 🔧 Configuration

### Custom Upload Times
Edit `youtube_scheduler.py`:
```python
self.upload_times = ['07:30', '12:00', '19:00']  # Customize as needed
```

### Video Settings
- **Resolution**: 1080x1920 (9:16 mobile format)
- **Duration**: 6 seconds
- **Format**: MP4 with H.264 codec
- **Audio**: AAC codec

## 📈 Monitoring

### Health Checks
```bash
python main_app.py status
```

### Log Analysis
```bash
# View recent activity
python main_app.py log 10

# Check success rates
python main_app.py stats

# Export detailed logs
python view_logs.py export
```

## 🚨 Troubleshooting

### Common Issues
1. **YouTube API Authentication Failed**
   - Ensure `client_secret.json` is in project root
   - Delete `token.pickle` and re-authenticate

2. **Video Generation Fails**
   - Check required directories exist (`bg_images/`, `music/`, `icons/`)
   - Verify file permissions

3. **Upload Fails**
   - Check internet connection
   - Verify YouTube API credentials
   - Check video file size limits

### Log Files
- `blockscroll_app.log` - Application logs
- `youtube_scheduler.log` - Scheduler logs  
- `video_upload_log.csv` - Detailed upload records

## 🔒 Security

- Never commit `client_secret.json` to version control
- The `token.pickle` file contains sensitive authentication data
- Use proper file permissions for sensitive files

## 📞 Support

1. Check log files first
2. Verify all requirements are met
3. Test individual components
4. Check YouTube API status and quotas

---

**Made with ❤️ for automated content creation**
