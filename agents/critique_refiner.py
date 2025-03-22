import logging
import re
from typing import Dict, Any, List
from utils.bedrock_client import BedrockClient
from utils.prompt_templates import SELF_CRITIQUE_PROMPT, CONTENT_REFINEMENT_PROMPT
from config import TEMPERATURE, MAX_TOKENS, MAX_ITERATIONS

logger = logging.getLogger(__name__)

class CritiqueRefinerAgent:
    def __init__(self):
        self.claude_client = BedrockClient()
    
    def critique_content(self, content: str) -> str:
        """
        Generate a critique of the content.
        """
        try:
            # Call Claude for critique
            system_prompt = "You are an expert editor specializing in technical content about artificial intelligence."
            user_message = SELF_CRITIQUE_PROMPT.format(content=content)
            
            response = self.claude_client.generate_text(
                system_prompt=system_prompt,
                user_message=user_message,
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating critique: {str(e)}")
            return "The content needs improvement in clarity and structure. Consider adding more specific examples and reorganizing the sections for better flow."
    
    def refine_content(self, original_content: str, critique: str) -> str:
        """
        Refine the content based on the critique.
        """
        try:
            # Call Claude for refinement
            system_prompt = "You are an expert AI content writer. Your task is to improve content based on editorial feedback."
            user_message = CONTENT_REFINEMENT_PROMPT.format(
                original_content=original_content,
                critique=critique
            )
            
            response = self.claude_client.generate_text(
                system_prompt=system_prompt,
                user_message=user_message,
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error refining content: {str(e)}")
            return original_content
    
    def _format_final_content(self, content: str) -> str:
        """
        Format the final content to be properly structured for the HTML generator.
        Ensures proper headings and paragraphs.
        """
        # Clean up any excessive newlines
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # Ensure headings are properly formatted with # symbols if not already
        lines = content.split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                # Check if this looks like a heading but doesn't use markdown format
                if re.match(r'^[A-Z][A-Za-z0-9\s:]{5,50}$', line) and not line.startswith('#'):
                    if len(line) <= 40:  # Short enough to be a main heading
                        formatted_lines.append(f"# {line}")
                    else:  # Likely a subheading
                        formatted_lines.append(f"## {line}")
                else:
                    formatted_lines.append(line)
        
        # Join the lines back together
        formatted_content = '\n'.join(formatted_lines)
        
        # Ensure paragraphs are properly separated
        formatted_content = re.sub(r'(\w)\n(\w)', r'\1\n\n\2', formatted_content)
        
        return formatted_content
    
    def finalize_content(self, content: str, title: str) -> str:
        """
        Perform final formatting on the content to prepare it for HTML generation.
        """
        try:
            # Get Claude to format the content with proper headings and structure
            system_prompt = """You are an expert content formatter preparing blog content for HTML conversion.
            Format the content with proper Markdown headings and paragraph structure.
            Ensure the title uses a # heading, section titles use ## headings, and subsections use ### headings.
            Maintain proper paragraph spacing for readability.
            Return only the formatted content without explanations."""
            
            user_message = f"""Format this blog post for HTML conversion:
            
            Title: {title}
            
            Content:
            {content}
            
            Please structure with proper markdown headings (# for title, ## for main sections, ### for subsections) 
            and ensure paragraphs are properly separated. Don't add any new content, just structure the existing content."""
            
            formatted_content = self.claude_client.generate_text(
                system_prompt=system_prompt,
                user_message=user_message,
                temperature=0.1,  # Lower temperature for more consistent formatting
                max_tokens=MAX_TOKENS
            )
            
            # Do additional formatting if needed
            formatted_content = self._format_final_content(formatted_content)
            
            return formatted_content
            
        except Exception as e:
            logger.error(f"Error finalizing content: {str(e)}")
            # Fall back to simple formatting
            return self._format_final_content(content)
    
    def iterative_refinement(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform iterative refinement on the content.
        """
        # Initialize history to track iterations
        refinement_history = []
        current_content = content_data.get("content", "")
        title = content_data.get("title", "")
        
        # Remove "Title:" prefix if present
        if title.startswith("Title:"):
            title = title[6:].strip()
        
        logger.info(f"Starting iterative refinement for: {title}")
        
        # Track iterations
        for iteration in range(MAX_ITERATIONS):
            logger.info(f"Iteration {iteration+1}/{MAX_ITERATIONS}")
            
            # Generate critique
            critique = self.critique_content(current_content)
            
            # Store the critique
            refinement_history.append({
                "iteration": iteration + 1,
                "critique": critique
            })
            
            # Skip refinement on the last iteration
            if iteration < MAX_ITERATIONS - 1:
                # Refine content based on critique
                refined_content = self.refine_content(current_content, critique)
                
                # Update current content for next iteration
                current_content = refined_content
                
                # Store the refined content
                refinement_history[-1]["refined_content"] = refined_content
        
        # Perform final formatting before returning
        final_content = self.finalize_content(current_content, title)
        print("==============================================")
        print("Final content:")
        print(final_content)
        print("==============================================")
            
        # Return the final refined content with history
        return {
            "topic": content_data.get("topic", {}),
            "title": title,
            "content": final_content,  # This is the final version
            "keywords": content_data.get("keywords", []),
            "refinement_history": refinement_history
        }
