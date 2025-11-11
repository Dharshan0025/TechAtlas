# 🚦 Gemini API Rate Limit - Troubleshooting Guide

## ❌ **Error You're Seeing**

```json
{
  "error": "Query processing failed",
  "message": "429 You exceeded your current quota...",
  "status": 500
}
```

---

## 🔍 **What This Means**

You've hit the **Gemini API rate limit**. Google's free tier has strict limits:

| Model | Free Tier Limit | Paid Tier |
|-------|----------------|-----------|
| `gemini-1.5-flash` | **15 requests/min** | 1000 RPM |
| `gemini-1.5-pro` | **2 requests/min** | 360 RPM |
| `gemini-2.5-pro` | **2 requests/min** | 360 RPM |

**Your error**: You made more than 2 requests per minute to `gemini-2.5-pro`.

---

## ✅ **Solutions**

### **Option 1: Switch to Faster Model (Recommended)**

The `gemini-1.5-flash` model has **15 RPM** (7.5x more) on free tier!

**Steps:**

1. **Update your `.env` file:**
```env
# Change this line
GEMINI_MODEL=models/gemini-1.5-flash

# Add rate limit delay
RATE_LIMIT_DELAY=4.0
```

2. **Restart your server:**
```bash
# Stop server (Ctrl+C)
# Start again
python app.py
```

**Done!** You can now make 15 requests per minute instead of 2.

---

### **Option 2: Add Rate Limiting**

Automatically space out API calls to avoid hitting limits.

**Already implemented!** The system now includes:
- ✅ `Config.RATE_LIMIT_DELAY` - Configurable delay between calls
- ✅ `utils/rate_limiter.py` - Rate limiting utility
- ✅ Automatic waiting between API calls

**To use:**
```python
from utils.rate_limiter import rate_limit

@rate_limit
def my_gemini_call():
    # Your Gemini API call
    pass
```

---

### **Option 3: Upgrade to Paid Tier**

For production use, upgrade to paid tier:

1. **Go to**: https://ai.google.dev/pricing
2. **Enable billing** in Google Cloud Console
3. **Get higher limits**:
   - gemini-1.5-flash: **1000 RPM**
   - gemini-1.5-pro: **360 RPM**

---

## 🔧 **Quick Fix (Right Now)**

### **Step 1: Update .env**
```bash
# Edit your .env file
GEMINI_MODEL=models/gemini-1.5-flash
RATE_LIMIT_DELAY=4.0
```

### **Step 2: Restart Server**
```bash
python app.py
```

### **Step 3: Test Again**
```bash
curl -X POST http://localhost:5000/detect-decision \
  -H "Content-Type: application/json" \
  -d '{"message": "We decided to use PostgreSQL", "user": "test@example.com", "channel_id": "tech"}'
```

---

## 📊 **Model Comparison**

| Feature | gemini-1.5-flash | gemini-1.5-pro | gemini-2.5-pro |
|---------|------------------|----------------|----------------|
| **Speed** | ⚡ Fastest | 🐢 Slower | 🐢 Slower |
| **Free RPM** | **15** | 2 | 2 |
| **Quality** | Good | Better | Best |
| **Cost** | Lowest | Medium | Highest |
| **Best For** | High volume, fast response | Balanced | Complex tasks |

**Recommendation**: Use `gemini-1.5-flash` for most endpoints, reserve pro models for complex analysis.

---

## 🎯 **Best Practices**

### **1. Use Flash Model for High-Volume Endpoints**
```python
# For detection, search, simple queries
GEMINI_MODEL=models/gemini-1.5-flash
```

### **2. Add Delays Between Calls**
```python
# In .env
RATE_LIMIT_DELAY=4.0  # 4 seconds = 15 calls/min max
```

### **3. Implement Caching**
Cache responses to avoid repeated API calls:
```python
# Cache decision detection results
# Cache feasibility analysis
# Cache embeddings
```

### **4. Batch Operations**
Group multiple operations together when possible.

### **5. Monitor Usage**
Check your usage at: https://ai.dev/usage?tab=rate-limit

---

## 🔍 **Debugging Rate Limits**

### **Check Current Model**
```python
from config import Config
print(f"Current model: {Config.GEMINI_MODEL}")
print(f"Rate limit delay: {Config.RATE_LIMIT_DELAY}s")
```

### **Monitor API Calls**
Enable debug logging:
```env
LOG_LEVEL=DEBUG
```

### **Test Rate Limits**
```bash
# Make multiple requests quickly
for i in {1..5}; do
  curl -X POST http://localhost:5000/detect-decision \
    -H "Content-Type: application/json" \
    -d '{"message": "Test '$i'", "user": "test@example.com", "channel_id": "tech"}'
  echo ""
done
```

---

## 📝 **Configuration Reference**

### **Environment Variables**

```env
# Model Selection
GEMINI_MODEL=models/gemini-1.5-flash

# Rate Limiting
RATE_LIMIT_DELAY=4.0

# API Key
GEMINI_API_KEY=your_key_here
```

### **Available Models**

```python
# Fast, high volume (15 RPM free)
GEMINI_MODEL=models/gemini-1.5-flash

# Balanced (2 RPM free)
GEMINI_MODEL=models/gemini-1.5-pro

# Best quality (2 RPM free)
GEMINI_MODEL=models/gemini-2.5-pro

# Legacy (deprecated)
GEMINI_MODEL=models/gemini-pro
```

---

## ⚠️ **Common Mistakes**

### **❌ Don't Do This**
```python
# Making rapid API calls without delay
for i in range(10):
    gemini_api_call()  # Will hit rate limit!
```

### **✅ Do This Instead**
```python
# Add delays or use rate limiter
from utils.rate_limiter import rate_limit

@rate_limit
def gemini_api_call():
    # API call here
    pass

for i in range(10):
    gemini_api_call()  # Automatically spaced out
```

---

## 🚀 **After Fixing**

Once you've updated to `gemini-1.5-flash`:

1. **Test basic endpoint:**
```bash
curl http://localhost:5000/health
```

2. **Test detection:**
```bash
curl -X POST http://localhost:5000/detect-decision \
  -H "Content-Type: application/json" \
  -d '{"message": "We decided to migrate", "user": "test@example.com", "channel_id": "tech"}'
```

3. **Monitor logs** for any rate limit warnings

4. **Check usage** at https://ai.dev/usage

---

## 📞 **Still Having Issues?**

### **If you still see 429 errors:**

1. **Wait 60 seconds** - Let the quota reset
2. **Check your API key** - Ensure it's valid
3. **Verify model name** - Must be exact
4. **Check billing** - Free tier has daily limits too
5. **Monitor usage** - https://ai.dev/usage

### **Alternative: Use Mock Mode**

For testing without API calls:
```env
USE_MOCK_AI=True  # Add this to .env
```

---

## ✅ **Summary**

**Problem**: Hit Gemini API rate limit (2 RPM)  
**Solution**: Switch to `gemini-1.5-flash` (15 RPM)  
**Steps**: Update `.env` → Restart server → Test  
**Result**: 7.5x more requests per minute! 🚀

**Your system is now configured to handle rate limits properly!**
