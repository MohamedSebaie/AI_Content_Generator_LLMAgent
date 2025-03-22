import logging
import os
import json
from typing import Dict, Any
from PIL import Image
from utils.bedrock_client import BedrockClient
from utils.stable_diffusion_client import StableDiffusionClient
from utils.prompt_templates import IMAGE_PROMPT_GENERATION
from config import STABLE_DIFFUSION_MODEL, IMAGE_SIZE, TEMPERATURE, OUTPUT_DIR, HF_API_TOKEN

logger = logging.getLogger(__name__)

class ImageGeneratorAgent:
    def __init__(self):
        self.claude_client = BedrockClient()
        self.sd_client = StableDiffusionClient(api_token=HF_API_TOKEN)
        
        # Set the model ID to use
        if STABLE_DIFFUSION_MODEL:
            self.sd_client.set_model(STABLE_DIFFUSION_MODEL)
    
    def generate_image_prompt(self, title: str, content: str) -> Dict[str, str]:
        """
        Generate a prompt for image generation based on the blog content.
        """
        try:
            # Prepare a condensed version of content to fit in context window
            condensed_content = content[:2000] + "..." if len(content) > 2000 else content
            
            # Call Claude to generate an image prompt
            system_prompt = "You are an expert in creating descriptive prompts for AI image generation."
            user_message = IMAGE_PROMPT_GENERATION.format(
                title=title,
                content=condensed_content
            )
            
            response = self.claude_client.generate_text(
                system_prompt=system_prompt,
                user_message=user_message,
                temperature=TEMPERATURE
            )
            
            content = response
            
            # Parse the JSON response
            try:
                # Check if response is in a code block
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
                data = json.loads(content)
                return {
                    "image_prompt": data.get("image_prompt", ""),
                    "image_description": data.get("image_description", "")
                }
            except (json.JSONDecodeError, KeyError):
                # Fallback: extract the prompt in a more forgiving way
                lines = content.split('\n')
                image_prompt = ""
                image_description = ""
                
                for line in lines:
                    if "image prompt:" in line.lower():
                        image_prompt = line.split(":", 1)[1].strip()
                    elif "description:" in line.lower() or "caption:" in line.lower():
                        image_description = line.split(":", 1)[1].strip()
                
                return {
                    "image_prompt": image_prompt or f"A conceptual illustration of {title}",
                    "image_description": image_description or f"Illustration of {title}"
                }
                
        except Exception as e:
            logger.error(f"Error generating image prompt: {str(e)}")
            return {
                "image_prompt": f"A conceptual illustration of {title}, digital art style with technology themes",
                "image_description": f"Conceptual visualization of {title}"
            }
    
    def generate_image(self, image_prompt: str) -> Dict[str, Any]:
        """
        Generate an image using Stable Diffusion via Hugging Face API.
        """
        try:
            # Ensure output directory exists
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            
            # Set a negative prompt to avoid common issues
            negative_prompt = "low quality, blurry, distorted, deformed, disfigured, bad anatomy, text, watermark, signature, multiple faces"
            
            logger.info(f"Generating image with prompt: {image_prompt[:100]}...")
            
            # Generate the image using the API
            image = self.sd_client.generate_image(
                prompt=image_prompt,
                negative_prompt=negative_prompt,
                width=IMAGE_SIZE[0],
                height=IMAGE_SIZE[1],
                num_inference_steps=30,
                guidance_scale=7.5
            )
            
            # Save the image
            image_filename = f"blog_image_{os.urandom(4).hex()}.png"
            
            # Save the image and get path information
            image_data = self.sd_client.save_image(image, image_filename)
            
            return image_data
            
        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            return {"error": str(e)}
    
    def process_content_for_image(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the content and generate an accompanying image.
        """
        title = content_data.get("title", "AI Technology")
        content = content_data.get("content", "")
        
        # Generate the image prompt
        prompt_data = self.generate_image_prompt(title, content)
        image_prompt = prompt_data.get("image_prompt", "")
        image_description = prompt_data.get("image_description", "")
        
        # Generate the image
        image_data = self.generate_image(image_prompt)
        
        # Add image information to content data
        return {
            **content_data,
            "image_prompt": image_prompt,
            "image_description": image_description,
            "image_path": image_data.get("image_path", ""),
            "image_filename": image_data.get("image_filename", "")
        }