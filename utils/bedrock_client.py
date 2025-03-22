import json
import boto3 # type: ignore
import logging
from typing import List, Dict, Any, Optional
from config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, CLAUDE_MODEL_ID, MAX_TOKENS, TEMPERATURE

logger = logging.getLogger(__name__)

class BedrockClient:
    def __init__(self):
        """
        Initialize the AWS Bedrock client for interacting with Claude model.
        """
        self.client = boto3.client(
            service_name='bedrock-runtime',
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
        self.model_id = CLAUDE_MODEL_ID
    
    def invoke_model(self, 
                     system_prompt: str, 
                     messages: List[Dict[str, str]], 
                     temperature: float = TEMPERATURE, 
                     max_tokens: int = MAX_TOKENS) -> Dict[str, Any]:
        """
        Invoke the Claude model with the given prompt and parameters.
        
        Args:
            system_prompt: The system instructions for Claude
            messages: List of message objects (role and content)
            temperature: Controls randomness (0-1)
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            The model's response
        """
        try:
            # Format the request for Claude on Bedrock
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "system": system_prompt,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            # Invoke the model
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )
            
            # Parse and return the response
            response_body = json.loads(response.get('body').read())
            return response_body
            
        except Exception as e:
            logger.error(f"Error invoking Claude model: {str(e)}")
            # Return a minimal response structure in case of error
            return {
                "error": str(e),
                "content": f"Error invoking model: {str(e)}"
            }
    
    def generate_text(self, 
                      system_prompt: str, 
                      user_message: str,
                      temperature: float = TEMPERATURE,
                      max_tokens: int = MAX_TOKENS) -> str:
        """
        Simplified method to generate text with Claude using a single user message.
        
        Args:
            system_prompt: System instructions
            user_message: The user's message/prompt
            temperature: Controls randomness
            max_tokens: Maximum tokens to generate
            
        Returns:
            The model's text response
        """
        messages = [{"role": "user", "content": user_message}]
        
        response = self.invoke_model(
            system_prompt=system_prompt,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Extract the response content
        if "content" in response:
            return response["content"][0]["text"]
        elif "error" in response:
            logger.error(f"Error from Claude API: {response['error']}")
            return f"Error generating content: {response.get('error', 'Unknown error')}"
        else:
            return "Error: Unexpected response format from model"