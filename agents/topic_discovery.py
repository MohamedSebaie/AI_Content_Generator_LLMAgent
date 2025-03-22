import logging
import json
import re
from typing import List, Dict, Any
from utils.web_scraper import WebScraper
from utils.bedrock_client import BedrockClient
from utils.prompt_templates import TREND_DISCOVERY_PROMPT

logger = logging.getLogger(__name__)

class TopicDiscoveryAgent:
    def __init__(self):
        self.claude_client = BedrockClient()
        self.web_scraper = WebScraper()
    
    def discover_trending_topics(self) -> List[Dict[str, Any]]:
        """
        Discover trending AI topics by combining web search and LLM analysis.
        """
        try:
            # Get initial search results for AI trends
            search_results = self.web_scraper.search_google("latest artificial intelligence trends 2025", 10)
            
            # Collect context from search results
            context = ""
            for result in search_results[:5]:
                if 'link' in result:
                    content = self.web_scraper.fetch_page_content(result['link'])
                    context += f"\nSource: {result['title']}\n{content[:1000]}\n"
            
            # Use Claude to analyze trends
            system_prompt = "You are an AI trend analyst specialized in identifying emerging topics."
            user_message = f"{TREND_DISCOVERY_PROMPT}\n\nUse the following search results to inform your analysis:\n{context}"
            
            response = self.claude_client.generate_text(system_prompt, user_message)
            logger.info(f"Claude Response: {response}")
            
            # Parse the JSON response
            try:
                # Extract JSON using regex to find JSON object
                json_match = re.search(r'({[\s\S]*})', response)
                if json_match:
                    json_str = json_match.group(1)
                    topics_data = json.loads(json_str)
                    
                    # Handle different possible JSON structures with case-insensitive keys
                    topics_list = None
                    
                    # Try different possible key names for the topics list
                    for key in ["TrendingAITopics", "trendingAITopics", "Topics", "topics", "trendingTopics"]:
                        if key in topics_data:
                            topics_list = topics_data[key]
                            break
                    
                    # If we found a list of topics, normalize the field names
                    if topics_list and isinstance(topics_list, list):
                        normalized_topics = []
                        for topic in topics_list:
                            normalized_topic = {}
                            
                            # Handle different possible field names with case insensitivity
                            for key, value in topic.items():
                                key_lower = key.lower()
                                if key_lower == "title":
                                    normalized_topic["title"] = value
                                elif key_lower == "description":
                                    normalized_topic["description"] = value
                                elif key_lower in ["trendingreason", "why_trending", "why trending", "whytrending", "importance"]:
                                    normalized_topic["why_trending"] = value
                                elif key_lower == "keywords":
                                    normalized_topic["keywords"] = value
                            
                            if "title" in normalized_topic:  # Only add if we have at least a title
                                normalized_topics.append(normalized_topic)
                        
                        if normalized_topics:
                            return normalized_topics
                    
                    # If we couldn't find a list structure, check if the top-level is a list
                    if isinstance(topics_data, list):
                        normalized_topics = []
                        for topic in topics_data:
                            normalized_topic = {}
                            
                            for key, value in topic.items():
                                key_lower = key.lower()
                                if key_lower == "title":
                                    normalized_topic["title"] = value
                                elif key_lower == "description":
                                    normalized_topic["description"] = value
                                elif key_lower in ["trendingreason", "why_trending", "why trending", "whytrending", "importance"]:
                                    normalized_topic["why_trending"] = value
                                elif key_lower == "keywords":
                                    normalized_topic["keywords"] = value
                            
                            if "title" in normalized_topic:
                                normalized_topics.append(normalized_topic)
                        
                        if normalized_topics:
                            return normalized_topics
                
                # If JSON parsing didn't work, try to extract using regex
                if not json_match:
                    # Look for structured data in the response using regex
                    topics = []
                    
                    # Match patterns for topic entries
                    topic_pattern = r'(?:Topic|[0-9]+[\.:\)])\s*(?:AI\s*)?(.*?)[\r\n]'
                    title_pattern = r'Title:?\s*(.*?)[\r\n]'
                    description_pattern = r'Description:?\s*(.*?)[\r\n]'
                    trending_pattern = r'(?:Why trending|Trending Reason|TrendingReason|Importance):?\s*(.*?)[\r\n]'
                    keywords_pattern = r'Keywords:?\s*(.*?)[\r\n]'
                    
                    # Try to find topics by Title: pattern first
                    title_matches = re.finditer(title_pattern, response)
                    for match in title_matches:
                        title = match.group(1).strip()
                        # Get context around this title
                        start_pos = max(0, match.start() - 50)
                        end_pos = min(len(response), match.end() + 500)
                        context_block = response[start_pos:end_pos]
                        
                        # Extract other fields
                        desc_match = re.search(description_pattern, context_block)
                        trending_match = re.search(trending_pattern, context_block)
                        keywords_match = re.search(keywords_pattern, context_block)
                        
                        description = desc_match.group(1).strip() if desc_match else ""
                        why_trending = trending_match.group(1).strip() if trending_match else ""
                        
                        keywords = []
                        if keywords_match:
                            # Handle both comma-separated lists and array notations
                            keywords_text = keywords_match.group(1).strip()
                            if '[' in keywords_text and ']' in keywords_text:
                                # Handle array notation
                                keywords_text = keywords_text.replace('[', '').replace(']', '')
                                keywords = [k.strip().strip('"\'') for k in keywords_text.split(',')]
                            else:
                                # Handle comma separated list
                                keywords = [k.strip().strip('"\'') for k in keywords_text.split(',')]
                        
                        topics.append({
                            "title": title,
                            "description": description,
                            "why_trending": why_trending,
                            "keywords": keywords
                        })
                    
                    if topics:
                        return topics
                    
                    # If no structured topics found with Title pattern, try numbered list approach
                    if not topics:
                        # Try to extract topics assuming they're in a numbered list
                        lines = response.split('\n')
                        current_topic = {}
                        
                        for line in lines:
                            line = line.strip()
                            # Check if this line starts a new numbered item
                            if re.match(r'^[0-9]+[\.\)]', line):
                                # Save previous topic if it exists
                                if current_topic and "title" in current_topic:
                                    topics.append(current_topic)
                                
                                # Extract title from this line
                                title = re.sub(r'^[0-9]+[\.\)]\s*', '', line).strip()
                                current_topic = {"title": title}
                            # Try to identify description, why trending, and keywords lines
                            elif "description:" in line.lower() and current_topic:
                                current_topic["description"] = line.split(":", 1)[1].strip()
                            elif "why trending:" in line.lower() and current_topic:
                                current_topic["why_trending"] = line.split(":", 1)[1].strip()
                            elif "trending reason:" in line.lower() and current_topic:
                                current_topic["why_trending"] = line.split(":", 1)[1].strip()
                            elif "importance:" in line.lower() and current_topic:
                                current_topic["why_trending"] = line.split(":", 1)[1].strip()
                            elif "keywords:" in line.lower() and current_topic:
                                keywords_text = line.split(":", 1)[1].strip()
                                current_topic["keywords"] = [k.strip().strip('"\'') for k in keywords_text.split(',')]
                        
                        # Add the last topic if it exists
                        if current_topic and "title" in current_topic:
                            topics.append(current_topic)
                        
                        if topics:
                            return topics
                
                # If all parsing methods fail, use the fallback
                raise ValueError("Could not parse topics from response")
                    
            except Exception as e:
                logger.error(f"Error parsing topics: {str(e)}")
                # Use the fallback topics from Claude's actual response
                return [
                    {
                        "title": "Multimodal AI Agents",
                        "description": "AI systems that can understand and generate different data modalities like text, images, and audio. They act as interactive virtual assistants.",
                        "why_trending": "Recent releases like Anthropic's Claude and Google's Bard have popularized AI agents that can handle multimodal inputs and outputs.",
                        "keywords": ["AIAgents", "Multimodal", "VirtualAssistants", "NaturalLanguageProcessing", "ComputerVision"]
                    },
                    {
                        "title": "Generative AI for Video",
                        "description": "AI models that can generate realistic video footage from text descriptions or existing images/videos.",
                        "why_trending": "Major tech companies like OpenAI, Google, and Meta have released powerful video generation models, enabling new creative possibilities.",
                        "keywords": ["GenerativeAI", "VideoGeneration", "DeepLearning", "ComputerVision", "SyntheticMedia"]
                    },
                    {
                        "title": "AI for Climate Change",
                        "description": "Applying AI techniques to tackle environmental challenges like carbon emissions, extreme weather prediction, and sustainable energy solutions.",
                        "why_trending": "With the urgency of climate change, there is growing interest in leveraging AI's potential to develop mitigation and adaptation strategies.",
                        "keywords": ["AIforGood", "ClimateChange", "SustainableDevelopment", "GreenAI", "EnvironmentalAI"]
                    },
                    {
                        "title": "Responsible AI Governance",
                        "description": "Frameworks and best practices to ensure AI systems are developed and deployed ethically, securely, and with accountability.",
                        "why_trending": "As AI becomes more prevalent, there are increasing concerns around privacy, fairness, transparency, and AI's societal impact.",
                        "keywords": ["AIEthics", "TrustedAI", "AIGovernance", "ResponsibleAI", "AIRisks"]
                    },
                    {
                        "title": "AI-Powered Healthcare",
                        "description": "Using AI to improve disease diagnosis, drug discovery, personalized treatment plans, and overall healthcare delivery.",
                        "why_trending": "AI shows immense potential in healthcare, from analyzing medical images to predicting disease outbreaks and optimizing hospital operations.",
                        "keywords": ["AIinHealthcare", "PrecisionMedicine", "DrugDiscovery", "MedicalImaging", "DigitalHealth"]
                    }
                ]
                    
        except Exception as e:
            logger.error(f"Error discovering trending topics: {str(e)}")
            # Return the fallback topics
            return [
                {
                    "title": "Multimodal AI Agents",
                    "description": "AI systems that can understand and generate different data modalities like text, images, and audio. They act as interactive virtual assistants.",
                    "why_trending": "Recent releases like Anthropic's Claude and Google's Bard have popularized AI agents that can handle multimodal inputs and outputs.",
                    "keywords": ["AIAgents", "Multimodal", "VirtualAssistants", "NaturalLanguageProcessing", "ComputerVision"]
                },
                {
                    "title": "Generative AI for Video",
                    "description": "AI models that can generate realistic video footage from text descriptions or existing images/videos.",
                    "why_trending": "Major tech companies like OpenAI, Google, and Meta have released powerful video generation models, enabling new creative possibilities.",
                    "keywords": ["GenerativeAI", "VideoGeneration", "DeepLearning", "ComputerVision", "SyntheticMedia"]
                },
                {
                    "title": "AI for Climate Change",
                    "description": "Applying AI techniques to tackle environmental challenges like carbon emissions, extreme weather prediction, and sustainable energy solutions.",
                    "why_trending": "With the urgency of climate change, there is growing interest in leveraging AI's potential to develop mitigation and adaptation strategies.",
                    "keywords": ["AIforGood", "ClimateChange", "SustainableDevelopment", "GreenAI", "EnvironmentalAI"]
                },
                {
                    "title": "Responsible AI Governance",
                    "description": "Frameworks and best practices to ensure AI systems are developed and deployed ethically, securely, and with accountability.",
                    "why_trending": "As AI becomes more prevalent, there are increasing concerns around privacy, fairness, transparency, and AI's societal impact.",
                    "keywords": ["AIEthics", "TrustedAI", "AIGovernance", "ResponsibleAI", "AIRisks"]
                },
                {
                    "title": "AI-Powered Healthcare",
                    "description": "Using AI to improve disease diagnosis, drug discovery, personalized treatment plans, and overall healthcare delivery.",
                    "why_trending": "AI shows immense potential in healthcare, from analyzing medical images to predicting disease outbreaks and optimizing hospital operations.",
                    "keywords": ["AIinHealthcare", "PrecisionMedicine", "DrugDiscovery", "MedicalImaging", "DigitalHealth"]
                }
            ]
    
    def get_detailed_research(self, topic: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get detailed research about a specific topic.
        """
        title = topic.get("title", "")
        keywords = topic.get("keywords", [])
        keywords_str = ", ".join(keywords) if isinstance(keywords, list) else keywords
        
        research_data = self.web_scraper.research_topic(f"{title} {keywords_str}")
        return {
            "topic": topic,
            "research_data": research_data
        }
    
    def human_topic_selection(self, topics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Present topics to the user and let them select one.
        This is a placeholder for the actual human-in-the-loop implementation.
        In a real application, this would involve a UI interaction.
        """
        print("\nDiscovered Trending AI Topics:\n")
        
        for i, topic in enumerate(topics):
            print(f"{i+1}. {topic.get('title', 'Unnamed Topic')}")
            print(f"   Description: {topic.get('description', 'No description')}")
            print(f"   Why trending: {topic.get('why_trending', 'No information')}")
            print(f"   Keywords: {', '.join(topic.get('keywords', []))}")
            print()
        
        while True:
            try:
                choice = int(input("Select a topic by number (1-5): "))
                if 1 <= choice <= len(topics):
                    selected_topic = topics[choice-1]
                    print(f"\nYou selected: {selected_topic.get('title')}\n")
                    return selected_topic
                else:
                    print(f"Please enter a number between 1 and {len(topics)}")
            except ValueError:
                print("Please enter a valid number")