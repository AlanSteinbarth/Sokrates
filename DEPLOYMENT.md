# 🚀 Deployment Guide - Sokrates v2.3.0

## Quick Deployment Options

### Option 1: Local Development
```bash
git clone https://github.com/AlanSteinbarth/Sokrates.git
cd Sokrates
pip install -r requirements.txt
cp .env.example .env
# Add your OpenAI API key to .env
streamlit run app.py
```

### Option 2: Docker (Coming Soon)
```bash
docker pull alansteinbarth/sokrates:latest
docker run -p 8501:8501 -e OPENAI_API_KEY=your_key sokrates:latest
```

### Option 3: Cloud Deployment

#### Streamlit Cloud
1. Fork this repository
2. Connect to [Streamlit Cloud](https://streamlit.io/cloud)
3. Add `OPENAI_API_KEY` to secrets
4. Deploy!

#### Heroku
```bash
heroku create your-sokrates-app
heroku config:set OPENAI_API_KEY=your_key
git push heroku main
```

## Production Considerations

### Environment Variables
- `OPENAI_API_KEY` - Required for AI functionality
- `APP_ENV=production` - Optional, enables production mode
- `LOG_LEVEL=INFO` - Optional, controls logging verbosity

### Security Checklist
- [ ] API key stored securely (not in code)
- [ ] HTTPS enabled for production
- [ ] Regular backup of user profiles
- [ ] Monitor API usage and costs

### Performance Optimization
- Expected load: 10-50 concurrent users
- Memory usage: ~100MB per user session
- API response time: 1-3 seconds
- Recommended: 1GB RAM, 1 CPU core

## Monitoring

### Health Check
Application provides health endpoint at `/health` (when implemented)

### Logs
- Application logs: `logs/app.log`
- Error logs: `logs/error.log`
- User activity: `db/activity.log`

## Troubleshooting

### Common Issues
1. **API Key Issues**: Verify key format starts with `sk-`
2. **Port Conflicts**: Change port with `streamlit run app.py --server.port 8502`
3. **Dependencies**: Ensure Python 3.8+ and all requirements installed

### Support
- GitHub Issues: [Report problems](https://github.com/AlanSteinbarth/Sokrates/issues)
- Email: alan.steinbarth@gmail.com
