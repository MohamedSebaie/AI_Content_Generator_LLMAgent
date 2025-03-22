import logging
from typing import Dict, Any
from utils.bedrock_client import BedrockClient
from utils.prompt_templates import CONTENT_GENERATION_PROMPT
from config import TEMPERATURE, MAX_TOKENS

logger = logging.getLogger(__name__)

class ContentGeneratorAgent:
    def __init__(self):
        self.claude_client = BedrockClient()
    
    def generate_content(self, topic_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a blog post based on the provided topic data.
        """
        try:
            topic = topic_data.get("topic", {})
            research_data = topic_data.get("research_data", {})
            
            topic_title = topic.get("title", "AI Technology")
            
            # Extract keywords
            keywords = topic.get("keywords", [])
            if isinstance(keywords, list):
                keywords_str = ", ".join(keywords)
            else:
                keywords_str = str(keywords)
            
            # Prepare context from research
            context = ""
            if "content" in research_data:
                for i, source in enumerate(research_data["content"][:3]):
                    source_text = source.get("text", "")
                    # Limit text length to keep prompt size manageable
                    context += f"\nSource {i+1}: {source.get('title', '')}\n{source_text[:1500]}...\n"
            
            # Build the prompt
            prompt = CONTENT_GENERATION_PROMPT.format(
                topic=topic_title,
                keywords=keywords_str
            )
            
            if context:
                prompt += f"\n\nUse the following research information to enrich your content:\n{context}"
            
            # Call Claude
            system_prompt = f"You are an expert AI content writer specialized in {topic_title}. Create comprehensive, accurate, and engaging content."
            response = self.claude_client.generate_text(
                system_prompt=system_prompt,
                user_message=prompt,
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS
            )
            
            # Extract title and body from the response
            content = response
            
            # Simple parsing - assumes the first line is the title
            lines = content.split('\n')
            title = lines[0].strip().replace('#', '').strip()
            body = '\n'.join(lines[1:]).strip()
            
            # Return the generated content
            return {
                "topic": topic,
                "title": title,
                "content": body,
                "keywords": keywords
            }
            
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            # Return a basic fallback content
            return {
                "topic": topic_data.get("topic", {}),
                "title": f"Understanding {topic_data.get('topic', {}).get('title', 'AI Technology')}",
                "content": f"An exploration of {topic_data.get('topic', {}).get('title', 'AI Technology')} and its impact on the industry.",
                "keywords": topic_data.get("topic", {}).get("keywords", [])
            }