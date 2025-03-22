import logging
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
    
    def iterative_refinement(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform iterative refinement on the content.
        """
        # Initialize history to track iterations
        refinement_history = []
        current_content = content_data.get("content", "")
        title = content_data.get("title", "")
        
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
            
        # Return the final refined content with history
        return {
            "topic": content_data.get("topic", {}),
            "title": title,
            "content": current_content,  # This is the final version
            "keywords": content_data.get("keywords", []),
            "refinement_history": refinement_history
        }