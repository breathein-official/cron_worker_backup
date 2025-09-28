#!/usr/bin/env python3
"""
View OpenAI API Usage
Run this script to see your token usage and costs
"""

from token_tracker import print_usage_summary, tracker
import json
import os

def main():
    print("🔍 Checking OpenAI API Usage...")
    
    if not os.path.exists("token_usage.json"):
        print("❌ No usage data found. Run your application first to generate usage data.")
        return
    
    # Print comprehensive summary
    print_usage_summary()
    
    # Show recent calls
    if tracker.session_usage["calls"]:
        print("\n📋 Recent API Calls:")
        print("-" * 80)
        recent_calls = tracker.session_usage["calls"][-5:]  # Last 5 calls
        
        for i, call in enumerate(recent_calls, 1):
            timestamp = call["timestamp"][:19].replace("T", " ")
            print(f"{i}. {call['operation']} - {timestamp}")
            print(f"   Tokens: {call['total_tokens']} | Cost: ${call['call_cost']:.6f}")
            print()
    
    # Show cost breakdown
    if tracker.session_usage["calls_count"] > 0:
        avg_cost_per_call = tracker.session_usage["total_cost"] / tracker.session_usage["calls_count"]
        print(f"📊 Average cost per call: ${avg_cost_per_call:.6f}")
        
        # Estimate monthly cost
        daily_calls = len([call for call in tracker.session_usage["calls"] 
                          if call["timestamp"].startswith(tracker.session_usage["start_time"][:10])])
        if daily_calls > 0:
            daily_cost = sum(call["call_cost"] for call in tracker.session_usage["calls"] 
                           if call["timestamp"].startswith(tracker.session_usage["start_time"][:10]))
            monthly_estimate = daily_cost * 30
            print(f"📈 Estimated monthly cost: ${monthly_estimate:.2f}")

if __name__ == "__main__":
    main()
