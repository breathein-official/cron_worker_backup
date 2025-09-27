# BlockScroll YouTube Auto-Uploader Setup Guide

## Overview
This application automatically generates motivational videos and uploads them to YouTube three times daily at:
- **7:30 AM IST** - Morning Motivation
- **12:00 PM IST** - Midday Reality Check  
- **7:00 PM IST** - Evening Wake-up Call

## Prerequisites

### 1. YouTube API Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the YouTube Data API v3
4. Create credentials (OAuth 2.0 Client ID)
5. Download the `client_secret.json` file
6. Place `client_secret.json` in your project root directory

### 2. Required Files Structure
```
pythonSocialMediaUploader/
├── app.py                    # Video generation logic
├── youtube_uploader.py       # YouTube API integration
├── youtube_scheduler.py      # Scheduling and timezone handling
├── main_app.py              # Main application
├── client_secret.json       # YouTube API credentials
├── requirements.txt         # Python dependencies
├── bg_images/              # Background images for videos
├── music/                  # Background music files
├── icons/                  # App icons and logos
└── outputVideos/           # Generated video output
```

## Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. First-Time YouTube Authentication
Run the uploader once to authenticate:
```bash
python youtube_uploader.py
```
This will open a browser window for YouTube authentication. Complete the OAuth flow.

## Usage

### Start the Application
```bash
python main_app.py start
```

### Test Components
```bash
# Test video generation only
python main_app.py test-video

# Test YouTube upload with existing video
python main_app.py test-upload

# Run all tests
python main_app.py test-all

# Check status
python main_app.py status

# View recent upload log
python main_app.py log

# View upload statistics
python main_app.py stats
```

### Log Management
```bash
# View recent uploads (default: 10 entries)
python main_app.py log

# View more entries
python main_app.py log 25

# View upload statistics
python main_app.py stats

# Use dedicated log viewer for more options
python view_logs.py view 20
python view_logs.py stats
python view_logs.py export
```

### Stop the Application
Press `Ctrl+C` to stop the application gracefully.

## Configuration

### Timezone Settings
The app automatically handles IST (Indian Standard Time) conversion. The scheduler uses `pytz` to ensure accurate timing regardless of server timezone.

### Video Settings
- **Resolution**: 1080x1920 (9:16 aspect ratio for mobile)
- **Duration**: 6 seconds
- **Format**: MP4 with H.264 codec
- **Audio**: AAC codec

### Upload Settings
- **Privacy**: Public videos
- **Category**: People & Blogs (ID: 22)
- **Tags**: Auto-generated motivational tags

## File Management

### Video Management
After successful upload, videos are automatically **deleted** from the local system to save disk space. All video details are logged to `video_upload_log.csv` for tracking.

### Logs
- Application logs: `blockscroll_app.log`
- Scheduler logs: `youtube_scheduler.log`
- Upload details: `video_upload_log.csv` (detailed CSV log with all video information)

### CSV Log Details
The `video_upload_log.csv` file contains comprehensive information about each video:
- Timestamp and upload time slot
- Video filename, size, and duration
- YouTube video ID and URL
- Title and description preview
- Upload status and error messages
- File hash for verification

## Troubleshooting

### Common Issues

1. **YouTube API Authentication Failed**
   - Ensure `client_secret.json` is in the project root
   - Delete `token.pickle` and re-authenticate
   - Check YouTube API quota limits

2. **Video Generation Fails**
   - Ensure all required directories exist (`bg_images/`, `music/`, `icons/`)
   - Check file permissions
   - Verify ffmpeg installation

3. **Scheduler Not Working**
   - Check system timezone settings
   - Verify pytz installation
   - Check log files for errors

4. **Upload Fails**
   - Check internet connection
   - Verify YouTube API credentials
   - Check video file size limits (YouTube has 128GB limit)

### Log Analysis
Check log files for detailed error information:
```bash
tail -f blockscroll_app.log
tail -f youtube_scheduler.log
```

## Advanced Configuration

### Custom Upload Times
Edit `youtube_scheduler.py` and modify the `upload_times` list:
```python
self.upload_times = ['07:30', '12:00', '19:30']  # Customize as needed
```

### Custom Video Titles/Descriptions
Modify the `create_video_title()` and `create_video_description()` methods in `youtube_scheduler.py`.

### Background Images and Music
- Add images to `bg_images/` directory (JPG, PNG, BMP supported)
- Add music files to `music/` directory (MP3 supported)
- The app randomly selects from available files

## Production Deployment

### Running as a Service (Linux)
Create a systemd service file:
```ini
[Unit]
Description=BlockScroll YouTube Uploader
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/your/project
ExecStart=/usr/bin/python3 /path/to/your/project/main_app.py start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Running on Windows
Use Task Scheduler to run the application at startup or create a batch file.

### Cloud Deployment
Consider deploying on:
- AWS EC2 with auto-scaling
- Google Cloud Compute Engine
- Azure Virtual Machines
- DigitalOcean Droplets

## Monitoring

### Health Checks
The application provides status information:
```bash
python main_app.py status
```

### Log Monitoring
Set up log monitoring to track:
- Successful uploads
- Failed uploads
- Video generation errors
- API quota usage

## Security Considerations

1. **API Credentials**: Never commit `client_secret.json` to version control
2. **Token Storage**: The `token.pickle` file contains sensitive authentication data
3. **File Permissions**: Ensure proper file permissions for sensitive files
4. **Network Security**: Use HTTPS for all API communications

## Support

For issues or questions:
1. Check the log files first
2. Verify all requirements are met
3. Test individual components
4. Check YouTube API status and quotas
