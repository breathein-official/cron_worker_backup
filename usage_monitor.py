#!/usr/bin/env python3
"""
Real-time Usage Monitor
Monitors token usage in real-time
"""

import time
import os
import json
from datetime import datetime
from token_tracker import tracker

def monitor_usage():
    """Monitor usage in real-time"""
    print("🔍 OpenAI API Usage Monitor")
    print("Press Ctrl+C to stop monitoring")
    print("=" * 50)
    
    last_call_count = 0
    
    try:
        while True:
            # Load current data
            if os.path.exists("token_usage.json"):
                with open("token_usage.json", 'r') as f:
                    data = json.load(f)
                
                current_calls = data.get("calls_count", 0)
                total_cost = data.get("total_cost", 0.0)
                total_tokens = data.get("total_tokens", 0)
                
                # Check if there are new calls
                if current_calls > last_call_count:
                    new_calls = current_calls - last_call_count
                    print(f"\n🆕 {new_calls} new API call(s) detected!")
                    print(f"📊 Total calls: {current_calls}")
                    print(f"🔢 Total tokens: {total_tokens:,}")
                    print(f"💵 Total cost: ${total_cost:.6f}")
                    print(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
                    print("-" * 30)
                    
                    last_call_count = current_calls
                
                # Show current status
                if current_calls > 0:
                    avg_cost = total_cost / current_calls
                    print(f"\r💡 Status: {current_calls} calls | ${total_cost:.6f} total | ${avg_cost:.6f} avg/call", end="", flush=True)
            
            time.sleep(2)  # Check every 2 seconds
            
    except KeyboardInterrupt:
        print("\n\n👋 Monitoring stopped.")
        print_usage_summary()

def print_usage_summary():
    """Print final usage summary"""
    if os.path.exists("token_usage.json"):
        with open("token_usage.json", 'r') as f:
            data = json.load(f)
        
        print("\n" + "="*50)
        print("📊 FINAL USAGE SUMMARY")
        print("="*50)
        print(f"🔢 Total API calls: {data.get('calls_count', 0)}")
        print(f"📝 Total prompt tokens: {data.get('total_prompt_tokens', 0):,}")
        print(f"🤖 Total completion tokens: {data.get('total_completion_tokens', 0):,}")
        print(f"📊 Total tokens: {data.get('total_tokens', 0):,}")
        print(f"💵 Total cost: ${data.get('total_cost', 0.0):.6f}")
        
        if data.get('calls_count', 0) > 0:
            avg_cost = data.get('total_cost', 0.0) / data.get('calls_count', 1)
            print(f"📈 Average cost per call: ${avg_cost:.6f}")
        
        print("="*50)

if __name__ == "__main__":
    monitor_usage()
