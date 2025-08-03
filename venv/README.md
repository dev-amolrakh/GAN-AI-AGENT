# 🤖 Social Media AI Agent

An intelligent social media automation tool that generates and posts engaging content to Twitter with multiple operation modes for testing and production.

## ✨ Features

- **Two Operation Modes**: Testing mode for safe experimentation and Production mode for automated posting
- **Intelligent Content Generation**: Creates various types of posts using Google Gemini AI (primary), with OpenAI and Hugging Face as backups
- **Multiple Content Sources**: Uses Google Gemini 1.5 Flash, OpenAI, Hugging Face, or fallback templates for content generation
- **Trending Topics Integration**: Fetches current trends from multiple sources
- **Image Integration**: Automatically selects relevant images from curated collections
- **Scheduled Posting**: Automated posting at optimal engagement times
- **Admin Interface**: User-friendly command-line interface for management
- **Quality Control**: Built-in content quality assessment and improvement suggestions
- **Comprehensive Logging**: Detailed logging for monitoring and debugging

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd social-media-ai-agent
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

1. Copy the example environment file:

   ```bash
   copy .env.example .env
   ```

2. Edit `.env` and add your API credentials:
   - **Google Gemini API**: Primary AI for content generation (get from [Google AI Studio](https://makersuite.google.com/app/apikey))
   - **Twitter API**: Required for posting (get from [Twitter Developer Portal](https://developer.twitter.com/))
   - **OpenAI API**: Optional, backup content generation
   - **Hugging Face API**: Optional, free alternative
   - **News API**: Optional, for news-based content

### 4. Run the Agent

```bash
python app.py
```

## 🎯 Operation Modes

### Testing Mode

- **Purpose**: Test content generation and posting without automation
- **Features**:
  - Manual content testing
  - API connection verification
  - Post preview without publishing
  - Safe environment for experimentation

### Production Mode

- **Purpose**: Automated content posting with scheduling
- **Features**:
  - Scheduled posts at optimal times
  - Continuous operation
  - Automatic trend monitoring
  - Performance analytics

## 🛠️ Admin Interface Commands

| Command | Description             |
| ------- | ----------------------- |
| **1**   | Test Twitter Connection |
| **2**   | Test Content Generation |
| **3**   | Test Full Post Cycle    |
| **4**   | Start Production Mode   |
| **5**   | Stop Production Mode    |
| **6**   | View Agent Status       |
| **7**   | Manual Post Now         |
| **8**   | View Recent Posts       |
| **9**   | Switch Mode             |
| **0**   | Exit                    |

## 📅 Default Posting Schedule

### Weekdays

- 9:00 AM UTC
- 2:00 PM UTC
- 6:00 PM UTC

### Weekends

- 11:00 AM UTC
- 3:00 PM UTC
- 7:00 PM UTC

_Schedule can be customized through the admin interface_

## 📝 Content Types

The agent generates various types of engaging content:

1. **Informative**: Educational posts with valuable facts
2. **Questions**: Thought-provoking questions to encourage engagement
3. **Statistics**: Data-driven posts with interesting statistics
4. **Tips**: Practical advice and actionable insights
5. **News**: Current events and trending topics
6. **Opinions**: Thoughtful perspectives on relevant subjects
7. **Resources**: Useful tools and materials

## 🔧 Configuration

### Environment Variables

```env
# Primary AI for content generation
GOOGLE_API_KEY=your_google_gemini_key

# Required for Twitter posting
TWITTER_BEARER_TOKEN=your_token
TWITTER_API_KEY=your_key
TWITTER_API_SECRET=your_secret
TWITTER_ACCESS_TOKEN=your_token
TWITTER_ACCESS_SECRET=your_secret

# Optional for backup content generation
OPENAI_API_KEY=your_openai_key
HUGGINGFACE_API_KEY=your_hf_key
NEWS_API_KEY=your_news_key
```

### Custom Scheduling

You can modify posting times by editing the `production_schedule` in the agent:

```python
agent.set_production_schedule(
    weekday_times=["08:00", "13:00", "17:00"],
    weekend_times=["10:00", "14:00", "18:00"]
)
```

## 📊 Quality Control

The agent includes built-in quality assessment that checks for:

- Content length optimization
- Engagement elements (questions, calls-to-action)
- Hashtag usage
- Visual elements (emojis)
- Platform-specific formatting

## 🔒 Safety Features

- **Testing Mode**: Safe environment for testing without live posting
- **API Validation**: Checks API connectivity before operations
- **Error Handling**: Comprehensive error handling and recovery
- **Content Validation**: Quality checks before posting
- **Fallback Systems**: Multiple fallback options for content generation

## 📈 Monitoring and Logging

- **Real-time Logging**: Detailed logs saved to `social_media_agent.log`
- **Performance Tracking**: Monitor posting success rates
- **Status Dashboard**: View agent status and recent activity
- **Error Reporting**: Detailed error messages and troubleshooting

## 🆘 Troubleshooting

### Common Issues

1. **Twitter API Errors**:

   - Verify API credentials in `.env`
   - Check API usage limits
   - Ensure proper Twitter Developer account setup

2. **Content Generation Issues**:

   - Check internet connectivity
   - Verify API keys for OpenAI/Hugging Face
   - Fallback system will activate automatically

3. **Scheduling Problems**:
   - Ensure agent is in Production mode
   - Check system time and timezone settings
   - Monitor logs for scheduling errors

### Getting Help

1. Check the logs in `social_media_agent.log`
2. Use the admin interface diagnostic tools
3. Test individual components using Testing mode

## 🔄 Updates and Maintenance

- **Regular Updates**: Keep dependencies updated with `pip install -r requirements.txt --upgrade`
- **Log Rotation**: Logs are automatically rotated to prevent disk space issues
- **Performance Monitoring**: Use the admin interface to monitor agent performance

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly in Testing mode
5. Submit a pull request

## ⚠️ Disclaimer

This tool is for educational and legitimate marketing purposes only. Users are responsible for:

- Complying with platform terms of service
- Following applicable laws and regulations
- Ensuring content quality and appropriateness
- Managing API usage limits and costs

---

**Happy Posting! 🚀**
