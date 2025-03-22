import os
import io
import base64
import requests
import json
import logging
from typing import Dict, Any, Optional
from PIL import Image
from config import OUTPUT_DIR

logger = logging.getLogger(__name__)

class StableDiffusionClient:
    """
    Client for interacting with Hugging Face's Stable Diffusion API.
    """
    def __init__(self, api_token: Optional[str] = None):
        """
        Initialize the Stable Diffusion client.
        
        Args:
            api_token: Your Hugging Face API token. If None, will attempt to load from 
                      environment variable HF_API_TOKEN or .env file.
        """
        # Get API token
        self.api_token = api_token or os.environ.get("HF_API_TOKEN")
        if not self.api_token:
            raise ValueError("API token must be provided or set in environment as HF_API_TOKEN")
        
        # Base URL for Hugging Face API
        self.api_url = "https://api-inference.huggingface.co/models"
        
        # Set default model to Stable Diffusion 2.1
        self.model_id = "stabilityai/stable-diffusion-xl-base-1.0"
        
        # Headers for API requests
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        logger.info(f"Initialized Stable Diffusion client with model: {self.model_id}")
    
    def set_model(self, model_id: str) -> None:
        """
        Change the Stable Diffusion model.
        
        Args:
            model_id: The Hugging Face model ID (e.g., "runwayml/stable-diffusion-v1-5")
        """
        self.model_id = model_id
        logger.info(f"Changed model to: {self.model_id}")
    
    def generate_image(self, 
                      prompt: str, 
                      negative_prompt: str = None,
                      width: int = 512, 
                      height: int = 512,
                      num_inference_steps: int = 50,
                      guidance_scale: float = 7.5) -> Image.Image:
        """
        Generate an image using Stable Diffusion.
        
        Args:
            prompt: Text description of the desired image
            negative_prompt: Text description of what to avoid in the image
            width: Output image width (multiples of 64 recommended)
            height: Output image height (multiples of 64 recommended)
            num_inference_steps: Number of denoising steps (higher = better quality, slower)
            guidance_scale: How closely to follow the prompt (higher = more faithful)
            
        Returns:
            PIL Image object
        """
        url = f"{self.api_url}/{self.model_id}"
        
        # Prepare the payload
        payload = {
            "inputs": prompt,
            "parameters": {
                "width": width,
                "height": height,
                "num_inference_steps": num_inference_steps,
                "guidance_scale": guidance_scale
            }
        }
        
        # Add negative prompt if provided
        if negative_prompt:
            payload["parameters"]["negative_prompt"] = negative_prompt
        
        logger.info(f"Generating image with prompt: {prompt[:100]}...")
        
        try:
            # Make the API request
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            # Get image from response
            image = Image.open(io.BytesIO(response.content))
            logger.info("Image generated successfully")
            
            return image
            
        except requests.exceptions.RequestException as e:
            if response.status_code == 503:
                # Model is loading
                logger.warning("Model is still loading. Try again in a few minutes.")
            else:
                logger.error(f"Error generating image: {str(e)}")
                logger.error(f"Response: {response.text}")
            
            raise
    
    def save_image(self, image: Image.Image, filename: str = None) -> Dict[str, str]:
        """
        Save a generated image to a file.
        
        Args:
            image: PIL Image object
            filename: Optional filename (will generate one if not provided)
            
        Returns:
            Dictionary with image path information
        """
        try:
            # Ensure output directory exists
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            
            # Generate filename if not provided
            if filename is None:
                filename = f"blog_image_{os.urandom(4).hex()}.png"
            
            # Add .png extension if not present
            if not filename.endswith('.png'):
                filename += '.png'
            
            # Full path
            image_path = os.path.join(OUTPUT_DIR, filename)
            
            # Save the image
            image.save(image_path)
            logger.info(f"Image saved to: {image_path}")
            
            # For web embedding, use a relative path
            relative_path = f"./outputs/{filename}"
            
            return {
                "image_path": relative_path,
                "image_filename": filename,
                "full_path": image_path
            }
            
        except Exception as e:
            logger.error(f"Error saving image: {str(e)}")
            raise