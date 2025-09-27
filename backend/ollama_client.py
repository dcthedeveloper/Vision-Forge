"""
Ollama Integration Module for VisionForge
Provides unified interface for local LLM functionality replacing emergentintegrations
"""

import ollama
import base64
import logging
from typing import Dict, List, Any, Optional
import json

# Configure logging
logger = logging.getLogger(__name__)

class OllamaClient:
    """Unified client for Ollama LLM operations"""
    
    def __init__(self):
        self.text_model = "llama3.2:latest"  # For narrative generation
        self.vision_model = "llava:7b"       # For image analysis
        
    async def generate_text(self, prompt: str, model: Optional[str] = None, temperature: float = 0.7) -> str:
        """Generate text using Ollama text model"""
        try:
            model_name = model or self.text_model
            response = ollama.generate(
                model=model_name,
                prompt=prompt,
                options={
                    'temperature': temperature,
                    'num_predict': 2048
                }
            )
            return response['response']
        except Exception as e:
            logger.error(f"Error generating text with Ollama: {e}")
            raise
    
    async def analyze_image(self, image_data: str, prompt: str) -> str:
        """Analyze image using Ollama vision model"""
        try:
            # Convert base64 image data to format expected by Ollama
            if image_data.startswith('data:image'):
                # Remove data:image/jpeg;base64, prefix if present
                image_data = image_data.split(',')[1]
            
            response = ollama.generate(
                model=self.vision_model,
                prompt=prompt,
                images=[image_data],
                options={
                    'temperature': 0.3,
                    'num_predict': 1024
                }
            )
            return response['response']
        except Exception as e:
            logger.error(f"Error analyzing image with Ollama: {e}")
            raise
    
    async def chat_completion(self, messages: List[Dict], model: Optional[str] = None, temperature: float = 0.7) -> str:
        """Chat completion using Ollama (converts to generate format)"""
        try:
            model_name = model or self.text_model
            
            # Convert chat messages to a single prompt
            prompt_parts = []
            for message in messages:
                role = message.get('role', 'user')
                content = message.get('content', '')
                if role == 'system':
                    prompt_parts.append(f"System: {content}")
                elif role == 'user':
                    prompt_parts.append(f"User: {content}")
                elif role == 'assistant':
                    prompt_parts.append(f"Assistant: {content}")
            
            prompt = "\n".join(prompt_parts) + "\nAssistant:"
            
            response = ollama.generate(
                model=model_name,
                prompt=prompt,
                options={
                    'temperature': temperature,
                    'num_predict': 2048
                }
            )
            return response['response']
        except Exception as e:
            logger.error(f"Error in chat completion with Ollama: {e}")
            raise

# Global client instance
ollama_client = OllamaClient()

# Helper functions to maintain API compatibility
async def get_text_generation(prompt: str, model: Optional[str] = None, temperature: float = 0.7) -> str:
    """Generate text - main interface function"""
    return await ollama_client.generate_text(prompt, model, temperature)

async def get_image_analysis(image_data: str, prompt: str) -> str:
    """Analyze image - main interface function"""
    return await ollama_client.analyze_image(image_data, prompt)

async def get_chat_completion(messages: List[Dict], model: Optional[str] = None, temperature: float = 0.7) -> str:
    """Chat completion - main interface function"""
    return await ollama_client.chat_completion(messages, model, temperature)