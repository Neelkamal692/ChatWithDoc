# Deploying ChatWithDoc to Vercel

## Prerequisites

1. **Google Gemini API Key**: Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
3. **Git Repository**: Your code should be in a Git repository (GitHub, GitLab, etc.)

## Step-by-Step Deployment

### 1. Prepare Your Repository

Make sure your repository contains:
- ✅ `main.py` - FastAPI application
- ✅ `vercel.json` - Vercel configuration
- ✅ `requirements.txt` - Python dependencies
- ✅ `frontend/` - Static files
- ✅ All handler files (`pdfHandler.py`, `docHandler.py`, etc.)

### 2. Set Up Environment Variables

In your Vercel dashboard:

1. Go to your project settings
2. Navigate to "Environment Variables"
3. Add the following variables:

```
GOOGLE_API_KEY=your_actual_google_gemini_api_key
```

### 3. Deploy to Vercel

#### Option A: Using Vercel CLI
```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy
vercel

# Follow the prompts to connect your repository
```

#### Option B: Using Vercel Dashboard
1. Go to [vercel.com](https://vercel.com)
2. Click "New Project"
3. Import your Git repository
4. Configure environment variables
5. Deploy

### 4. Configure Build Settings

Vercel will automatically detect your Python project, but ensure:
- **Framework Preset**: Other
- **Build Command**: Leave empty (Vercel will auto-detect)
- **Output Directory**: Leave empty
- **Install Command**: `pip install -r requirements.txt`

### 5. Important Notes

#### ⚠️ Limitations
- **File Storage**: Vercel is serverless, so uploaded files are temporary
- **Memory Limits**: 1024MB RAM per function
- **Timeout**: 30 seconds max per request
- **Cold Starts**: First request may be slow

#### 🔧 Optimizations
- **Static Files**: Frontend files are served from CDN
- **Caching**: Vercel caches static assets automatically
- **Edge Functions**: Consider using edge functions for better performance

### 6. Testing Your Deployment

1. **Upload Files**: Test file upload functionality
2. **Process URLs**: Test URL processing
3. **Chat**: Test the chat functionality
4. **Error Handling**: Check error responses

### 7. Monitoring

- **Vercel Analytics**: Monitor performance
- **Function Logs**: Check for errors
- **Environment Variables**: Ensure API keys are set correctly

## Troubleshooting

### Common Issues

1. **"No module named 'langchain'"**
   - Ensure `requirements.txt` is in the root directory
   - Check that all dependencies are listed

2. **"GOOGLE_API_KEY not found"**
   - Verify environment variable is set in Vercel dashboard
   - Check variable name spelling

3. **"Function timeout"**
   - Large files may take longer to process
   - Consider file size limits

4. **"Memory limit exceeded"**
   - Large models may exceed memory limits
   - Consider using smaller models or edge functions

### Performance Tips

1. **Use Edge Functions**: For better performance
2. **Optimize Models**: Use smaller, faster models
3. **Cache Results**: Implement caching for repeated queries
4. **Monitor Usage**: Keep track of API calls and costs

## Support

If you encounter issues:
1. Check Vercel function logs
2. Verify environment variables
3. Test locally first
4. Check the [Vercel documentation](https://vercel.com/docs)
