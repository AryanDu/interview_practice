"""
Image generation utilities using DALL-E or other services
"""
from typing import Optional, Dict, Any
import openai
from config import Config
import base64
from io import BytesIO


class ImageGenerator:
    """Generate images related to interview preparation"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or Config.OPENAI_API_KEY
        self.client = openai.OpenAI(api_key=self.api_key) if self.api_key else None
        self.model = Config.DEFAULT_IMAGE_MODEL
        self.size = Config.DEFAULT_IMAGE_SIZE
    
    def generate_interview_image(
        self,
        concept: str,
        style: str = "professional",
        size: str = None
    ) -> Dict[str, Any]:
        """Generate an image related to interview preparation"""
        if not self.client:
            raise ValueError("OpenAI API key not configured for image generation")
        
        prompt = f"""A professional {style} illustration representing: {concept}
        The image should be suitable for an interview preparation context.
        Style: clean, modern, business-appropriate."""
        
        size = size or self.size
        
        try:
            response = self.client.images.generate(
                model=self.model,
                prompt=prompt,
                size=size,
                quality="standard",
                n=1
            )
            
            image_url = response.data[0].url
            
            return {
                "success": True,
                "url": image_url,
                "revised_prompt": response.data[0].revised_prompt if hasattr(response.data[0], 'revised_prompt') else prompt,
                "concept": concept
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "concept": concept
            }
    
    def generate_motivational_image(self) -> Dict[str, Any]:
        """Generate a motivational image for interview preparation"""
        return self.generate_interview_image(
            concept="motivation and success in interviews",
            style="inspiring"
        )
    
    def generate_skill_visualization(self, skill: str) -> Dict[str, Any]:
        """Generate an image visualizing a specific skill"""
        return self.generate_interview_image(
            concept=f"visual representation of {skill} skills",
            style="diagrammatic"
        )
    
    def generate_result_card(self, score, skills, improvement, mock_score):
        """Generate a shareable result card image (stub)"""
        # Here you would implement the logic to create a result card image
        # For now, we return a dummy image URL
        return {"success": True, "url": "https://dummyimage.com/600x400/4caf50/fff&text=Result+Card"}

    def generate_mistake_snapshot(self, mistake_desc):
        """Generate a visual freeze frame for interview mistakes (stub)"""
        # Here you would implement the logic to create a mistake snapshot image
        # For now, we return a dummy image URL
        return {"success": True, "url": "https://dummyimage.com/600x400/f44336/fff&text=Mistake+Snapshot"}
