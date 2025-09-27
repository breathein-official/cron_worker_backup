import os
import time
import schedule
import threading
from datetime import datetime, timedelta
import pytz
import csv
import hashlib
from youtube_uploader import upload_video
from app import generate_video
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('youtube_scheduler.log'),
        logging.StreamHandler()
    ]
)

class YouTubeScheduler:
    def __init__(self):
        self.ist = pytz.timezone('Asia/Kolkata')
        self.upload_times = ['07:30', '12:00', '19:00']  # 7:30 AM, 12 PM, 7:00 PM IST
        self.is_running = False
        self.scheduler_thread = None
        self.csv_log_file = 'video_upload_log.csv'
        self._initialize_csv_log()
        
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
            from youtube_uploader import get_youtube_service
            
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
        """Generate dynamic video title using Meta AI"""
        try:
            from meta_ai_api import MetaAI
            ai = MetaAI()
            
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
                response_dict = ai.prompt(message=prompt)
                response = response_dict.get("message", "").strip()
                
                # Parse the response
                if "\n" in response:
                    lines = response.split("\n")
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
                logging.warning(f"AI title generation failed: {e}, using fallback")
                import random
                fallback = random.choice(fallback_titles)
                return f"{fallback[0]}\n{fallback[1]}"
                
        except Exception as e:
            logging.warning(f"Meta AI not available: {e}, using fallback")
            import random
            fallback_titles = [
                ("Success Habits!", "Be the one ✅"),
                ("Achieve More!", "Be the one ✅"),
                ("Win Today!", "Achieve ✅"),
                ("Success Mindset!", "Be the one ✅"),
                ("Level Up!", "Achieve ✅")
            ]
            fallback = random.choice(fallback_titles)
            return f"{fallback[0]}\n{fallback[1]}"
    
    def create_video_description(self, upload_time):
        """Generate dynamic video description"""
        base_hashtags = "#BlockScroll #Productivity #DigitalDetox #Motivation #SelfImprovement #Focus #Success #Mindfulness #BreakTheScroll #shorts #trending #viral #business #creator #youtuber #youtubeshorts"
        
        descriptions = {
            '07:30': f"""Start your day right! This morning motivation will help you focus on building success habits, not scrolling mindlessly!

{base_hashtags} #MorningMotivation""",
            
            '12:00': f"""Midday reality check! While you're scrolling, others are building their dreams. Time to refocus and make every moment count.

{base_hashtags} #MiddayMotivation""",
            
            '19:30': f"""Evening wake-up call! Don't let another day slip away in endless scrolling. Your future self will thank you for the time you invest wisely.

{base_hashtags} #EveningMotivation"""
        }
        
        return descriptions.get(upload_time, f"""Focus on building success habits, not scrolling mindlessly! 

{base_hashtags}""")
    
    def generate_and_upload_video(self, upload_time):
        """Generate a video and upload it to YouTube"""
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
            logging.info(f"Starting video generation and upload for {upload_time} IST")
            
            # Generate video
            logging.info("Generating video...")
            generate_video()
            
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
                tags=["BlockScroll", "Motivation", "Productivity", "Digital Detox", "Self Improvement", "Focus", "Success", "Mindfulness", "Break The Scroll", "shorts", "trending", "viral", "business", "creator", "youtuber", "youtubeshorts"]
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
        for upload_time in self.upload_times:
            schedule.every().day.at(upload_time).do(
                self.generate_and_upload_video, 
                upload_time=upload_time
            )
            logging.info(f"Scheduled upload at {upload_time} IST daily")
    
    def run_scheduler(self):
        """Run the scheduler in a separate thread"""
        self.is_running = True
        logging.info("YouTube Scheduler started")
        logging.info(f"Current IST time: {self.get_current_ist_time().strftime('%Y-%m-%d %H:%M:%S')}")
        
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
        
        logging.info("YouTube Scheduler stopped")
    
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
            time.sleep(60)
            print(f"\nStatus: {scheduler.status()}")
    except KeyboardInterrupt:
        print("\nStopping scheduler...")
        scheduler.stop()
        print("Scheduler stopped.")
