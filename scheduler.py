import os
import time
import schedule
import threading
from datetime import datetime, timedelta
import pytz
import csv
import hashlib
from exit import upload_video
from app import generate_video
import logging
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('event.log'),
        logging.StreamHandler()
    ]
)

class YouTubeScheduler:
    def __init__(self):
        self.ist = pytz.timezone('Asia/Kolkata')
        self.upload_times = ['07:30', '12:29', '19:00']  # 7:30 AM, 12 PM, 7:00 PM IST
        self.is_running = False
        self.scheduler_thread = None
        self.csv_log_file = 'exitLog.csv'
        self.upload_lock = threading.Lock()  # Prevent concurrent uploads
        self.upload_tracker_file = 'upload_tracker.json'  # Track completed uploads
        self._initialize_upload_tracker()
        self._initialize_csv_log()
    
    def _initialize_upload_tracker(self):
        """Initialize upload tracker to prevent duplicate uploads"""
        if not os.path.exists(self.upload_tracker_file):
            tracker_data = {
                "completed_uploads": {},
                "last_cleanup": None
            }
            with open(self.upload_tracker_file, 'w') as f:
                json.dump(tracker_data, f, indent=2)
            logging.info(f"Initialized upload tracker: {self.upload_tracker_file}")
    
    def _load_upload_tracker(self):
        """Load upload tracker data"""
        try:
            with open(self.upload_tracker_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading upload tracker: {e}")
            return {"completed_uploads": {}, "last_cleanup": None}
    
    def _save_upload_tracker(self, tracker_data):
        """Save upload tracker data"""
        try:
            with open(self.upload_tracker_file, 'w') as f:
                json.dump(tracker_data, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving upload tracker: {e}")
    
    def _is_upload_completed_today(self, upload_time):
        """Check if upload for this time slot was already completed today"""
        tracker_data = self._load_upload_tracker()
        today = self.get_current_ist_time().date().isoformat()
        
        # Clean up old entries (older than 7 days)
        self._cleanup_old_entries(tracker_data)
        
        upload_key = f"{today}_{upload_time}"
        return upload_key in tracker_data.get("completed_uploads", {})
    
    def _mark_upload_completed(self, upload_time):
        """Mark upload as completed for today"""
        tracker_data = self._load_upload_tracker()
        today = self.get_current_ist_time().date().isoformat()
        upload_key = f"{today}_{upload_time}"
        
        tracker_data["completed_uploads"][upload_key] = {
            "timestamp": self.get_current_ist_time().isoformat(),
            "upload_time": upload_time
        }
        
        self._save_upload_tracker(tracker_data)
        logging.info(f"Marked upload as completed: {upload_key}")
    
    def _cleanup_old_entries(self, tracker_data):
        """Clean up upload tracker entries older than 7 days"""
        today = self.get_current_ist_time().date()
        cutoff_date = today - timedelta(days=7)
        
        # Clean up old entries
        old_keys = []
        for key, data in tracker_data.get("completed_uploads", {}).items():
            try:
                entry_date = datetime.fromisoformat(data["timestamp"]).date()
                if entry_date < cutoff_date:
                    old_keys.append(key)
            except:
                old_keys.append(key)  # Remove malformed entries
        
        for key in old_keys:
            del tracker_data["completed_uploads"][key]
        
        if old_keys:
            logging.info(f"Cleaned up {len(old_keys)} old upload tracker entries")
        
    def _initialize_csv_log(self):
        """Initialize CSV log file with headers if it doesn't exist"""
        if not os.path.exists(self.csv_log_file):
            with open(self.csv_log_file, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'timestamp', 'upload_time_slot', 'video_filename', 'video_size_mb', 
                    'video_duration_sec', 'youtube_video_id', 'youtube_url', 'title', 
                    'description_preview', 'upload_status', 'error_message', 'file_hash'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
            logging.info(f"Initialized CSV log file: {self.csv_log_file}")
    
    def _calculate_file_hash(self, file_path):
        """Calculate MD5 hash of video file"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logging.error(f"Error calculating file hash: {e}")
            return "unknown"
    
    def _get_video_duration(self, file_path):
        """Get video duration in seconds"""
        try:
            from moviepy import VideoFileClip
            with VideoFileClip(file_path) as clip:
                return round(clip.duration, 2)
        except Exception as e:
            logging.error(f"Error getting video duration: {e}")
            return 0
    
    def _post_comment(self, video_id):
        """Post a comment on the uploaded video"""
        try:
            from exit import get_youtube_service
            
            youtube = get_youtube_service()
            
            # Post comment
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
            comment_id = comment_response['id']
            
            logging.info(f"SUCCESS: Posted comment on video {video_id}")
            return comment_id
            
        except Exception as e:
            logging.error(f"ERROR: Failed to post comment on video {video_id}: {e}")
            return None
    
    def _log_video_details(self, video_data):
        """Log video details to CSV file"""
        try:
            with open(self.csv_log_file, 'a', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'timestamp', 'upload_time_slot', 'video_filename', 'video_size_mb', 
                    'video_duration_sec', 'youtube_video_id', 'youtube_url', 'title', 
                    'description_preview', 'upload_status', 'error_message', 'file_hash'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writerow(video_data)
            logging.info(f"Logged video details to CSV: {video_data['video_filename']}")
        except Exception as e:
            logging.error(f"Error logging to CSV: {e}")
    
    def get_current_ist_time(self):
        """Get current time in IST"""
        return datetime.now(self.ist)
    
    def create_video_title(self, upload_time):
        """Generate dynamic video title using OpenAI"""
        import os
        import random
        import openai
        from dotenv import load_dotenv
        from token_tracker import track_usage
        
        # Load environment variables
        load_dotenv()
        
        # Initialize OpenAI client
        openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Generate motivational phrases for the title
        prompt = (
            "Generate two short motivational phrases for a YouTube Shorts title. "
            "Format: First line should be about success habits or achievement, "
            "second line should be 'Be the one [action]' or 'Achieve [goal]'. "
            "Keep each line under 20 characters. "
            "Examples: 'Success Habits!' and 'Be the one ✅' or 'Achieve ✅'. "
            "Output only the two lines separated by a newline, nothing else."
        )
        
        # Fallback titles if AI fails
        fallback_titles = [
            ("Success Habits!", "Be the one ✅"),
            ("Achieve More!", "Be the one ✅"),
            ("Win Today!", "Achieve ✅"),
            ("Success Mindset!", "Be the one ✅"),
            ("Level Up!", "Achieve ✅")
        ]
        
        try:
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.7
            )
            
            # Track token usage
            track_usage(response.usage, "Title Generation", "gpt-3.5-turbo")
            
            response_text = response.choices[0].message.content.strip()
            
            # Parse the response
            if "\n" in response_text:
                lines = response_text.split("\n")
                if len(lines) >= 2:
                    line1 = lines[0].strip()
                    line2 = lines[1].strip()
                    
                    # Clean up the lines
                    line1 = line1.replace('"', '').replace("'", "")
                    line2 = line2.replace('"', '').replace("'", "")
                    
                    if len(line1) > 0 and len(line2) > 0:
                        return f"{line1}\n{line2}"
            
            # If parsing failed, use fallback
            import random
            fallback = random.choice(fallback_titles)
            return f"{fallback[0]}\n{fallback[1]}"
            
        except Exception as e:
            logging.warning(f"OpenAI title generation failed: {e}, using fallback")
            import random
            fallback = random.choice(fallback_titles)
            return f"{fallback[0]}\n{fallback[1]}"
    
    def create_video_description(self, upload_time):
        """Generate dynamic video description"""
        base_hashtags = "#Breathe-In #Productivity #DigitalDetox #Motivation #SelfImprovement #Focus #Success #Mindfulness #BreakTheScroll #shorts #trending #viral #business #creator #youtuber #youtubeshorts"
        
        descriptions = {
            '07:00': f"""Start your day right! This morning motivation will help you focus on building success habits, not scrolling mindlessly!

{base_hashtags} #MorningMotivation""",
            
            '12:00': f"""Midday reality check! While you're scrolling, others are building their dreams. Time to refocus and make every moment count.

{base_hashtags} #MiddayMotivation""",
            
            '19:30': f"""Evening wake-up call! Don't let another day slip away in endless scrolling. Your future self will thank you for the time you invest wisely.

{base_hashtags} #EveningMotivation"""
        }
        
        return descriptions.get(upload_time, f"""Focus on building success habits, not scrolling mindlessly! 

{base_hashtags}""")
    
    def generate_and_upload_video(self, upload_time):
        """Generate a video and upload it to YouTube with duplicate prevention"""
        
        # Check if upload already completed today for this time slot
        if self._is_upload_completed_today(upload_time):
            logging.info(f"SKIP: Upload for {upload_time} already completed today")
            return
        
        # Acquire lock to prevent concurrent uploads
        if not self.upload_lock.acquire(blocking=False):
            logging.warning(f"LOCKED: Another upload is in progress, skipping {upload_time}")
            return
        
        try:
            logging.info(f"STARTING: Video generation and upload for {upload_time}")
            self._perform_upload(upload_time)
        finally:
            # Always release the lock
            self.upload_lock.release()
            logging.info(f"RELEASED: Upload lock for {upload_time}")
    
    def _perform_upload(self, upload_time):
        """Perform the actual upload (called within lock)"""
        logging.info(f"VIDEO DEBUG: ===== VIDEO GENERATION STARTED =====")
        logging.info(f"VIDEO DEBUG: Upload time slot: {upload_time}")
        logging.info(f"VIDEO DEBUG: Current IST time: {self.get_current_ist_time().strftime('%Y-%m-%d %H:%M:%S')}")
        
        video_data = {
            'timestamp': self.get_current_ist_time().strftime('%Y-%m-%d %H:%M:%S IST'),
            'upload_time_slot': upload_time,
            'video_filename': '',
            'video_size_mb': 0,
            'video_duration_sec': 0,
            'youtube_video_id': '',
            'youtube_url': '',
            'title': '',
            'description_preview': '',
            'upload_status': 'failed',
            'error_message': '',
            'file_hash': ''
        }
        
        try:
            logging.info(f"VIDEO DEBUG: Starting video generation and upload for {upload_time} IST")
            
            # Generate video
            logging.info("VIDEO DEBUG: Calling generate_video() function...")
            try:
                generate_video()
                logging.info("VIDEO DEBUG: Video generation completed successfully!")
            except Exception as e:
                logging.error(f"VIDEO DEBUG: Video generation failed: {e}")
                raise
            
            # Find the most recent video file
            output_dir = "outputVideos"
            if not os.path.exists(output_dir):
                error_msg = "Output videos directory not found!"
                logging.error(error_msg)
                video_data['error_message'] = error_msg
                self._log_video_details(video_data)
                return
            
            video_files = [f for f in os.listdir(output_dir) if f.endswith('.mp4')]
            if not video_files:
                error_msg = "No video files found to upload!"
                logging.error(error_msg)
                video_data['error_message'] = error_msg
                self._log_video_details(video_data)
                return
            
            # Get the most recently created video
            video_files.sort(key=lambda x: os.path.getctime(os.path.join(output_dir, x)), reverse=True)
            latest_video = os.path.join(output_dir, video_files[0])
            video_filename = video_files[0]
            
            logging.info(f"Found video to upload: {latest_video}")
            
            # Collect video metadata
            video_data['video_filename'] = video_filename
            video_data['video_size_mb'] = round(os.path.getsize(latest_video) / (1024 * 1024), 2)
            video_data['video_duration_sec'] = self._get_video_duration(latest_video)
            video_data['file_hash'] = self._calculate_file_hash(latest_video)
            
            # Create title and description
            title = self.create_video_title(upload_time)
            description = self.create_video_description(upload_time)
            
            video_data['title'] = title
            video_data['description_preview'] = description[:100] + "..." if len(description) > 100 else description
            
            # Upload to YouTube
            logging.info("Uploading to YouTube...")
            video_id = upload_video(
                file_path=latest_video,
                title=title,
                description=description,
                tags=["Breathe-In", "Motivation", "Productivity", "Digital Detox", "Self Improvement", "Focus", "Success", "Mindfulness", "Break The Scroll", "shorts", "trending", "viral", "business", "creator", "youtuber", "youtubeshorts"]
            )
            
            # Update video data with successful upload info
            video_data['youtube_video_id'] = video_id
            video_data['youtube_url'] = f"https://www.youtube.com/watch?v={video_id}"
            video_data['upload_status'] = 'success'
            video_data['error_message'] = ''
            
            logging.info(f"SUCCESS: Successfully uploaded video with ID: {video_id}")
            logging.info(f"YOUTUBE: {video_data['youtube_url']}")
            
            # Post comment on the video
            logging.info("Posting comment on uploaded video...")
            comment_id = self._post_comment(video_id)
            if comment_id:
                logging.info(f"SUCCESS: Comment posted with ID: {comment_id}")
            else:
                logging.warning("WARNING: Failed to post comment, but upload was successful")
            
            # Mark upload as completed to prevent duplicates
            self._mark_upload_completed(upload_time)
            
            # Delete the video file after successful upload
            try:
                os.remove(latest_video)
                logging.info(f"DELETED: Local video file: {latest_video}")
            except Exception as e:
                logging.error(f"Error deleting video file: {e}")
                video_data['error_message'] = f"Upload successful but failed to delete file: {str(e)}"
            
        except Exception as e:
            error_msg = str(e)
            logging.error(f"Error during video generation/upload: {error_msg}")
            video_data['error_message'] = error_msg
            video_data['upload_status'] = 'failed'
            import traceback
            traceback.print_exc()
        
        finally:
            # Always log the video details to CSV
            self._log_video_details(video_data)
    
    def schedule_uploads(self):
        """Schedule video uploads at specified times"""
        logging.info("SCHEDULER DEBUG: Setting up scheduled uploads...")
        logging.info(f"SCHEDULER DEBUG: Upload times configured: {self.upload_times}")
        
        # Clear any existing jobs
        schedule.clear()
        
        for upload_time in self.upload_times:
            # Schedule with explicit timezone handling
            schedule.every().day.at(upload_time).do(
                self.generate_and_upload_video, 
                upload_time=upload_time
            )
            logging.info(f"SCHEDULER DEBUG: Scheduled upload at {upload_time} IST daily")
        
        # Log all scheduled jobs
        logging.info(f"SCHEDULER DEBUG: Total scheduled jobs: {len(schedule.jobs)}")
        for i, job in enumerate(schedule.jobs):
            logging.info(f"SCHEDULER DEBUG: Job {i+1}: {job}")
            
        # Note: Removed immediate check system to prevent duplicate uploads
        # Only using regular daily schedule jobs now
    
    def run_scheduler(self):
        """Run the scheduler in a separate thread"""
        self.is_running = True
        logging.info("SCHEDULER DEBUG: YouTube Scheduler started")
        logging.info(f"SCHEDULER DEBUG: Current IST time: {self.get_current_ist_time().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Log next upload times
        next_upload = self.get_next_upload_time()
        logging.info(f"SCHEDULER DEBUG: Next upload scheduled for: {next_upload.strftime('%Y-%m-%d %H:%M:%S IST')}")
        
        # Check if we missed any scheduled times today
        self._check_missed_schedules()
        
        check_count = 0
        while self.is_running:
            check_count += 1
            current_time = self.get_current_ist_time()
            
            # Log every 4th check (every minute) to avoid spam
            if check_count % 4 == 0:
                logging.info(f"SCHEDULER DEBUG: Check #{check_count} - Current time: {current_time.strftime('%H:%M:%S IST')}")
                logging.info(f"SCHEDULER DEBUG: Pending jobs: {len(schedule.jobs)}")
                
                # Check if any jobs should run now
                for i, job in enumerate(schedule.jobs):
                    if job.should_run:
                        logging.info(f"SCHEDULER DEBUG: Job {i+1} should run NOW! {job}")
                    else:
                        next_run = job.next_run
                        if next_run:
                            logging.info(f"SCHEDULER DEBUG: Job {i+1} next run: {next_run.strftime('%H:%M:%S IST')}")
            
            # Run pending jobs
            try:
                schedule.run_pending()
            except Exception as e:
                logging.error(f"SCHEDULER DEBUG: Error running pending jobs: {e}")
            
            time.sleep(5)  # Check every 5 seconds for more responsive scheduling
        
        logging.info("SCHEDULER DEBUG: YouTube Scheduler stopped")
    
    def _check_missed_schedules(self):
        """Check if we missed any scheduled uploads today and run them"""
        current_time = self.get_current_ist_time()
        current_time_str = current_time.strftime('%H:%M')
        
        logging.info(f"SCHEDULER DEBUG: Checking for missed schedules at {current_time_str}")
        
        # Check each upload time to see if we missed it
        for upload_time in self.upload_times:
            # Parse upload time
            upload_hour, upload_minute = map(int, upload_time.split(':'))
            current_hour = current_time.hour
            current_minute = current_time.minute
            
            # Check if current time is past the upload time (within 30 minutes)
            current_minutes = current_hour * 60 + current_minute
            upload_minutes = upload_hour * 60 + upload_minute
            
            # If we're past the upload time but within 30 minutes, run it
            if upload_minutes < current_minutes <= upload_minutes + 30:
                logging.info(f"SCHEDULER DEBUG: Missed schedule detected for {upload_time}!")
                logging.info(f"SCHEDULER DEBUG: Running missed upload for {upload_time}")
                
                try:
                    # Run the missed upload
                    self.generate_and_upload_video(upload_time)
                    logging.info(f"SCHEDULER DEBUG: Successfully completed missed upload for {upload_time}")
                except Exception as e:
                    logging.error(f"SCHEDULER DEBUG: Failed to run missed upload for {upload_time}: {e}")
            elif upload_minutes < current_minutes:
                logging.info(f"SCHEDULER DEBUG: Upload time {upload_time} already passed (more than 30 min ago)")
            else:
                logging.info(f"SCHEDULER DEBUG: Upload time {upload_time} is in the future")
    
    # Removed _check_immediate_schedules method to prevent duplicate uploads
    
    def start(self):
        """Start the scheduler"""
        if self.is_running:
            logging.warning("Scheduler is already running!")
            return
        
        self.schedule_uploads()
        self.scheduler_thread = threading.Thread(target=self.run_scheduler, daemon=True)
        self.scheduler_thread.start()
        logging.info("YouTube Scheduler started successfully!")
    
    def stop(self):
        """Stop the scheduler"""
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        schedule.clear()
        logging.info("YouTube Scheduler stopped")
    
    def get_next_upload_time(self):
        """Get the next scheduled upload time"""
        now = self.get_current_ist_time()
        today = now.date()
        
        next_uploads = []
        for upload_time in self.upload_times:
            hour, minute = map(int, upload_time.split(':'))
            upload_datetime = self.ist.localize(datetime.combine(today, datetime.min.time().replace(hour=hour, minute=minute)))
            
            # If time has passed today, schedule for tomorrow
            if upload_datetime <= now:
                upload_datetime += timedelta(days=1)
            
            next_uploads.append(upload_datetime)
        
        return min(next_uploads)
    
    def status(self):
        """Get scheduler status"""
        if not self.is_running:
            return "Scheduler is not running"
        
        next_upload = self.get_next_upload_time()
        current_time = self.get_current_ist_time()
        time_until_next = next_upload - current_time
        
        hours, remainder = divmod(time_until_next.total_seconds(), 3600)
        minutes, _ = divmod(remainder, 60)
        
        return f"Scheduler is running. Next upload in {int(hours)}h {int(minutes)}m at {next_upload.strftime('%H:%M IST')}"
    
    def test_trigger_now(self):
        """Test function to manually trigger video generation (for debugging)"""
        logging.info("TEST DEBUG: Manual trigger test started")
        current_time = self.get_current_ist_time().strftime('%H:%M')
        logging.info(f"TEST DEBUG: Triggering video generation for time slot: {current_time}")
        
        try:
            self.generate_and_upload_video(current_time)
            logging.info("TEST DEBUG: Manual trigger test completed successfully!")
            return True
        except Exception as e:
            logging.error(f"TEST DEBUG: Manual trigger test failed: {e}")
            return False

# Global scheduler instance
scheduler = YouTubeScheduler()

def start_youtube_scheduler():
    """Start the YouTube scheduler"""
    scheduler.start()

def stop_youtube_scheduler():
    """Stop the YouTube scheduler"""
    scheduler.stop()

def get_scheduler_status():
    """Get the current status of the scheduler"""
    return scheduler.status()

if __name__ == "__main__":
    # Test the scheduler
    print("YouTube Scheduler Test")
    print("====================")
    
    # Show current IST time
    ist_time = scheduler.get_current_ist_time()
    print(f"Current IST time: {ist_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Show next upload time
    next_upload = scheduler.get_next_upload_time()
    print(f"Next upload scheduled: {next_upload.strftime('%Y-%m-%d %H:%M:%S IST')}")
    
    # Start scheduler
    print("\nStarting scheduler...")
    scheduler.start()
    
    try:
        # Keep running
        while True:
            time.sleep(15)
            print(f"\nStatus: {scheduler.status()}")
    except KeyboardInterrupt:
        print("\nStopping scheduler...")
        scheduler.stop()
        print("Scheduler stopped.")
