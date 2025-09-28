#!/usr/bin/env python3
"""
Scheduler Debugging Tool
Helps debug scheduler issues and timing problems
"""

import os
import sys
import time
import logging
from datetime import datetime, timedelta
import pytz
from scheduler import scheduler

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler_debug.log'),
        logging.StreamHandler()
    ]
)

def debug_scheduler_status():
    """Debug scheduler status and timing"""
    print("🔍 SCHEDULER DEBUG ANALYSIS")
    print("=" * 50)
    
    # Current time
    ist = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(ist)
    print(f"🕐 Current IST time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Scheduler status
    print(f"📊 Scheduler running: {scheduler.is_running}")
    print(f"📊 Upload times configured: {scheduler.upload_times}")
    
    # Next upload calculation
    try:
        next_upload = scheduler.get_next_upload_time()
        print(f"⏰ Next upload scheduled: {next_upload.strftime('%Y-%m-%d %H:%M:%S IST')}")
        
        time_until = next_upload - current_time
        hours, remainder = divmod(time_until.total_seconds(), 3600)
        minutes, _ = divmod(remainder, 60)
        print(f"⏳ Time until next upload: {int(hours)}h {int(minutes)}m")
        
    except Exception as e:
        print(f"❌ Error calculating next upload: {e}")
    
    # Check if current time matches any upload time
    current_time_str = current_time.strftime('%H:%M')
    print(f"🔍 Current time matches upload times: {current_time_str in scheduler.upload_times}")
    
    # Check schedule jobs
    import schedule
    print(f"📋 Total scheduled jobs: {len(schedule.jobs)}")
    for i, job in enumerate(schedule.jobs):
        print(f"   Job {i+1}: {job}")
        if hasattr(job, 'next_run') and job.next_run:
            print(f"      Next run: {job.next_run.strftime('%H:%M:%S IST')}")
        if hasattr(job, 'should_run'):
            print(f"      Should run now: {job.should_run}")

def test_manual_trigger():
    """Test manual trigger of video generation"""
    print("\n🧪 TESTING MANUAL TRIGGER")
    print("=" * 30)
    
    try:
        success = scheduler.test_trigger_now()
        if success:
            print("✅ Manual trigger: SUCCESS")
        else:
            print("❌ Manual trigger: FAILED")
    except Exception as e:
        print(f"❌ Manual trigger error: {e}")

def monitor_scheduler(duration_minutes=5):
    """Monitor scheduler for a specified duration"""
    print(f"\n👀 MONITORING SCHEDULER FOR {duration_minutes} MINUTES")
    print("=" * 50)
    
    start_time = datetime.now()
    end_time = start_time + timedelta(minutes=duration_minutes)
    
    check_count = 0
    while datetime.now() < end_time:
        check_count += 1
        current_time = datetime.now()
        
        print(f"\n🔍 Check #{check_count} - {current_time.strftime('%H:%M:%S')}")
        
        # Check if any jobs should run
        import schedule
        for i, job in enumerate(schedule.jobs):
            if hasattr(job, 'should_run') and job.should_run:
                print(f"🚨 Job {i+1} should run NOW!")
            elif hasattr(job, 'next_run') and job.next_run:
                next_run = job.next_run
                if hasattr(next_run, 'strftime'):
                    print(f"⏳ Job {i+1} next run: {next_run.strftime('%H:%M:%S')}")
        
        # Try to run pending jobs
        try:
            schedule.run_pending()
            print("✅ Ran pending jobs")
        except Exception as e:
            print(f"❌ Error running pending jobs: {e}")
        
        time.sleep(10)  # Check every 10 seconds
    
    print(f"\n✅ Monitoring completed after {duration_minutes} minutes")

def check_requirements():
    """Check if all requirements are met"""
    print("\n🔧 CHECKING REQUIREMENTS")
    print("=" * 30)
    
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
    
    all_good = True
    
    for file in required_files:
        exists = os.path.exists(file)
        print(f"{'✅' if exists else '❌'} {file}")
        if not exists:
            all_good = False
    
    for dir_name in required_dirs:
        exists = os.path.exists(dir_name)
        print(f"{'✅' if exists else '❌'} {dir_name}/")
        if not exists:
            all_good = False
    
    if all_good:
        print("✅ All requirements met!")
    else:
        print("❌ Some requirements missing!")
    
    return all_good

def main():
    """Main debugging function"""
    print("🐛 SCHEDULER DEBUGGING TOOL")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "status":
            debug_scheduler_status()
        elif command == "test":
            test_manual_trigger()
        elif command == "monitor":
            duration = int(sys.argv[2]) if len(sys.argv) > 2 else 5
            monitor_scheduler(duration)
        elif command == "requirements":
            check_requirements()
        elif command == "all":
            check_requirements()
            debug_scheduler_status()
            test_manual_trigger()
        else:
            print(f"Unknown command: {command}")
    else:
        print("""
Available commands:
  python debug_scheduler.py status       - Show scheduler status
  python debug_scheduler.py test         - Test manual trigger
  python debug_scheduler.py monitor [N]  - Monitor scheduler for N minutes
  python debug_scheduler.py requirements - Check requirements
  python debug_scheduler.py all          - Run all checks
        """)

if __name__ == "__main__":
    main()
