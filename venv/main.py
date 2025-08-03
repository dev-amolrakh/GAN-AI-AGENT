#!/usr/bin/env python3
"""
Enhanced Social Media AI Agent with Menu Interface
This version includes proper error handling and a user-friendly menu system.
"""

import os
import json
import random
import time
import threading
from datetime import datetime
from app import SocialMediaAIAgent

class SocialMediaManager:
    def __init__(self):
        self.agent = None
        self.mode = "testing"  # testing or production
        self.running = False
        self.scheduler_thread = None
        
    def initialize_agent(self):
        """Initialize the Social Media AI Agent"""
        try:
            print("🔄 Initializing Social Media AI Agent...")
            self.agent = SocialMediaAIAgent()
            self.agent.load_posted_content()
            print("✅ Agent initialized successfully!")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize agent: {e}")
            return False
    
    def test_twitter_connection(self):
        """Test Twitter API connection"""
        print("\n🔍 Testing Twitter connection...")
        
        if not self.agent:
            print("❌ Agent not initialized. Please initialize first.")
            return
            
        try:
            result = self.agent.test_twitter_connection()
            
            if result["status"] == "success":
                print("✅ Connection successful!")
                print(f"   {result['message']}")
                if "user_info" in result:
                    user_info = result["user_info"]
                    print(f"   Username: @{user_info['username']}")
                    print(f"   Name: {user_info['name']}")
                    if "followers" in user_info:
                        print(f"   Followers: {user_info['followers']}")
                if "connection_type" in result:
                    print(f"   Connection Type: {result['connection_type']}")
                if "note" in result:
                    print(f"   📝 Note: {result['note']}")
                    
            elif result["status"] == "warning":
                print("⚠️  Rate limit reached (but connection likely working)")
                print(f"   {result['message']}")
                if "note" in result:
                    print(f"   📝 {result['note']}")
                if "suggestion" in result:
                    print(f"   💡 Suggestion: {result['suggestion']}")
                if "tip" in result:
                    print(f"   💡 Tip: {result['tip']}")
                    
            else:
                print("❌ Connection failed!")
                print(f"   Error: {result['message']}")
                if "suggestion" in result:
                    print(f"   💡 Suggestion: {result['suggestion']}")
                
        except Exception as e:
            print(f"❌ Connection failed: {e}")
    
    def test_content_generation(self):
        """Test content generation"""
        print("\n🔄 Testing content generation...")
        
        if not self.agent:
            print("❌ Agent not initialized.")
            return
            
        try:
            # Test with a sample topic
            test_topic = "artificial intelligence"
            print(f"   Generating content for topic: '{test_topic}'")
            
            content = self.agent.generate_content(test_topic, "twitter", include_image=True)
            
            print("✅ Content generation successful!")
            print(f"   Text: {content['text']}")
            print(f"   Post Type: {content.get('post_type', 'N/A')}")
            if content.get("image_url"):
                print(f"   Image: {content['image_url']}")
                
        except Exception as e:
            print(f"❌ Content generation failed: {e}")
    
    def test_full_post_cycle(self):
        """Test the full posting cycle without actually posting"""
        print("\n🔄 Testing full post cycle (simulation)...")
        
        if not self.agent:
            print("❌ Agent not initialized.")
            return
            
        try:
            # Fetch trends
            print("   Step 1: Fetching trending topics...")
            trends = self.agent.fetch_trends()
            if trends:
                print(f"   ✅ Found {len(trends)} trending topics")
                print(f"   Topics: {', '.join(trends[:3])}...")
            else:
                print("   ⚠️ No trends found, using fallback topics")
                trends = self.agent.get_fallback_topics()
            
            # Select a topic
            selected_topic = random.choice(trends)
            print(f"   Step 2: Selected topic: '{selected_topic}'")
            
            # Generate content
            print("   Step 3: Generating content...")
            content = self.agent.generate_content(selected_topic, "twitter", include_image=True)
            
            print("   ✅ Full cycle test successful!")
            print(f"   Generated content: {content['text']}")
            print(f"   Post type: {content.get('post_type', 'N/A')}")
            
        except Exception as e:
            print(f"❌ Full cycle test failed: {e}")
    
    def start_production_mode(self):
        """Start production mode with scheduled posting"""
        if not self.agent:
            print("❌ Agent not initialized.")
            return
            
        if self.running:
            print("⚠️ Production mode is already running.")
            return
            
        print("\n🚀 Starting production mode...")
        self.mode = "production"
        self.running = True
        
        # Start scheduler in a separate thread
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        print("✅ Production mode started!")
        print("   Posts will be scheduled according to optimal timing.")
        print("   Use 'Stop Production Mode' to halt scheduled posting.")
    
    def stop_production_mode(self):
        """Stop production mode"""
        if not self.running:
            print("⚠️ Production mode is not running.")
            return
            
        print("\n🛑 Stopping production mode...")
        self.running = False
        self.mode = "testing"
        
        print("✅ Production mode stopped!")
    
    def _run_scheduler(self):
        """Run the scheduler in production mode"""
        import schedule
        
        # Schedule posts at optimal times
        optimal_times = ["12:30", "15:45", "17:30"]
        
        for time_slot in optimal_times:
            schedule.every().day.at(time_slot).do(self._scheduled_post)
        
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def _scheduled_post(self):
        """Execute a scheduled post"""
        if self.running and self.agent:
            try:
                self.agent.run_daily_post()
            except Exception as e:
                print(f"❌ Scheduled post failed: {e}")
    
    def manual_post_now(self):
        """Make a manual post immediately"""
        print("\n📝 Creating manual post...")
        
        if not self.agent:
            print("❌ Agent not initialized.")
            return
            
        try:
            # Test connection first
            connection_test = self.agent.test_twitter_connection()
            if connection_test["status"] != "success":
                print(f"❌ Cannot post: {connection_test['message']}")
                return
            
            # Get user confirmation
            confirm = input("   Are you sure you want to post now? (y/n): ").lower()
            if confirm != 'y':
                print("   Post cancelled.")
                return
            
            # Execute the post
            self.agent.run_daily_post()
            print("✅ Manual post completed!")
            
        except Exception as e:
            print(f"❌ Manual post failed: {e}")
    
    def view_recent_posts(self):
        """View recent posts"""
        print("\n📋 Recent Posts:")
        
        if not self.agent:
            print("❌ Agent not initialized.")
            return
            
        try:
            posts = self.agent.posted_content[-10:]  # Last 10 posts
            
            if not posts:
                print("   No posts found.")
                return
            
            for i, post in enumerate(reversed(posts), 1):
                timestamp = post.get('timestamp', 'Unknown')
                platform = post.get('platform', 'Unknown')
                post_type = post.get('post_type', 'Unknown')
                content = post.get('content', 'No content')[:100]
                
                print(f"   {i}. [{timestamp}] {platform} ({post_type})")
                print(f"      {content}{'...' if len(post.get('content', '')) > 100 else ''}")
                print()
                
        except Exception as e:
            print(f"❌ Error retrieving posts: {e}")
    
    def switch_mode(self):
        """Switch between testing and production modes"""
        if self.running:
            print("⚠️ Cannot switch modes while production mode is running.")
            print("   Please stop production mode first.")
            return
            
        current_mode = self.mode
        new_mode = "production" if current_mode == "testing" else "testing"
        
        self.mode = new_mode
        print(f"✅ Switched from {current_mode} to {new_mode} mode.")
    
    def get_status(self):
        """Get current agent status"""
        agent_status = "Initialized" if self.agent else "Not initialized"
        twitter_status = "Unknown"
        
        if self.agent:
            try:
                result = self.agent.test_twitter_connection()
                twitter_status = "Connected" if result["status"] == "success" else "Disconnected"
            except:
                twitter_status = "Error"
        
        return {
            "agent": agent_status,
            "twitter": twitter_status,
            "mode": self.mode,
            "running": self.running
        }
    
    def show_menu(self):
        """Display the main menu"""
        status = self.get_status()
        
        print("\n" + "="*50)
        print("🤖 Social Media AI Agent - Control Panel")
        print("="*50)
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
        
        print(f"\n📊 Current Status: Mode={status['mode']}, Running={status['running']}")
        print(f"   Agent: {status['agent']}, Twitter: {status['twitter']}")
    
    def run(self):
        """Run the main application loop"""
        print("🚀 Social Media AI Agent Manager")
        print("Initializing...")
        
        # Initialize agent
        if not self.initialize_agent():
            print("❌ Failed to initialize. Exiting.")
            return
        
        # Main loop
        while True:
            try:
                self.show_menu()
                choice = input("\n👤 Enter your choice (0-9): ").strip()
                
                if choice == "0":
                    if self.running:
                        print("🛑 Stopping production mode before exit...")
                        self.stop_production_mode()
                    print("👋 Goodbye!")
                    break
                elif choice == "1":
                    self.test_twitter_connection()
                elif choice == "2":
                    self.test_content_generation()
                elif choice == "3":
                    self.test_full_post_cycle()
                elif choice == "4":
                    self.start_production_mode()
                elif choice == "5":
                    self.stop_production_mode()
                elif choice == "6":
                    status = self.get_status()
                    print(f"\n📊 Agent Status:")
                    print(f"   Agent: {status['agent']}")
                    print(f"   Twitter: {status['twitter']}")
                    print(f"   Mode: {status['mode']}")
                    print(f"   Running: {status['running']}")
                elif choice == "7":
                    self.manual_post_now()
                elif choice == "8":
                    self.view_recent_posts()
                elif choice == "9":
                    self.switch_mode()
                else:
                    print("❌ Invalid choice. Please enter a number between 0-9.")
                
                # Pause before showing menu again
                input("\nPress Enter to continue...")
                
            except KeyboardInterrupt:
                print("\n\n🛑 Interrupted by user.")
                if self.running:
                    self.stop_production_mode()
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {e}")
                input("Press Enter to continue...")

if __name__ == "__main__":
    manager = SocialMediaManager()
    manager.run()
