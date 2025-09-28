# 🔢 OpenAI Token Usage Tracking Guide

## Overview
Your application now includes comprehensive token usage tracking to monitor your OpenAI API costs and usage patterns.

## Features

### ✅ **Real-time Token Tracking**
- Tracks prompt tokens, completion tokens, and total tokens
- Calculates costs based on current OpenAI pricing
- Logs every API call with timestamps
- Provides session and daily summaries

### ✅ **Cost Monitoring**
- Real-time cost calculation
- Session totals and averages
- Daily and monthly projections
- Cost breakdown by operation type

### ✅ **Usage Analytics**
- Total API calls count
- Token usage patterns
- Cost per call analysis
- Historical usage data

## Files Added

1. **`token_tracker.py`** - Core tracking functionality
2. **`view_usage.py`** - View usage summary
3. **`usage_monitor.py`** - Real-time monitoring
4. **`token_usage.json`** - Usage data storage (auto-created)

## How to Use

### 1. **Automatic Tracking**
Token usage is automatically tracked when you run your application:
```python
from app import ai_function

# This will automatically track tokens
result = ai_function()
```

### 2. **View Usage Summary**
```bash
python view_usage.py
```

### 3. **Real-time Monitoring**
```bash
python usage_monitor.py
```

### 4. **Programmatic Access**
```python
from token_tracker import tracker, print_usage_summary

# Print summary
print_usage_summary()

# Access raw data
print(f"Total calls: {tracker.session_usage['calls_count']}")
print(f"Total cost: ${tracker.session_usage['total_cost']:.6f}")
```

## Sample Output

```
🔢 Token Usage (Notification Generation):
   📝 Prompt tokens: 45
   🤖 Completion tokens: 23
   📊 Total tokens: 68
💰 Cost for this call:
   📥 Input cost: $0.000068
   📤 Output cost: $0.000046
   💵 Call cost: $0.000114

📈 Session Totals:
   🔢 Total calls: 1
   📝 Total prompt tokens: 45
   🤖 Total completion tokens: 23
   📊 Total tokens: 68
   💵 Total cost: $0.000114
```

## Cost Breakdown

### GPT-3.5-turbo Pricing (2024)
- **Input tokens**: $0.0015 per 1K tokens
- **Output tokens**: $0.002 per 1K tokens

### Example Costs
- **Short notification** (~50 tokens): ~$0.0001
- **Video title** (~30 tokens): ~$0.00006
- **100 calls per day**: ~$0.01
- **1000 calls per day**: ~$0.10

## Usage Patterns

### Typical Usage
- **Notification generation**: 40-60 tokens per call
- **Title generation**: 25-40 tokens per call
- **Cost per video**: ~$0.0001-0.0002

### High Usage Scenarios
- **100 videos per day**: ~$0.01-0.02
- **1000 videos per day**: ~$0.10-0.20
- **Monthly (30 days)**: ~$0.30-6.00

## Monitoring Tools

### 1. **View Usage Summary**
```bash
python view_usage.py
```
Shows:
- Total calls and tokens
- Total cost
- Recent API calls
- Cost projections

### 2. **Real-time Monitor**
```bash
python usage_monitor.py
```
Shows:
- Live usage updates
- New call notifications
- Running totals
- Cost alerts

### 3. **JSON Data Access**
```python
import json

with open('token_usage.json', 'r') as f:
    data = json.load(f)
    
print(f"Total cost: ${data['total_cost']:.6f}")
```

## Cost Optimization Tips

### 1. **Reduce Token Usage**
- Use shorter prompts
- Lower max_tokens when possible
- Cache similar requests

### 2. **Monitor Usage**
- Set up daily cost alerts
- Review usage patterns
- Optimize based on data

### 3. **Budget Management**
- Set monthly spending limits
- Use usage projections
- Monitor cost trends

## Troubleshooting

### No Usage Data
- Ensure you've run the application at least once
- Check that `token_usage.json` exists
- Verify OpenAI API calls are working

### High Costs
- Review token usage patterns
- Check for unnecessary API calls
- Optimize prompt lengths

### Missing Data
- Check file permissions
- Ensure JSON file is not corrupted
- Restart the application

## Advanced Features

### Custom Tracking
```python
from token_tracker import track_usage

# Track custom operations
track_usage(usage, "Custom Operation", "gpt-4")
```

### Data Export
```python
import json

# Export usage data
with open('token_usage.json', 'r') as f:
    data = json.load(f)

# Save to CSV or other format
```

### Cost Alerts
```python
# Set up cost alerts
if tracker.session_usage['total_cost'] > 1.0:
    print("⚠️ High usage detected!")
```

## Benefits

- ✅ **Cost Control**: Know exactly how much you're spending
- ✅ **Usage Optimization**: Identify patterns and optimize
- ✅ **Budget Planning**: Project future costs
- ✅ **Transparency**: Full visibility into API usage
- ✅ **Debugging**: Track which operations use the most tokens
