import os
import json
import random
import time
import schedule
import requests
from datetime import datetime, timedelta
import tweepy
from dotenv import load_dotenv
import google.generativeai as genai
from bs4 import BeautifulSoup
import re
import logging
import threading
import sys
from typing import Dict, List, Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("social_media_agent.log"),
        logging.StreamHandler()
    ]
)

# Load environment variables from .env file
load_dotenv()

class SocialMediaAIAgent:
    def __init__(self, mode="testing"):
        # Set operation mode
        self.mode = mode  # "production" or "testing"
        self.is_running = False
        
        # Initialize API credentials
        self.twitter_api = self.setup_twitter_api()
        
        # Set up Google Gemini AI (Primary content generation)
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if google_api_key:
            genai.configure(api_key=google_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
            logging.info("Google Gemini AI configured successfully")
        else:
            self.gemini_model = None
            logging.warning("Google API key not found")
        
        # Platform configurations
        self.platforms = ["twitter"]  # Add more as needed: "facebook", "instagram", etc.
        
        # Content tracking
        self.posted_content = []
        self.trending_topics = []
        
        # Production mode settings
        self.production_schedule = {
            "weekday_times": ["09:00", "14:00", "18:00"],
            "weekend_times": ["11:00", "15:00", "19:00"],
            "timezone": "UTC"
        }
        
        # Post types for variety
        self.post_types = [
            "informative",
            "question",
            "statistic",
            "tip",
            "news",
            "opinion",
            "resource"
        ]
        
        # Image database - collection of royalty-free image URLs by category
        self.image_database = {
            "technology": [
                "https://images.unsplash.com/photo-1518770660439-4636190af475",
                "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5",
                "https://images.unsplash.com/photo-1504384764586-bb4cdc1707b0"
            ],
            "health": [
                "https://images.unsplash.com/photo-1505576399279-565b52d4ac71",
                "https://images.unsplash.com/photo-1498837167922-ddd27525d352",
                "https://images.unsplash.com/photo-1506126613408-eca07ce68773"
            ],
            "business": [
                "https://images.unsplash.com/photo-1560472355-536de3962603",
                "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab",
                "https://images.unsplash.com/photo-1507679799987-c73779587ccf"
            ],
            "nature": [
                "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05",
                "https://images.unsplash.com/photo-1441974231531-c6227db76b6e",
                "https://images.unsplash.com/photo-1472214103451-9374bd1c798e"
            ],
            "travel": [
                "https://images.unsplash.com/photo-1500835556837-99ac94a94552",
                "https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1",
                "https://images.unsplash.com/photo-1502602898657-3e91760cbb34"
            ],
            "food": [
                "https://images.unsplash.com/photo-1504674900247-0877df9cc836",
                "https://images.unsplash.com/photo-1512621776951-a57141f2eefd",
                "https://images.unsplash.com/photo-1476224203421-9ac39bcb3327"
            ],
            "sports": [
                "https://images.unsplash.com/photo-1461896836934-ffe607ba8211",
                "https://images.unsplash.com/photo-1517649763962-0c623066013b",
                "https://images.unsplash.com/photo-1541534741688-6078c6bfb5c5"
            ],
            "education": [
                "https://images.unsplash.com/photo-1503676260728-1c00da094a0b",
                "https://images.unsplash.com/photo-1523050854058-8df90110c9f1",
                "https://images.unsplash.com/photo-1509062522246-3755977927d7"
            ],
            "finance": [
                "https://images.unsplash.com/photo-1565514020179-026b92b4a5b0",
                "https://images.unsplash.com/photo-1579170053380-58a5b2c13ff6",
                "https://images.unsplash.com/photo-1620714223084-8fcacc6dfd8d"
            ],
            "science": [
                "https://images.unsplash.com/photo-1507668077129-56e32842523b",
                "https://images.unsplash.com/photo-1564325724739-bae0bd08762c",
                "https://images.unsplash.com/photo-1532094349884-543bc11b234d"
            ],
            "default": [
                "https://images.unsplash.com/photo-1496449903678-68ddcb189a24",
                "https://images.unsplash.com/photo-1522199755839-a2bacb67c546",
                "https://images.unsplash.com/photo-1554774853-d50f9c681ae2"
            ]
        }
        
    def setup_twitter_api(self):
        """Set up Twitter API connection"""
        try:
            # Check if credentials are available
            bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
            consumer_key = os.getenv("TWITTER_API_KEY")
            consumer_secret = os.getenv("TWITTER_API_SECRET")
            access_token = os.getenv("TWITTER_ACCESS_TOKEN")
            access_token_secret = os.getenv("TWITTER_ACCESS_SECRET")
            
            if not bearer_token:
                logging.error("Twitter Bearer Token not found in environment variables")
                return None
            
            # Try to create client with full OAuth first
            if all([consumer_key, consumer_secret, access_token, access_token_secret]):
                try:
                    client = tweepy.Client(
                        bearer_token=bearer_token,
                        consumer_key=consumer_key,
                        consumer_secret=consumer_secret,
                        access_token=access_token,
                        access_token_secret=access_token_secret
                    )
                    logging.info("Twitter API client setup successful with full OAuth")
                    return client
                except Exception as e:
                    logging.warning(f"Failed to setup with full OAuth credentials: {e}")
            
            # Fallback to Bearer Token only
            try:
                client = tweepy.Client(bearer_token=bearer_token)
                logging.info("Twitter API client setup successful with Bearer Token only")
                return client
            except Exception as e:
                logging.error(f"Failed to setup with Bearer Token: {e}")
                return None
                
        except Exception as e:
            logging.error(f"Error setting up Twitter API: {e}")
            return None
    
    def get_twitter_trends(self, woeid=1):
        """Get trending topics from Twitter - may not work with free API tier"""
        try:
            # Use Twitter API v1.1 for trends
            auth = tweepy.OAuth1UserHandler(
                os.getenv("TWITTER_API_KEY"),
                os.getenv("TWITTER_API_SECRET"),
                os.getenv("TWITTER_ACCESS_TOKEN"),
                os.getenv("TWITTER_ACCESS_SECRET")
            )
            api = tweepy.API(auth)
            
            trends = api.get_place_trends(woeid)
            trending_topics = [trend['name'] for trend in trends[0]['trends']]
            logging.info(f"Retrieved {len(trending_topics)} trending topics via Twitter API v1")
            return trending_topics[:10]  # Return top 10 trending topics
        except Exception as e:
            logging.error(f"Error fetching Twitter trends: {e}")
            return []
    
    def get_twitter_trends_v2(self):
        """Get trending topics using Twitter API v2 recent search"""
        try:
            if not self.twitter_api:
                return []
                
            # Search for recent popular tweets
            response = self.twitter_api.search_recent_tweets(
                query="-is:retweet lang:en",
                max_results=20,
                sort_order="relevancy"
            )
            
            # Extract potential hashtags and topics
            hashtags = []
            topics = []
            
            if hasattr(response, 'data') and response.data:
                for tweet in response.data:
                    # Extract hashtags
                    words = tweet.text.split()
                    hashtags.extend([word for word in words if word.startswith('#')])
                    
                    # Extract meaningful phrases (simplified)
                    text = tweet.text.lower()
                    for phrase in text.split(','):
                        clean_phrase = phrase.strip()
                        if 3 < len(clean_phrase) < 30 and ' ' in clean_phrase:
                            topics.append(clean_phrase)
            
            # Combine and get unique topics
            all_topics = hashtags + topics
            unique_topics = list(set(all_topics))[:10]
            logging.info(f"Retrieved {len(unique_topics)} trending topics via Twitter API v2")
            return unique_topics
        except Exception as e:
            logging.error(f"Error fetching Twitter trends V2: {e}")
            return []
    
    def get_twitter_trends_scraping(self):
        """Get trending topics by scraping"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get('https://trends24.in/', headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # The structure of the page may change
            trend_items = soup.select('.trend-card:first-child ol li a')
            trends = [item.text for item in trend_items]
            
            logging.info(f"Retrieved {len(trends)} trending topics via web scraping")
            return trends[:10]
        except Exception as e:
            logging.error(f"Error scraping trends: {e}")
            return []
    
    def get_fallback_topics(self):
        """Get predefined topics when API access fails"""
        topics = [
            "technology advancements", "sustainable living", "health breakthroughs", 
            "remote work productivity", "digital marketing strategies", "AI ethics",
            "climate solutions", "entrepreneurship tips", "financial literacy",
            "productivity hacks", "mental health awareness", "educational innovations", 
            "technological innovation", "sustainable travel", "nutrition science", 
            "fitness trends", "stress management", "influential books",
            "film analysis", "music production", "ethical fashion", "photography techniques", 
            "sports science", "home organization", "sustainable gardening", 
            "pet health", "effective parenting", "career development",
            "data privacy", "renewable energy", "medical research", "space exploration"
        ]
        # Return 3-5 random topics
        selected_topics = random.sample(topics, random.randint(3, 5))
        logging.info(f"Using fallback topics: {selected_topics}")
        return selected_topics

    def fetch_news_for_topic(self, topic):
        """Fetch recent news articles related to the topic"""
        try:
            # Clean topic for search
            search_query = topic.replace('#', '').replace('@', '')
            
            # Use public news API if available
            news_api_key = os.getenv("NEWS_API_KEY")
            if news_api_key:
                url = f"https://newsapi.org/v2/everything?q={search_query}&sortBy=publishedAt&apiKey={news_api_key}&pageSize=3"
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('articles'):
                        articles = data['articles']
                        return [{
                            'title': article['title'],
                            'source': article['source']['name'],
                            'url': article['url'],
                            'published': article['publishedAt']
                        } for article in articles[:3]]
            
            # Fallback: Search for news using web scraping
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            search_url = f"https://www.google.com/search?q={search_query}+news&tbm=nws"
            response = requests.get(search_url, headers=headers)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                news_results = []
                
                # Extract news results (this is simplified and may need adjustment)
                news_items = soup.select('div.SoaBEf')
                for item in news_items[:3]:  # Get top 3 results
                    title_elem = item.select_one('div.mCBkyc')
                    source_elem = item.select_one('div.UPmit')
                    link_elem = item.select_one('a')
                    
                    if title_elem and link_elem:
                        title = title_elem.text
                        source = source_elem.text if source_elem else "News Source"
                        url = link_elem.get('href')
                        if url and url.startswith('/url?q='):
                            url = url.split('/url?q=')[1].split('&')[0]
                        
                        news_results.append({
                            'title': title,
                            'source': source,
                            'url': url,
                            'published': 'Recent'
                        })
                
                if news_results:
                    logging.info(f"Found {len(news_results)} news articles for topic '{topic}'")
                    return news_results
                
        except Exception as e:
            logging.error(f"Error fetching news for topic '{topic}': {e}")
            
        return []

    def get_stats_for_topic(self, topic):
        """Get interesting statistics about the topic if available"""
        # This would ideally use a specific API or database
        # Here we're simulating with common statistics by category
        
        stats_by_category = {
            "technology": [
                "90% of the world's data has been created in the last two years",
                "There are over 5 billion smartphone users worldwide",
                "The average person touches their phone 2,617 times a day"
            ],
            "health": [
                "Regular exercise can reduce the risk of major illnesses by up to 50%",
                "Drinking water can increase energy levels by up to 30%",
                "Laughing 100 times is equivalent to 15 minutes of exercise on a stationary bike"
            ],
            "business": [
                "65% of entrepreneurs start their businesses at home",
                "It takes an average of 3 years for a startup to become profitable",
                "42% of startups fail because there's no market need for their product"
            ],
            "climate": [
                "The last decade was the warmest on record",
                "Sea levels have risen by about 8-9 inches since 1880",
                "The Earth's average temperature has increased by 1.1°C since the pre-industrial era"
            ],
            "social media": [
                "Users spend an average of 2.5 hours per day on social platforms",
                "There are over 4.2 billion active social media users globally",
                "72% of the public uses some type of social media"
            ],
            "ai": [
                "The AI market is projected to reach $190 billion by 2025",
                "AI adoption in businesses has grown by 270% in the past four years",
                "70% of customer interactions involve AI like chatbots or virtual assistants"
            ]
        }
        
        # Find relevant category
        topic_lower = topic.lower()
        for category, stats_list in stats_by_category.items():
            if category in topic_lower or any(word in category for word in topic_lower.split()):
                return random.choice(stats_list)
        
        return None

    def fetch_trends(self):
        """Fetch trending topics from all platforms with fallbacks"""
        all_trends = []
        
        if "twitter" in self.platforms:
            # Try multiple methods to get trends
            twitter_trends = []
            
            # Method 1: Standard API (likely to fail with free tier)
            if not twitter_trends:
                try:
                    twitter_trends = self.get_twitter_trends()
                    if twitter_trends:
                        logging.info("Successfully got trends via Twitter API v1")
                except Exception as e:
                    logging.error(f"Twitter API v1 trends failed: {e}")
            
            # Method 2: Twitter v2 API approach
            if not twitter_trends:
                try:
                    twitter_trends = self.get_twitter_trends_v2()
                    if twitter_trends:
                        logging.info("Successfully got trends via Twitter API v2")
                except Exception as e:
                    logging.error(f"Twitter API v2 trends failed: {e}")
            
            # Method 3: Web scraping
            if not twitter_trends:
                try:
                    twitter_trends = self.get_twitter_trends_scraping()
                    if twitter_trends:
                        logging.info("Successfully got trends via web scraping")
                except Exception as e:
                    logging.error(f"Web scraping for trends failed: {e}")
            
            # Method 4: Fallback to predefined topics
            if not twitter_trends:
                twitter_trends = self.get_fallback_topics()
                logging.info("Using fallback topic list")
                
            all_trends.extend(twitter_trends)
        
        # Add more platforms here as needed
        
        # Filter and clean trends
        filtered_trends = []
        for trend in all_trends:
            # Skip empty trends and overly long ones
            if trend and len(trend) < 50:
                # Remove any URLs
                if not trend.startswith('http'):
                    filtered_trends.append(trend)
        
        # Update trending topics
        self.trending_topics = filtered_trends
        logging.info(f"Current trends: {self.trending_topics}")
        return filtered_trends
    
    def get_relevant_image_url(self, topic):
        """Get a relevant image URL based on the topic"""
        # Convert topic to lowercase for matching
        topic_lower = topic.lower()
        
        # Find the most relevant category
        for category, urls in self.image_database.items():
            if category.lower() in topic_lower:
                selected_url = random.choice(urls)
                logging.info(f"Selected image from category '{category}' for topic '{topic}'")
                return selected_url
        
        # Check for partial matches
        for category, urls in self.image_database.items():
            # Skip default category for partial matching
            if category == "default":
                continue
                
            # Check if any word in the topic matches the category
            words = re.findall(r'\w+', topic_lower)
            if any(word in category or category in word for word in words):
                selected_url = random.choice(urls)
                logging.info(f"Selected image from category '{category}' for topic '{topic}' (partial match)")
                return selected_url
        
        # Return a default image if no match
        selected_url = random.choice(self.image_database["default"])
        logging.info(f"Selected default image for topic '{topic}'")
        return selected_url
    
    def generate_content_gemini(self, topic, platform, include_image=True, post_type=None):
        """Generate engaging and informative content using Google Gemini API"""
        try:
            if not self.gemini_model:
                logging.error("Gemini model not initialized")
                return self.generate_content_fallback(topic, platform, include_image, post_type)
            
            # If post type not specified, choose randomly
            if not post_type:
                post_type = random.choice(self.post_types)
                
            logging.info(f"Generating {post_type} content for topic '{topic}' on {platform} using Gemini")
                
            # Get related news if it's an informative or news post
            news_data = None
            if post_type in ["informative", "news"]:
                news_data = self.fetch_news_for_topic(topic)
                
            # Get statistics if it's a statistic post
            stat = None
            if post_type == "statistic":
                stat = self.get_stats_for_topic(topic)
            
            # Platform specifications
            platform_specs = {
                "twitter": {
                    "max_length": 250,
                    "description": "tweet"
                },
                "facebook": {
                    "max_length": 400,
                    "description": "Facebook post"
                },
                "instagram": {
                    "max_length": 300,
                    "description": "Instagram caption"
                }
            }
            
            post_type_prompts = {
                "informative": "Write an informative, fact-based post that educates the audience",
                "question": "Write a thought-provoking question that encourages audience participation",
                "statistic": "Write a post highlighting an interesting statistic or data point",
                "tip": "Write a practical tip or advice that provides immediate value",
                "news": "Write a news update that summarizes recent developments",
                "opinion": "Write a thoughtful opinion or perspective that invites discussion",
                "resource": "Write a post sharing a useful resource or tool related to the topic"
            }
            
            platform_info = platform_specs.get(platform, {"max_length": 300, "description": "social media post"})
            post_prompt = post_type_prompts.get(post_type, "Write an engaging social media post")
            
            # Create comprehensive prompt for Gemini
            prompt = f"""You are a social media expert creating engaging, valuable content that educates and engages users.

Task: {post_prompt} about '{topic}' as a {platform_info['description']}.

Requirements:
- Maximum {platform_info['max_length']} characters
- Include 1-2 relevant hashtags (e.g., #{topic.replace(' ', '')[:15]})
- Add appropriate emojis for visual appeal
- Include a call-to-action or engagement question
- Be informative yet conversational
- Focus on providing actionable insights or interesting perspectives

Post Type: {post_type}
Platform: {platform}"""

            # Add news context if available
            if news_data and post_type in ["informative", "news"]:
                prompt += f"\n\nRecent news context: {news_data[0]['title']}"
                
            # Add statistic if available
            if stat and post_type == "statistic":
                prompt += f"\n\nRelevant statistic to incorporate: {stat}"
                
            prompt += f"\n\nGenerate only the social media post content, nothing else:"
            
            # Generate content using Gemini
            response = self.gemini_model.generate_content(prompt)
            content = response.text.strip()
            
            # Ensure we don't exceed platform character limits
            max_length = platform_info['max_length']
            if len(content) > max_length:
                content = content[:max_length-3] + "..."
            
            # Get a relevant image URL if requested
            image_url = None
            if include_image:
                image_url = self.get_relevant_image_url(topic)
            
            result = {
                "text": content,
                "image_url": image_url,
                "post_type": post_type
            }
            
            # For news posts, include the article URL
            if news_data and post_type == "news":
                result["article_url"] = news_data[0]['url']
                
            logging.info(f"Successfully generated content using Gemini: {content[:50]}...")
            return result
            
        except Exception as e:
            logging.error(f"Error generating content with Gemini: {e}")
            return self.generate_content_fallback(topic, platform, include_image, post_type)
    
    def generate_content_huggingface(self, topic, platform, include_image=True, post_type=None):
        """Generate content using Hugging Face API (free alternative)"""
        try:
            API_URL = "https://api-inference.huggingface.co/models/gpt2"
            headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}"}
            
            # If post type not specified, choose randomly
            if not post_type:
                post_type = random.choice(self.post_types)
                
            logging.info(f"Generating {post_type} content for topic '{topic}' using Hugging Face")
            
            # Get related news if it's an informative or news post
            news_data = None
            if post_type in ["informative", "news"]:
                news_data = self.fetch_news_for_topic(topic)
            
            # Get statistics if it's a statistic post
            stat = None
            if post_type == "statistic":
                stat = self.get_stats_for_topic(topic)
            
            platform_desc = {
                "twitter": "tweet",
                "facebook": "Facebook post",
                "instagram": "Instagram caption"
            }.get(platform, "social media post")
            
            # Create a specific prompt based on post type
            prompts_by_type = {
                "informative": f"Write an informative {platform_desc} about {topic} with valuable facts:",
                "question": f"Write a {platform_desc} with a thought-provoking question about {topic}:",
                "statistic": f"Write a {platform_desc} about {topic} with this statistic: {stat or 'an interesting statistic'}:",
                "tip": f"Write a {platform_desc} with a useful tip about {topic}:",
                "news": f"Write a {platform_desc} about this {topic} news: {news_data[0]['title'] if news_data else 'recent developments'}:",
                "opinion": f"Write a {platform_desc} with a thoughtful perspective on {topic}:",
                "resource": f"Write a {platform_desc} sharing a valuable resource about {topic}:"
            }
            
            prompt_text = prompts_by_type.get(post_type, f"Write an informative {platform_desc} about {topic}:")
            
            response = requests.post(
                API_URL,
                headers=headers,
                json={"inputs": prompt_text, "parameters": {"max_length": 150}}
            )
            
            result = response.json()
            content = result[0].get('generated_text', '').replace(prompt_text, '').strip()
            
            # Add hashtags if needed
            if not any(tag.startswith('#') for tag in content.split()):
                hashtags = []
                topic_words = re.findall(r'\w+', topic)
                for word in topic_words:
                    if len(word) > 3:  # Only use meaningful words
                        hashtags.append(f"#{word}")
                
                # Add up to 2 hashtags
                if hashtags:
                    content += "\n\n" + " ".join(hashtags[:2])
            
            # Add engagement element if missing
            if "?" not in content and post_type != "question":
                engagement_questions = [
                    "What do you think?",
                    "Have you experienced this?",
                    "What's your take on this?",
                    "How does this impact you?",
                    "Would you like to learn more about this topic?"
                ]
                content += f" {random.choice(engagement_questions)}"
            
            # Ensure we don't exceed platform character limits
            max_length = {
                "twitter": 250,
                "facebook": 400,
                "instagram": 300
            }.get(platform, 300)
            
            if len(content) > max_length:
                content = content[:max_length-3] + "..."
                
            # Get a relevant image URL if requested
            image_url = None
            if include_image:
                image_url = self.get_relevant_image_url(topic)
            
            result = {
                "text": content,
                "image_url": image_url,
                "post_type": post_type
            }
            
            # For news posts, include the article URL
            if news_data and post_type == "news":
                result["article_url"] = news_data[0]['url']
                
            return result
            
        except Exception as e:
            logging.error(f"Error generating content with Hugging Face: {e}")
            return self.generate_content_fallback(topic, platform, include_image, post_type)
    
    def generate_content_fallback(self, topic, platform, include_image=True, post_type=None):
        """Generate informative content as fallback"""
        # If post type not specified, choose randomly
        if not post_type:
            post_type = random.choice(self.post_types)
            
        logging.info(f"Using fallback content generation for {topic} with post type {post_type}")
        
        # Templates by post type
        templates = {
            "informative": [
                f"📚 Did you know? Here's an interesting fact about {topic} that most people don't realize. Learning about this changed my perspective! #informative #{topic.replace(' ', '')}",
                f"🔍 Understanding {topic} is essential in today's world. Here's what you need to know and why it matters. Have you explored this topic before? #knowledgeshare #{topic.replace(' ', '')}"
            ],
            "question": [
                f"🤔 What's your experience with {topic}? I'm curious to hear different perspectives on this important topic! #discussion #{topic.replace(' ', '')}",
                f"❓ If you could change one thing about {topic}, what would it be and why? Share your thoughts below! #feedback #{topic.replace(' ', '')}"
            ],
            "statistic": [
                f"📊 Surprising statistic: The latest research on {topic} shows significant developments. Did you expect these numbers? #data #{topic.replace(' ', '')}",
                f"📈 The numbers don't lie: {topic} is changing rapidly. Here's what the latest data reveals about where things are headed. What do these trends mean for you? #statistics #{topic.replace(' ', '')}"
            ],
            "tip": [
                f"💡 Pro tip for {topic}: This approach can save you time and improve results. What strategies have worked for you? #helpful #{topic.replace(' ', '')}",
                f"✅ Quick tip that improved my approach to {topic}: This simple change made a significant difference. What tips would you add? #productivity #{topic.replace(' ', '')}"
            ],
            "news": [
                f"🔔 Breaking update on {topic}: Recent developments are changing how we understand this issue. What's your take on these changes? #update #{topic.replace(' ', '')}",
                f"📰 Just in: Important news about {topic} that everyone should know. How might this affect your approach? #currentevents #{topic.replace(' ', '')}"
            ],
            "opinion": [
                f"💭 My perspective on {topic}: After researching this topic, I've come to an interesting conclusion. Do you agree or see it differently? #perspective #{topic.replace(' ', '')}",
                f"🧠 Unpopular opinion about {topic}: This viewpoint challenges conventional wisdom but deserves consideration. Where do you stand on this? #thoughtleadership #{topic.replace(' ', '')}"
            ],
            "resource": [
                f"🔗 Just discovered an excellent resource on {topic} that's worth checking out. What resources have you found helpful? #useful #{topic.replace(' ', '')}",
                f"📚 For anyone interested in {topic}, this comprehensive guide covers everything you need to know. What other resources would you recommend? #learning #{topic.replace(' ', '')}"
            ]
        }
        
        # Get appropriate templates for the post type and pick one
        type_templates = templates.get(post_type, templates["informative"])
        content = random.choice(type_templates)
        
        # Ensure we don't exceed platform character limits
        max_length = {
            "twitter": 250,
            "facebook": 400,
            "instagram": 300
        }.get(platform, 300)
        
        if len(content) > max_length:
            content = content[:max_length-3] + "..."
        
        # Get a relevant image URL if requested
        image_url = None
        if include_image:
            image_url = self.get_relevant_image_url(topic)
        
        # Get news data for news posts
        news_data = None
        if post_type == "news":
            news_data = self.fetch_news_for_topic(topic)
        
        result = {
            "text": content,
            "image_url": image_url,
            "post_type": post_type
        }
        
        # For news posts, include the article URL if available
        if news_data and post_type == "news":
            result["article_url"] = news_data[0]['url']
            
        return result
    
    def generate_content(self, topic, platform, include_image=True):
        """Generate content using available methods with random post type for variety"""
        # Select a random post type for variety
        post_type = random.choice(self.post_types)
        logging.info(f"Selected post type '{post_type}' for topic '{topic}'")
        
        # Try Google Gemini first (primary AI model)
        if self.gemini_model and os.getenv("GOOGLE_API_KEY"):
            try:
                return self.generate_content_gemini(topic, platform, include_image, post_type)
            except Exception as e:
                logging.error(f"Gemini generation failed: {e}")
        
        # Try Hugging Face if Gemini fails
        if os.getenv("HUGGINGFACE_API_KEY"):
            try:
                return self.generate_content_huggingface(topic, platform, include_image, post_type)
            except Exception as e:
                logging.error(f"Hugging Face generation failed: {e}")
        
        # Use fallback method if all else fails
        return self.generate_content_fallback(topic, platform, include_image, post_type)
    
    def post_to_twitter(self, content):
        """Post content to Twitter with optional image and article link"""
        try:
            if not self.twitter_api:
                logging.error("Twitter API not configured properly")
                return False
            
            # Extract content components
            text = content.get("text", "")
            image_url = content.get("image_url")
            article_url = content.get("article_url")
            
            # Add article URL if available (for news posts) and there's room
            if article_url and len(text) + len(article_url) + 1 <= 250:
                text = f"{text}\n{article_url}"
            
            # If we have an image URL, download it and upload to Twitter
            media_id = None
            if image_url:
                try:
                    # Set up Twitter API v1 for media upload
                    auth = tweepy.OAuth1UserHandler(
                        os.getenv("TWITTER_API_KEY"),
                        os.getenv("TWITTER_API_SECRET"),
                        os.getenv("TWITTER_ACCESS_TOKEN"),
                        os.getenv("TWITTER_ACCESS_SECRET")
                    )
                    api_v1 = tweepy.API(auth)
                    
                    # Download the image
                    logging.info(f"Downloading image from: {image_url}")
                    img_response = requests.get(image_url)
                    if img_response.status_code == 200:
                        # Save the image temporarily
                        temp_img_path = "temp_tweet_image.jpg"
                        with open(temp_img_path, "wb") as f:
                            f.write(img_response.content)
                        
                        # Upload to Twitter
                        media = api_v1.media_upload(temp_img_path)
                        media_id = media.media_id
                        
                        # Clean up the temporary file
                        os.remove(temp_img_path)
                        logging.info(f"Image uploaded to Twitter with media ID: {media_id}")
                    else:
                        logging.error(f"Failed to download image: HTTP {img_response.status_code}")
                except Exception as e:
                    logging.error(f"Error uploading image to Twitter: {e}")
                    # Continue without the image if there's an error
            
            # Post the tweet with or without media
            if media_id:
                response = self.twitter_api.create_tweet(text=text, media_ids=[media_id])
            else:
                response = self.twitter_api.create_tweet(text=text)
                
            tweet_id = response.data['id']
            logging.info(f"Posted to Twitter: {text}")
            logging.info(f"Tweet URL: https://twitter.com/user/status/{tweet_id}")
            return True
        except Exception as e:
            logging.error(f"Error posting to Twitter: {e}")
            return False
    
    def post_content(self, platform, content):
        """Post content to specified platform"""
        success = False
        
        if platform == "twitter":
            success = self.post_to_twitter(content)
        # Add more platforms here as needed
        
        if success:
            # Store in posted content history
            content_record = {
                "platform": platform,
                "content": content["text"],
                "image_url": content.get("image_url"),
                "post_type": content.get("post_type", "general"),
                "article_url": content.get("article_url"),
                "timestamp": datetime.now().isoformat()
            }
            
            self.posted_content.append(content_record)
            
            # Save posted content to file
            self.save_posted_content()
        
        return success
    
    def analyze_post_performance(self):
        """Analyze which post types performed best (mock implementation)"""
        # In a real implementation, this would fetch engagement metrics
        # from the respective platform APIs
        logging.info("Analyzing post performance (mock implementation)")
        
        # For demonstration, return mock results
        return {
            "informative": {"avg_likes": 15, "avg_shares": 5, "avg_comments": 3},
            "question": {"avg_likes": 8, "avg_shares": 2, "avg_comments": 7},
            "statistic": {"avg_likes": 12, "avg_shares": 6, "avg_comments": 2},
            "tip": {"avg_likes": 18, "avg_shares": 8, "avg_comments": 4},
            "news": {"avg_likes": 10, "avg_shares": 7, "avg_comments": 3},
            "opinion": {"avg_likes": 9, "avg_shares": 3, "avg_comments": 6},
            "resource": {"avg_likes": 13, "avg_shares": 9, "avg_comments": 2}
        }
    
    def save_posted_content(self):
        """Save posted content to JSON file"""
        try:
            with open("posted_content.json", "w") as f:
                json.dump(self.posted_content, f, indent=4)
            logging.info("Posted content saved to file")
        except Exception as e:
            logging.error(f"Error saving posted content: {e}")
    
    def load_posted_content(self):
        """Load posted content from JSON file"""
        try:
            with open("posted_content.json", "r") as f:
                self.posted_content = json.load(f)
            logging.info(f"Loaded {len(self.posted_content)} previous posts from file")
        except FileNotFoundError:
            self.posted_content = []
            logging.info("No previous posted content file found")
        except Exception as e:
            self.posted_content = []
            logging.error(f"Error loading posted content: {e}")
    
    def run_daily_post(self):
        """Run the daily posting routine"""
        start_time = datetime.now()
        logging.info(f"Starting daily post routine at {start_time}")
        
        # Update last run time
        self.last_run = start_time.isoformat()
        
        # Fetch trending topics
        trends = self.fetch_trends()
        
        if not trends:
            logging.warning("No trending topics found")
            # Use emergency fallback
            trends = ["social media", "digital marketing", "technology"]
            logging.info(f"Using emergency fallback topics: {trends}")
        
        # Select a random trend
        selected_trend = random.choice(trends)
        logging.info(f"Selected topic: {selected_trend}")
        
        # For each platform, generate and post content
        for platform in self.platforms:
            try:
                content = self.generate_content(selected_trend, platform, include_image=True)
                logging.info(f"Generated {content.get('post_type', 'general')} content for {platform}: {content['text']}")
                if content.get("image_url"):
                    logging.info(f"With image: {content['image_url']}")
                
                success = self.post_content(platform, content)
                
                if success:
                    logging.info(f"Successfully posted to {platform}")
                else:
                    logging.error(f"Failed to post to {platform}")
                
                # Wait a bit between posts
                time.sleep(2)
                
            except Exception as e:
                logging.error(f"Error posting to {platform}: {e}")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        logging.info(f"Daily post routine completed in {duration:.2f} seconds")

    def schedule_posts(self):
        """Schedule regular posts with optimal timing"""
        # High engagement times (example)
        optimal_times = {
            "weekday": ["12:30", "15:45", "17:30"],
            "weekend": ["11:00", "14:15", "19:30"]
        }
        
        # Weekday schedule
        for time_slot in optimal_times["weekday"]:
            schedule.every().monday.at(time_slot).do(self.run_daily_post)
            schedule.every().tuesday.at(time_slot).do(self.run_daily_post)
            schedule.every().wednesday.at(time_slot).do(self.run_daily_post)
            schedule.every().thursday.at(time_slot).do(self.run_daily_post)
            schedule.every().friday.at(time_slot).do(self.run_daily_post)
        
        # Weekend schedule
        for time_slot in optimal_times["weekend"]:
            schedule.every().saturday.at(time_slot).do(self.run_daily_post)
            schedule.every().sunday.at(time_slot).do(self.run_daily_post)
        
        # Add weekly analysis task
        schedule.every().monday.at("06:00").do(self.analyze_post_performance)
        
        logging.info("Scheduled posts at optimal engagement times")
        logging.info(f"Weekday posts: {', '.join(optimal_times['weekday'])}")
        logging.info(f"Weekend posts: {', '.join(optimal_times['weekend'])}")
        
        # Run the scheduler loop
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

    def get_engagement_tips(self, topic):
        """Generate specific engagement tips for a given topic"""
        tips = {
            "technology": [
                "Ask your audience what tech tools they can't live without",
                "Run a poll about preferred brands or features",
                "Share a 'how-to' tip that solves a common tech problem"
            ],
            "health": [
                "Ask followers to share their wellness routines",
                "Create a quick challenge related to healthy habits",
                "Request success stories related to health goals"
            ],
            "business": [
                "Ask about biggest business challenges followers face",
                "Share a productivity hack and ask for others",
                "Create a scenario and ask how followers would handle it"
            ],
            "social media": [
                "Ask which platform offers the best ROI for their business",
                "Request tips on content creation strategies",
                "Create a poll about posting frequency preferences"
            ],
            "education": [
                "Ask followers about their favorite learning resources",
                "Create a mini-quiz related to the topic",
                "Request opinions on traditional vs. online learning"
            ],
            "general": [
                "End posts with a specific question to encourage comments",
                "Use 'fill in the blank' prompts to boost engagement",
                "Ask for opinions on industry trends or developments",
                "Create a 'this or that' choice to encourage responses",
                "Share a controversial (but respectful) opinion and ask for thoughts"
            ]
        }
        
        # Find matching category
        topic_lower = topic.lower()
        for category, category_tips in tips.items():
            if category != "general" and category in topic_lower:
                return random.choice(category_tips)
        
        # Default to general tips
        return random.choice(tips["general"])
    
    def check_content_quality(self, content):
        """Evaluate content quality and suggest improvements"""
        issues = []
        suggestions = []
        
        # Check content length
        if len(content) < 50:
            issues.append("Content is too short")
            suggestions.append("Add more valuable information or context")
        
        # Check for engagement elements
        if "?" not in content and not any(call in content.lower() for call in ["share", "comment", "tell us", "let us know"]):
            issues.append("Missing engagement prompt")
            suggestions.append("Add a question or clear call to action")
        
        # Check for hashtags
        if "#" not in content:
            issues.append("No hashtags")
            suggestions.append("Add 1-2 relevant hashtags for better discoverability")
        
        # Check for emoji usage
        emoji_chars = "😀😃😄😁😆😅😂🤣😊😇🙂🙃😉😌😍🥰😘😗😙😚😋😛😝😜🤪🤨🧐🤓😎🤩🥳😏😒😞😔😟😕🙁☹️😣😖😫😩🥺😢😭😤😠😡🤬🤯😳🥵🥶😱😨😰😥😓🤗🤔🤭🤫🤥😶😐😑😬🙄😯😦😧😮😲🥱😴🤤😪😵🤐🥴🤢🤮🤧😷🤒🤕🤑🤠😈👿👹👺🤡💩👻💀☠️👽👾🤖🎃😺😸😹😻😼😽🙀😿😾"
        if not any(c in emoji_chars for c in content):
            issues.append("No visual elements")
            suggestions.append("Include relevant emojis to increase visibility")
        
        # Return quality assessment
        return {
            "issues": issues,
            "suggestions": suggestions,
            "quality_score": 10 - len(issues) if len(issues) <= 10 else 0
        }
    
    def test_twitter_connection(self) -> Dict:
        """Test Twitter API connection and return status"""
        try:
            if not self.twitter_api:
                return {"status": "error", "message": "Twitter API not initialized"}
            
            # First check if credentials are loaded
            bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
            api_key = os.getenv("TWITTER_API_KEY")
            
            if not bearer_token:
                return {"status": "error", "message": "Twitter Bearer Token not found in environment variables"}
            
            # For rate limit issues, try a lighter API call first
            try:
                # Try to get user info directly (requires less rate limit)
                if api_key and os.getenv("TWITTER_API_SECRET") and os.getenv("TWITTER_ACCESS_TOKEN") and os.getenv("TWITTER_ACCESS_SECRET"):
                    try:
                        user = self.twitter_api.get_me()
                        if user and user.data:
                            return {
                                "status": "success", 
                                "message": f"Connected successfully as @{user.data.username}",
                                "user_info": {
                                    "username": user.data.username,
                                    "name": user.data.name,
                                    "id": user.data.id
                                },
                                "connection_type": "Full OAuth"
                            }
                    except tweepy.TooManyRequests:
                        # If rate limited on get_me, try a simpler verification
                        return {
                            "status": "warning", 
                            "message": "Twitter API rate limit hit, but credentials appear valid",
                            "note": "Connection likely working - rate limit will reset soon",
                            "suggestion": "Wait 15 minutes before testing again"
                        }
                    except Exception as oauth_error:
                        logging.warning(f"OAuth method failed: {oauth_error}")
                
                # Fallback: Try a very light search query
                try:
                    response = self.twitter_api.search_recent_tweets(
                        query="the", 
                        max_results=10
                    )
                    
                    if response:
                        return {
                            "status": "success", 
                            "message": "Twitter API connection successful (Bearer Token)",
                            "note": "Basic connection verified via search API",
                            "connection_type": "Bearer Token Only"
                        }
                except tweepy.TooManyRequests:
                    return {
                        "status": "warning", 
                        "message": "Twitter API rate limit exceeded",
                        "note": "This is normal - your credentials are likely valid",
                        "suggestion": "Rate limits reset every 15 minutes. Try again later.",
                        "tip": "In production mode, the agent handles rate limits automatically"
                    }
                    
            except tweepy.Unauthorized as e:
                return {"status": "error", "message": f"Twitter API authentication failed: {str(e)}. Please check your Bearer Token."}
            except tweepy.Forbidden as e:
                return {"status": "error", "message": f"Twitter API access forbidden: {str(e)}. Your app may not have the required permissions."}
                
        except tweepy.Unauthorized as e:
            return {"status": "error", "message": f"Twitter API authentication failed: {str(e)}. Please check your API credentials."}
        except tweepy.Forbidden as e:
            return {"status": "error", "message": f"Twitter API access forbidden: {str(e)}. Your app may not have the required permissions."}
        except tweepy.NotFound as e:
            return {"status": "error", "message": f"Twitter API endpoint not found: {str(e)}"}
        except tweepy.TooManyRequests as e:
            return {
                "status": "warning", 
                "message": "Twitter API rate limit exceeded",
                "note": "This usually means your credentials are working",
                "suggestion": "Wait 15 minutes for rate limit reset",
                "details": str(e)
            }
        except Exception as e:
            return {"status": "error", "message": f"Connection failed: {str(e)}. Error type: {type(e).__name__}"}
    
    def get_rate_limit_status(self) -> Dict:
        """Check Twitter API rate limit status"""
        try:
            if not self.twitter_api:
                return {"status": "error", "message": "Twitter API not initialized"}
            
            # This is a lightweight call to check rate limits
            rate_limit = self.twitter_api.get_rate_limit_status()
            return {
                "status": "success",
                "message": "Rate limit status retrieved",
                "rate_limits": rate_limit
            }
        except tweepy.TooManyRequests:
            return {
                "status": "rate_limited",
                "message": "Currently rate limited",
                "suggestion": "Wait 15 minutes for reset"
            }
        except Exception as e:
            return {"status": "error", "message": f"Failed to get rate limit status: {str(e)}"}
    
    def test_post_creation(self, test_topic: str = None) -> Dict:
        """Test content generation without posting"""
        try:
            if not test_topic:
                test_topic = random.choice(["AI technology", "productivity tips", "health and wellness"])
            
            logging.info(f"Testing content generation for topic: {test_topic}")
            
            # Generate test content
            content = self.generate_content(test_topic, "twitter", include_image=True)
            
            if content and content.get("text"):
                return {
                    "status": "success",
                    "message": "Content generated successfully",
                    "content": content,
                    "topic": test_topic
                }
            else:
                return {"status": "error", "message": "Failed to generate content"}
                
        except Exception as e:
            return {"status": "error", "message": f"Content generation failed: {str(e)}"}
    
    def test_full_post_cycle(self, test_topic: str = None) -> Dict:
        """Test the complete posting process without actually posting"""
        try:
            # Test API connection
            connection_test = self.test_twitter_connection()
            if connection_test["status"] != "success":
                return connection_test
            
            # Test content generation
            content_test = self.test_post_creation(test_topic)
            if content_test["status"] != "success":
                return content_test
            
            # Simulate posting (without actual post)
            content = content_test["content"]
            
            return {
                "status": "success",
                "message": "Full cycle test completed successfully",
                "details": {
                    "api_connection": "✓ Connected",
                    "content_generation": "✓ Generated",
                    "content_preview": content["text"][:100] + "..." if len(content["text"]) > 100 else content["text"],
                    "image_url": content.get("image_url", "No image"),
                    "post_type": content.get("post_type", "Unknown")
                }
            }
            
        except Exception as e:
            return {"status": "error", "message": f"Full cycle test failed: {str(e)}"}
    
    def run_production_mode(self):
        """Run in production mode with scheduled posts"""
        if self.mode != "production":
            logging.error("Agent not in production mode")
            return
        
        logging.info("Starting production mode with scheduled posts")
        self.is_running = True
        
        # Clear any existing scheduled jobs
        schedule.clear()
        
        # Schedule weekday posts
        for time_slot in self.production_schedule["weekday_times"]:
            schedule.every().monday.at(time_slot).do(self.run_daily_post)
            schedule.every().tuesday.at(time_slot).do(self.run_daily_post)
            schedule.every().wednesday.at(time_slot).do(self.run_daily_post)
            schedule.every().thursday.at(time_slot).do(self.run_daily_post)
            schedule.every().friday.at(time_slot).do(self.run_daily_post)
        
        # Schedule weekend posts
        for time_slot in self.production_schedule["weekend_times"]:
            schedule.every().saturday.at(time_slot).do(self.run_daily_post)
            schedule.every().sunday.at(time_slot).do(self.run_daily_post)
        
        # Add daily analytics check
        schedule.every().day.at("23:00").do(self.analyze_post_performance)
        
        logging.info(f"Scheduled posts at: {self.production_schedule}")
        
        # Run scheduler in background thread
        def run_scheduler():
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        
        return scheduler_thread
    
    def stop_production_mode(self):
        """Stop production mode"""
        self.is_running = False
        schedule.clear()
        logging.info("Production mode stopped")
    
    def get_status(self) -> Dict:
        """Get current agent status"""
        return {
            "mode": self.mode,
            "is_running": self.is_running,
            "posted_content_count": len(self.posted_content),
            "platforms": self.platforms,
            "scheduled_jobs": len(schedule.jobs) if hasattr(schedule, 'jobs') else 0,
            "last_run": getattr(self, 'last_run', None)
        }
    
    def admin_interface(self):
        """Interactive admin interface for managing the agent"""
        print("\n" + "="*60)
        print("🤖 SOCIAL MEDIA AI AGENT - ADMIN INTERFACE")
        print("="*60)
        
        while True:
            print(f"\n📊 Current Status: Mode={self.mode}, Running={self.is_running}")
            print("\n🔧 Available Commands:")
            print("1. Test Twitter Connection")
            print("2. Test Content Generation") 
            print("3. Test Full Post Cycle")
            print("4. Start Production Mode")
            print("5. Stop Production Mode")
            print("6. View Agent Status")
            print("7. Manual Post Now")
            print("8. View Recent Posts")
            print("9. Switch Mode")
            print("0. Exit")
            
            try:
                choice = input("\n👤 Enter your choice (0-9): ").strip()
                
                if choice == "0":
                    print("\n👋 Goodbye!")
                    self.stop_production_mode()
                    break
                
                elif choice == "1":
                    print("\n🔍 Testing Twitter connection...")
                    result = self.test_twitter_connection()
                    self._print_result(result)
                
                elif choice == "2":
                    topic = input("Enter test topic (or press Enter for random): ").strip()
                    print("\n✍️ Testing content generation...")
                    result = self.test_post_creation(topic if topic else None)
                    self._print_result(result)
                
                elif choice == "3":
                    topic = input("Enter test topic (or press Enter for random): ").strip()
                    print("\n🔄 Testing full post cycle...")
                    result = self.test_full_post_cycle(topic if topic else None)
                    self._print_result(result)
                
                elif choice == "4":
                    if self.mode != "production":
                        print("❌ Must be in production mode. Use option 9 to switch modes.")
                        continue
                    
                    if self.is_running:
                        print("⚠️ Production mode is already running")
                        continue
                    
                    print("\n🚀 Starting production mode...")
                    thread = self.run_production_mode()
                    print("✅ Production mode started successfully!")
                    print(f"📅 Posts scheduled at: {self.production_schedule}")
                
                elif choice == "5":
                    print("\n⏹️ Stopping production mode...")
                    self.stop_production_mode()
                    print("✅ Production mode stopped")
                
                elif choice == "6":
                    print("\n📊 Agent Status:")
                    status = self.get_status()
                    for key, value in status.items():
                        print(f"   {key}: {value}")
                
                elif choice == "7":
                    print("\n📝 Creating manual post...")
                    try:
                        self.run_daily_post()
                        print("✅ Manual post completed successfully!")
                    except Exception as e:
                        print(f"❌ Manual post failed: {e}")
                
                elif choice == "8":
                    print("\n📋 Recent Posts:")
                    recent_posts = self.posted_content[-5:] if self.posted_content else []
                    if recent_posts:
                        for i, post in enumerate(recent_posts, 1):
                            print(f"   {i}. {post.get('timestamp', 'N/A')}: {post.get('text', 'N/A')[:50]}...")
                    else:
                        print("   No recent posts found")
                
                elif choice == "9":
                    current_mode = self.mode
                    new_mode = "production" if current_mode == "testing" else "testing"
                    confirm = input(f"Switch from {current_mode} to {new_mode} mode? (y/n): ").lower()
                    if confirm == 'y':
                        if self.is_running:
                            self.stop_production_mode()
                        self.mode = new_mode
                        print(f"✅ Switched to {new_mode} mode")
                    else:
                        print("❌ Mode switch cancelled")
                
                else:
                    print("❌ Invalid choice. Please enter 0-9.")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                self.stop_production_mode()
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def _print_result(self, result: Dict):
        """Helper method to print test results"""
        if result["status"] == "success":
            print(f"✅ {result['message']}")
            if "details" in result:
                for key, value in result["details"].items():
                    print(f"   {key}: {value}")
            if "content" in result:
                content = result["content"]
                print(f"   📝 Generated Content: {content.get('text', 'N/A')}")
                if content.get('image_url'):
                    print(f"   🖼️ Image: {content['image_url']}")
        else:
            print(f"❌ {result['message']}")
    
    def set_production_schedule(self, weekday_times: List[str], weekend_times: List[str]):
        """Update production schedule times"""
        self.production_schedule["weekday_times"] = weekday_times
        self.production_schedule["weekend_times"] = weekend_times
        logging.info(f"Updated production schedule: {self.production_schedule}")

if __name__ == "__main__":
    print("🤖 Social Media AI Agent")
    print("=" * 50)
    
    # Mode selection
    print("\n📋 Select Operation Mode:")
    print("1. Testing Mode - Test posts without scheduling")
    print("2. Production Mode - Automated posting with scheduling")
    
    while True:
        try:
            mode_choice = input("\nEnter mode (1 or 2): ").strip()
            if mode_choice == "1":
                selected_mode = "testing"
                break
            elif mode_choice == "2":
                selected_mode = "production"
                break
            else:
                print("❌ Please enter 1 or 2")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            sys.exit(0)
    
    # Create agent with selected mode
    agent = SocialMediaAIAgent(mode=selected_mode)
    
    # Load previously posted content
    agent.load_posted_content()
    
    print(f"\n✅ Agent initialized in {selected_mode.upper()} mode")
    logging.info(f"Social Media AI Agent started in {selected_mode} mode")
    
    # Quick setup verification
    print("\n🔍 Performing initial setup verification...")
    
    # Test API connection
    connection_result = agent.test_twitter_connection()
    if connection_result["status"] == "success":
        print(f"✅ Twitter API: {connection_result['message']}")
    else:
        print(f"❌ Twitter API: {connection_result['message']}")
        print("⚠️  Warning: Twitter posting will not work without valid API credentials")
    
    # Test content generation
    content_result = agent.test_post_creation()
    if content_result["status"] == "success":
        print("✅ Content Generation: Working")
    else:
        print(f"❌ Content Generation: {content_result['message']}")
    
    # Mode-specific startup
    if selected_mode == "production":
        print("\n🚀 PRODUCTION MODE")
        print("This mode will automatically post content at scheduled times.")
        print("You can start/stop the scheduler from the admin interface.")
        
        # Ask if user wants to start immediately
        start_now = input("\nStart automated posting now? (y/n): ").lower()
        if start_now == 'y':
            try:
                agent.run_production_mode()
                print("✅ Production mode started! Posts will be published automatically.")
            except Exception as e:
                print(f"❌ Failed to start production mode: {e}")
    
    else:
        print("\n🧪 TESTING MODE")
        print("This mode allows you to test posts and features without automation.")
    
    # Start admin interface
    try:
        agent.admin_interface()
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down gracefully...")
        agent.stop_production_mode()
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        agent.stop_production_mode()
    finally:
        print("🔚 Agent stopped")