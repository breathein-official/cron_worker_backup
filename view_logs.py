#!/usr/bin/env python3
"""
cronWorker Upload Log Viewer
Simple script to view and analyze upload logs
"""

import csv
import sys
from datetime import datetime
import os

def view_logs(limit=20, show_all=False):
    """View upload logs with various options"""
    csv_file = 'exitLog.csv'
    
    if not os.path.exists(csv_file):
        print("ERROR: No upload log found. Run some uploads first.")
        return
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            rows = list(reader)
        
        if not rows:
            print("INFO: Upload log is empty.")
            return
        
        if show_all:
            display_rows = rows
        else:
            display_rows = rows[-limit:] if len(rows) > limit else rows
        
        print(f"\nLOG: cronWorker Upload Log")
        print("=" * 100)
        print(f"Showing {len(display_rows)} of {len(rows)} total entries")
        print("=" * 100)
        
        for i, row in enumerate(display_rows, 1):
            status_text = "SUCCESS" if row['upload_status'] == 'success' else "FAILED"
            print(f"\n{i}. {status_text}: {row['timestamp']}")
            print(f"   Time Slot: {row['upload_time_slot']}")
            print(f"   Title: {row['title']}")
            
            if row['upload_status'] == 'success':
                print(f"   YOUTUBE: {row['youtube_url']}")
                print(f"   VIDEO ID: {row['youtube_video_id']}")
            else:
                print(f"   ERROR: {row['error_message']}")
            
            print(f"   FILE: {row['video_filename']}")
            print(f"   SIZE: {row['video_size_mb']} MB | Duration: {row['video_duration_sec']}s")
            print(f"   HASH: {row['file_hash'][:16]}...")
            print("-" * 100)
            
    except Exception as e:
        print(f"ERROR: Error reading log file: {e}")

def show_stats():
    """Show upload statistics"""
    csv_file = 'exitLog.csv'
    
    if not os.path.exists(csv_file):
        print("ERROR: No upload log found.")
        return
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            rows = list(reader)
        
        if not rows:
            print("INFO: Upload log is empty.")
            return
        
        total = len(rows)
        successful = len([row for row in rows if row['upload_status'] == 'success'])
        failed = total - successful
        success_rate = (successful / total * 100) if total > 0 else 0
        
        # Time slot statistics
        time_slots = {}
        for row in rows:
            slot = row['upload_time_slot']
            if slot not in time_slots:
                time_slots[slot] = {'total': 0, 'success': 0}
            time_slots[slot]['total'] += 1
            if row['upload_status'] == 'success':
                time_slots[slot]['success'] += 1
        
        print(f"\nSTATISTICS: Upload Statistics")
        print("=" * 50)
        print(f"Total uploads: {total}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"Success rate: {success_rate:.1f}%")
        
        print(f"\nTIME SLOTS:")
        for slot, stats in time_slots.items():
            slot_success_rate = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
            print(f"  {slot}: {stats['success']}/{stats['total']} ({slot_success_rate:.1f}%)")
        
        # Recent activity
        recent_successful = [row for row in rows[-10:] if row['upload_status'] == 'success']
        if recent_successful:
            print(f"\nRECENT SUCCESSFUL UPLOADS:")
            for row in recent_successful[-5:]:
                print(f"  * {row['timestamp']} - {row['title'][:50]}...")
                print(f"    {row['youtube_url']}")
        
    except Exception as e:
        print(f"ERROR: Error reading statistics: {e}")

def export_logs():
    """Export logs to a formatted text file"""
    csv_file = 'exitLog.csv'
    export_file = f'upload_log_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
    
    if not os.path.exists(csv_file):
        print("ERROR: No upload log found.")
        return
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            rows = list(reader)
        
        with open(export_file, 'w', encoding='utf-8') as outfile:
            outfile.write("cronWorker Upload Log Export\n")
            outfile.write("=" * 50 + "\n")
            outfile.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            outfile.write(f"Total entries: {len(rows)}\n\n")
            
            for i, row in enumerate(rows, 1):
                outfile.write(f"{i}. {row['timestamp']} - {row['upload_time_slot']}\n")
                outfile.write(f"   Status: {row['upload_status']}\n")
                outfile.write(f"   Title: {row['title']}\n")
                if row['upload_status'] == 'success':
                    outfile.write(f"   YouTube: {row['youtube_url']}\n")
                else:
                    outfile.write(f"   Error: {row['error_message']}\n")
                outfile.write(f"   File: {row['video_filename']} ({row['video_size_mb']} MB)\n")
                outfile.write("-" * 50 + "\n")
        
        print(f"SUCCESS: Log exported to: {export_file}")
        
    except Exception as e:
        print(f"ERROR: Error exporting logs: {e}")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("""
cronWorker Log Viewer

Usage:
  python view_logs.py view [N]     - View recent N entries (default: 20)
  python view_logs.py all          - View all entries
  python view_logs.py stats        - Show statistics
  python view_logs.py export       - Export logs to text file
  python view_logs.py help         - Show this help
        """)
        return
    
    command = sys.argv[1].lower()
    
    if command == "view":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        view_logs(limit)
    elif command == "all":
        view_logs(show_all=True)
    elif command == "stats":
        show_stats()
    elif command == "export":
        export_logs()
    elif command == "help":
        print("""
cronWorker Log Viewer

This tool helps you view and analyze your video upload logs.

Commands:
  view [N]  - View the last N upload entries (default: 20)
  all       - View all upload entries
  stats     - Show upload statistics and success rates
  export    - Export logs to a formatted text file
  help      - Show this help message

The CSV log contains detailed information about each video:
- Timestamp and time slot
- Video title and description
- YouTube URL and video ID
- File size and duration
- Upload status and error messages
- File hash for verification
        """)
    else:
        print(f"ERROR: Unknown command: {command}")
        print("Use 'python view_logs.py help' for available commands")

if __name__ == "__main__":
    main()
