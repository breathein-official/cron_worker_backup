#!/usr/bin/env python3
"""
Test Scheduler Timing
Test the scheduler with a time that's about to happen
"""

import os
import sys
import time
import logging
from datetime import datetime, timedelta
import pytz
from scheduler import scheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler_timing_test.log'),
        logging.StreamHandler()
    ]
)

def test_scheduler_with_near_time():
    """Test scheduler with a time that's about to happen"""
    print("🧪 TESTING SCHEDULER WITH NEAR TIME")
    print("=" * 50)
    
    # Get current time
    ist = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(ist)
    print(f"🕐 Current IST time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Calculate a test time 2 minutes from now
    test_time = current_time + timedelta(minutes=2)
    test_time_str = test_time.strftime('%H:%M')
    print(f"⏰ Test time (2 minutes from now): {test_time_str}")
    
    # Temporarily set upload times to include our test time
    original_times = scheduler.upload_times.copy()
    scheduler.upload_times = [test_time_str]
    print(f"🔧 Set upload times to: {scheduler.upload_times}")
    
    try:
        # Start scheduler
        print("🚀 Starting scheduler...")
        scheduler.start()
        
        # Wait for the test time
        print(f"⏳ Waiting for {test_time_str}...")
        time.sleep(130)  # Wait 2 minutes and 10 seconds
        
        # Check if video was created
        output_dir = "outputVideos"
        if os.path.exists(output_dir):
            video_files = [f for f in os.listdir(output_dir) if f.endswith('.mp4')]
            if video_files:
                print(f"✅ SUCCESS: Found {len(video_files)} video(s) created!")
                for video in video_files:
                    print(f"   📹 {video}")
            else:
                print("❌ FAILED: No videos found in output directory")
        else:
            print("❌ FAILED: Output directory not found")
        
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
    finally:
        # Stop scheduler and restore original times
        print("🛑 Stopping scheduler...")
        scheduler.stop()
        scheduler.upload_times = original_times
        print(f"🔄 Restored original upload times: {original_times}")

def test_manual_trigger():
    """Test manual trigger"""
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

def main():
    """Main test function"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "manual":
            test_manual_trigger()
        elif command == "timing":
            test_scheduler_with_near_time()
        else:
            print("Unknown command. Use 'manual' or 'timing'")
    else:
        print("""
Scheduler Timing Test

Commands:
  python test_scheduler_timing.py manual  - Test manual trigger
  python test_scheduler_timing.py timing  - Test scheduler with near time
        """)

if __name__ == "__main__":
    main()
