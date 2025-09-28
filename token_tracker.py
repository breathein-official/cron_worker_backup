"""
Token Usage Tracker for OpenAI API
Tracks and logs token usage across all API calls
"""

import json
import os
from datetime import datetime
from typing import Dict, List

class TokenTracker:
    def __init__(self, log_file: str = "token_usage.json"):
        self.log_file = log_file
        self.session_usage = {
            "total_prompt_tokens": 0,
            "total_completion_tokens": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "calls_count": 0,
            "start_time": datetime.now().isoformat(),
            "calls": []
        }
        self.load_existing_data()
    
    def load_existing_data(self):
        """Load existing usage data from file"""
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r') as f:
                    data = json.load(f)
                    self.session_usage.update(data)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
    
    def log_usage(self, usage, operation: str = "API Call", model: str = "gpt-3.5-turbo"):
        """Log token usage for a single API call"""
        # Calculate costs (GPT-3.5-turbo pricing as of 2024)
        input_cost = (usage.prompt_tokens / 1000) * 0.0015
        output_cost = (usage.completion_tokens / 1000) * 0.002
        call_cost = input_cost + output_cost
        
        # Update session totals
        self.session_usage["total_prompt_tokens"] += usage.prompt_tokens
        self.session_usage["total_completion_tokens"] += usage.completion_tokens
        self.session_usage["total_tokens"] += usage.total_tokens
        self.session_usage["total_cost"] += call_cost
        self.session_usage["calls_count"] += 1
        
        # Log individual call
        call_data = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "model": model,
            "prompt_tokens": usage.prompt_tokens,
            "completion_tokens": usage.completion_tokens,
            "total_tokens": usage.total_tokens,
            "input_cost": input_cost,
            "output_cost": output_cost,
            "call_cost": call_cost
        }
        self.session_usage["calls"].append(call_data)
        
        # Print detailed usage
        print(f"\n🔢 Token Usage ({operation}):")
        print(f"   📝 Prompt tokens: {usage.prompt_tokens}")
        print(f"   🤖 Completion tokens: {usage.completion_tokens}")
        print(f"   📊 Total tokens: {usage.total_tokens}")
        print(f"💰 Cost for this call:")
        print(f"   📥 Input cost: ${input_cost:.6f}")
        print(f"   📤 Output cost: ${output_cost:.6f}")
        print(f"   💵 Call cost: ${call_cost:.6f}")
        
        # Print session totals
        print(f"\n📈 Session Totals:")
        print(f"   🔢 Total calls: {self.session_usage['calls_count']}")
        print(f"   📝 Total prompt tokens: {self.session_usage['total_prompt_tokens']}")
        print(f"   🤖 Total completion tokens: {self.session_usage['total_completion_tokens']}")
        print(f"   📊 Total tokens: {self.session_usage['total_tokens']}")
        print(f"   💵 Total cost: ${self.session_usage['total_cost']:.6f}")
        
        # Save to file
        self.save_data()
    
    def save_data(self):
        """Save usage data to file"""
        self.session_usage["last_updated"] = datetime.now().isoformat()
        with open(self.log_file, 'w') as f:
            json.dump(self.session_usage, f, indent=2)
    
    def get_daily_summary(self):
        """Get summary of today's usage"""
        today = datetime.now().date().isoformat()
        today_calls = [
            call for call in self.session_usage["calls"]
            if call["timestamp"].startswith(today)
        ]
        
        daily_tokens = sum(call["total_tokens"] for call in today_calls)
        daily_cost = sum(call["call_cost"] for call in today_calls)
        
        return {
            "date": today,
            "calls": len(today_calls),
            "total_tokens": daily_tokens,
            "total_cost": daily_cost
        }
    
    def print_summary(self):
        """Print a comprehensive usage summary"""
        print("\n" + "="*50)
        print("📊 OPENAI API USAGE SUMMARY")
        print("="*50)
        
        # Session summary
        print(f"🕐 Session started: {self.session_usage['start_time']}")
        print(f"🔢 Total API calls: {self.session_usage['calls_count']}")
        print(f"📝 Total prompt tokens: {self.session_usage['total_prompt_tokens']:,}")
        print(f"🤖 Total completion tokens: {self.session_usage['total_completion_tokens']:,}")
        print(f"📊 Total tokens: {self.session_usage['total_tokens']:,}")
        print(f"💵 Total cost: ${self.session_usage['total_cost']:.6f}")
        
        # Daily summary
        daily = self.get_daily_summary()
        print(f"\n📅 Today's Usage:")
        print(f"   🔢 Calls today: {daily['calls']}")
        print(f"   📊 Tokens today: {daily['total_tokens']:,}")
        print(f"   💵 Cost today: ${daily['total_cost']:.6f}")
        
        # Cost projections
        if daily['calls'] > 0:
            monthly_projection = daily['total_cost'] * 30
            print(f"\n📈 Projections:")
            print(f"   💰 Monthly cost (if daily usage continues): ${monthly_projection:.2f}")
        
        print("="*50)

# Global tracker instance
tracker = TokenTracker()

def track_usage(usage, operation: str = "API Call", model: str = "gpt-3.5-turbo"):
    """Convenience function to track usage"""
    tracker.log_usage(usage, operation, model)

def print_usage_summary():
    """Print usage summary"""
    tracker.print_summary()
