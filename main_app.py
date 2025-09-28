#!/usr/bin/env python3
"""
cronWorker
"""

import os
import sys
import time
import signal
import logging
import csv
from datetime import datetime
import pytz
from scheduler import start_youtube_scheduler, stop_youtube_scheduler, get_scheduler_status, scheduler
from app import generate_video, batch_generate_videos

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cronWorker_app.log'),
        logging.StreamHandler()
    ]
)

class cronWorkerApp:
    def __init__(self):
        self.is_running = False
        self.ist = pytz.timezone('Asia/Kolkata')
        
    def check_requirements(self):
        """Check if all required files and directories exist"""
        required_files = [
            'client_secret.json',
            'exit.py',
            'scheduler.py',
            'app.py'
        ]
        
        required_dirs = [
            'bg_images',
            'music', 
            'icons',
            'outputVideos'
        ]
        
        missing_files = []
        missing_dirs = []
        
        for file in required_files:
            if not os.path.exists(file):
                missing_files.append(file)
        
        for dir_name in required_dirs:
            if not os.path.exists(dir_name):
                missing_dirs.append(dir_name)
        
        if missing_files or missing_dirs:
            logging.error("Missing required files/directories:")
            for file in missing_files:
                logging.error(f"  - {file}")
            for dir_name in missing_dirs:
                logging.error(f"  - {dir_name}")
            return False
        
        return True
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logging.info(f"Received signal {signum}, shutting down gracefully...")
            self.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def start(self):
        """Start the cronWorker application"""
        logging.info("=" * 50)
        logging.info("cronWorker Starting...")
        logging.info("=" * 50)
        
        # Check requirements
        if not self.check_requirements():
            logging.error("Requirements check failed. Please ensure all required files and directories exist.")
            return False
        
        # Setup signal handlers
        self.setup_signal_handlers()
        
        # Show current IST time
        current_time = datetime.now(self.ist)
        logging.info(f"Current IST time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Show next upload times
        next_upload = scheduler.get_next_upload_time()
        logging.info(f"Next upload scheduled: {next_upload.strftime('%Y-%m-%d %H:%M:%S IST')}")
        
        # Start scheduler
        try:
            start_youtube_scheduler()
            self.is_running = True
            logging.info("SUCCESS: cronWorker app started successfully!")
            logging.info("SCHEDULE: Uploads at 7:30 AM, 12:00 PM, 7:00 PM IST")
            logging.info("STATUS: App will run continuously. Press Ctrl+C to stop.")
            return True
        except Exception as e:
            logging.error(f"Failed to start scheduler: {e}")
            return False
    
    def stop(self):
        """Stop the cronWorker application"""
        if not self.is_running:
            return
        
        logging.info("Stopping cronWorker app...")
        stop_youtube_scheduler()
        self.is_running = False
        logging.info("SUCCESS: cronWorker app stopped successfully!")
    
    def run(self):
        """Run the application continuously"""
        if not self.start():
            return
        
        try:
            # Main loop - show status every 10 seconds
            while self.is_running:
                print("App is running... Press Ctrl+C to stop.")
                time.sleep(10)  # Sleep for 10 seconds
                if self.is_running:
                    logging.info(f"Status: {get_scheduler_status()}")
        except KeyboardInterrupt:
            logging.info("Received keyboard interrupt")
        finally:
            self.stop()
    
    def test_video_generation(self):
        """Test video generation without uploading"""
        logging.info("Testing video generation...")
        try:
            generate_video()
            logging.info("SUCCESS: Video generation test successful!")
            return True
        except Exception as e:
            logging.error(f"ERROR: Video generation test failed: {e}")
            return False
    
    def test_youtube_upload(self):
        """Test YouTube upload with existing video"""
        logging.info("Testing YouTube upload...")
        
        # Find latest video
        output_dir = "outputVideos"
        if not os.path.exists(output_dir):
            logging.error("No output videos directory found")
            return False
        
        video_files = [f for f in os.listdir(output_dir) if f.endswith('.mp4')]
        if not video_files:
            logging.error("No video files found for upload test")
            return False
        
        # Get most recent video
        video_files.sort(key=lambda x: os.path.getctime(os.path.join(output_dir, x)), reverse=True)
        latest_video = os.path.join(output_dir, video_files[0])
        
        try:
            from exit import upload_video
            # Generate test title using the same format
            test_title = "Success Habits!\nBe the one ✅"
            
            video_id = upload_video(
                file_path=latest_video,
                title=test_title,
                description="Test upload from cronWorker app",
                tags=["test", "cronWorker", "shorts", "trending", "viral", "business", "creator", "youtuber", "youtubeshorts"]
            )
            logging.info(f"SUCCESS: YouTube upload test successful! Video ID: {video_id}")
            
            # Post test comment
            try:
                from exit import get_youtube_service
                youtube = get_youtube_service()
                comment_request = youtube.commentThreads().insert(
                    part="snippet",
                    body={
                        "snippet": {
                            "videoId": video_id,
                            "topLevelComment": {
                                "snippet": {
                                    "textOriginal": "Check Channel Description 💀"
                                }
                            }
                        }
                    }
                )
                comment_response = comment_request.execute()
                logging.info(f"SUCCESS: Test comment posted with ID: {comment_response['id']}")
            except Exception as e:
                logging.warning(f"WARNING: Failed to post test comment: {e}")
            
            # Delete test video after upload
            try:
                os.remove(latest_video)
                logging.info(f"DELETED: Test video file: {latest_video}")
            except Exception as e:
                logging.error(f"Error deleting test video: {e}")
            
            return True
        except Exception as e:
            logging.error(f"ERROR: YouTube upload test failed: {e}")
            return False
    
    def view_upload_log(self, limit=10):
        """View recent upload log entries from CSV"""
        csv_file = 'exitLog.csv'
        if not os.path.exists(csv_file):
            logging.info("No upload log found. Run some uploads first.")
            return
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                rows = list(reader)
                
            if not rows:
                logging.info("Upload log is empty.")
                return
            
            # Show most recent entries
            recent_rows = rows[-limit:] if len(rows) > limit else rows
            
            logging.info(f"\nLOG: Recent Upload Log (Last {len(recent_rows)} entries):")
            logging.info("=" * 80)
            
            for row in recent_rows:
                status_text = "SUCCESS" if row['upload_status'] == 'success' else "FAILED"
                logging.info(f"{status_text}: {row['timestamp']} | {row['upload_time_slot']} | {row['title'][:50]}...")
                if row['upload_status'] == 'success':
                    logging.info(f"   YOUTUBE: {row['youtube_url']}")
                else:
                    logging.info(f"   ERROR: {row['error_message']}")
                logging.info(f"   FILE: {row['video_filename']} ({row['video_size_mb']} MB, {row['video_duration_sec']}s)")
                logging.info("-" * 80)
                
        except Exception as e:
            logging.error(f"Error reading upload log: {e}")
    
    def get_upload_stats(self):
        """Get upload statistics from CSV log"""
        csv_file = 'exitLog.csv'
        if not os.path.exists(csv_file):
            return {"total": 0, "successful": 0, "failed": 0, "success_rate": 0}
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                rows = list(reader)
            
            total = len(rows)
            successful = len([row for row in rows if row['upload_status'] == 'success'])
            failed = total - successful
            success_rate = (successful / total * 100) if total > 0 else 0
            
            return {
                "total": total,
                "successful": successful,
                "failed": failed,
                "success_rate": round(success_rate, 1)
            }
        except Exception as e:
            logging.error(f"Error reading upload stats: {e}")
            return {"total": 0, "successful": 0, "failed": 0, "success_rate": 0}

def main():
    """Main function with command line options"""
    app = cronWorkerApp()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "start":
            app.run()
        elif command == "test-video":
            app.test_video_generation()
        elif command == "test-upload":
            app.test_youtube_upload()
        elif command == "test-all":
            logging.info("Running all tests...")
            video_ok = app.test_video_generation()
            if video_ok:
                app.test_youtube_upload()
        elif command == "test-scheduler":
            logging.info("Testing scheduler trigger...")
            from scheduler import scheduler
            success = scheduler.test_trigger_now()
            if success:
                logging.info("✅ Scheduler test completed successfully!")
            else:
                logging.error("❌ Scheduler test failed!")
        elif command == "status":
            if app.is_running:
                print(get_scheduler_status())
            else:
                print("App is not running")
        elif command == "log":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            app.view_upload_log(limit)
        elif command == "stats":
            stats = app.get_upload_stats()
            print(f"\nSTATISTICS: Upload Statistics:")
            print(f"Total uploads: {stats['total']}")
            print(f"Successful: {stats['successful']}")
            print(f"Failed: {stats['failed']}")
            print(f"Success rate: {stats['success_rate']}%")
        elif command == "help":
            print("""
cronWorker YouTube Auto-Uploader Commands:

  python main_app.py start        - Start the app with scheduled uploads
  python main_app.py test-video   - Test video generation only
  python main_app.py test-upload  - Test YouTube upload with existing video
  python main_app.py test-all     - Run both video and upload tests
  python main_app.py test-scheduler - Test scheduler trigger manually
  python main_app.py status       - Show current status
  python main_app.py log [N]      - View recent upload log (default: 10 entries)
  python main_app.py stats        - Show upload statistics
  python main_app.py help         - Show this help message

Scheduled uploads: 11:18 AM, 12:00 PM, 7:00 PM IST
Videos are automatically deleted after successful upload.
All upload details are logged to exitLog.csv
            """)
        else:
            print(f"Unknown command: {command}")
            print("Use 'python main_app.py help' for available commands")
    else:
        # Default: start the app
        app.run()

if __name__ == "__main__":
    main()
