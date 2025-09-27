"""
VisionForge Hybrid AI Client
Provides seamless switching between Ollama (local) and Cloud (Claude/OpenAI) models
"""

from enum import Enum
from typing import Dict, List, Optional, Any
import logging
import os
from ollama_client import ollama_client
from content_filter import get_content_filter, ContentSafetyLevel

logger = logging.getLogger(__name__)

class AIProvider(Enum):
    OLLAMA = "ollama"           # Local models
    CLAUDE = "claude"           # Anthropic Claude
    OPENAI = "openai"           # OpenAI GPT models

class ModelType(Enum):
    TEXT = "text"               # Text generation
    VISION = "vision"           # Image analysis
    CHAT = "chat"               # Conversational

class HybridAIClient:
    def __init__(self):
        self.default_provider = AIProvider.OLLAMA
        self.provider_models = self._initialize_provider_models()
        self.content_filter = get_content_filter()
    
    def _initialize_provider_models(self) -> Dict[AIProvider, Dict[ModelType, str]]:
        """Initialize available models for each provider"""
        return {
            AIProvider.OLLAMA: {
                ModelType.TEXT: "llama3.2:latest",
                ModelType.VISION: "llava:7b",
                ModelType.CHAT: "llama3.2:latest"
            },
            AIProvider.CLAUDE: {
                ModelType.TEXT: "claude-sonnet-4-20250514",
                ModelType.VISION: "claude-sonnet-4-20250514",  # Claude has vision
                ModelType.CHAT: "claude-sonnet-4-20250514"
            },
            AIProvider.OPENAI: {
                ModelType.TEXT: "gpt-4o",
                ModelType.VISION: "gpt-4o",  # GPT-4o has vision
                ModelType.CHAT: "gpt-4o"
            }
        }
    
    async def generate_text(self, prompt: str, 
                          provider: Optional[AIProvider] = None,
                          safety_level: ContentSafetyLevel = ContentSafetyLevel.MODERATE,
                          temperature: float = 0.7) -> str:
        """Generate text using specified provider with content filtering"""
        
        provider = provider or self.default_provider
        
        # Apply content filtering to prompt
        filtered_prompt = self.content_filter.apply_content_filter_to_prompt(prompt, safety_level)
        
        try:
            if provider == AIProvider.OLLAMA:
                response = await ollama_client.generate_text(filtered_prompt, temperature=temperature)
            
            elif provider == AIProvider.CLAUDE:
                response = await self._generate_with_claude(filtered_prompt, temperature)
            
            elif provider == AIProvider.OPENAI:
                response = await self._generate_with_openai(filtered_prompt, temperature)
            
            else:
                raise ValueError(f"Unsupported provider: {provider}")
            
            # Filter the response
            filter_result = self.content_filter.analyze_content(response, safety_level)
            
            if not filter_result.allowed:
                logger.warning(f"Generated content filtered out for safety level {safety_level.value}")
                # Return a safe fallback or regenerate with stricter prompt
                return await self._generate_safe_fallback(prompt, provider, safety_level)
            
            return response
            
        except Exception as e:
            logger.error(f"Text generation failed with {provider.value}: {e}")
            # Fallback to Ollama if cloud provider fails
            if provider != AIProvider.OLLAMA:
                logger.info("Falling back to Ollama for text generation")
                return await self.generate_text(prompt, AIProvider.OLLAMA, safety_level, temperature)
            raise
    
    async def analyze_image(self, image_data: str, prompt: str,
                          provider: Optional[AIProvider] = None,
                          safety_level: ContentSafetyLevel = ContentSafetyLevel.MODERATE) -> str:
        """Analyze image using specified provider with content filtering"""
        
        provider = provider or self.default_provider
        
        # Apply content filtering to prompt
        filtered_prompt = self.content_filter.apply_content_filter_to_prompt(prompt, safety_level)
        
        try:
            if provider == AIProvider.OLLAMA:
                response = await ollama_client.analyze_image(image_data, filtered_prompt)
            
            elif provider == AIProvider.CLAUDE:
                response = await self._analyze_image_with_claude(image_data, filtered_prompt)
            
            elif provider == AIProvider.OPENAI:
                response = await self._analyze_image_with_openai(image_data, filtered_prompt)
            
            else:
                raise ValueError(f"Unsupported provider: {provider}")
            
            # Filter the response
            filter_result = self.content_filter.analyze_content(response, safety_level)
            
            if not filter_result.allowed:
                logger.warning(f"Image analysis filtered out for safety level {safety_level.value}")
                return await self._generate_safe_image_analysis(image_data, prompt, provider, safety_level)
            
            return response
            
        except Exception as e:
            logger.error(f"Image analysis failed with {provider.value}: {e}")
            # Fallback to Ollama if cloud provider fails
            if provider != AIProvider.OLLAMA:
                logger.info("Falling back to Ollama for image analysis")
                return await self.analyze_image(image_data, prompt, AIProvider.OLLAMA, safety_level)
            raise
    
    async def _generate_with_claude(self, prompt: str, temperature: float) -> str:
        """Generate text using Claude via emergentintegrations"""
        try:
            from emergentintegrations.llm.chat import LlmChat, UserMessage
            
            chat = LlmChat(
                api_key=os.environ['EMERGENT_LLM_KEY'],
                session_id=f"hybrid-claude-{hash(prompt) % 10000}",
                system_message="You are VisionForge AI, helping creators build sophisticated characters and narratives."
            ).with_model("anthropic", "claude-sonnet-4-20250514")
            
            response = await chat.send_message(UserMessage(text=prompt))
            return str(response)
            
        except Exception as e:
            logger.error(f"Claude generation failed: {e}")
            raise
    
    async def _generate_with_openai(self, prompt: str, temperature: float) -> str:
        """Generate text using OpenAI via emergentintegrations"""
        try:
            from emergentintegrations.llm.chat import LlmChat, UserMessage
            
            chat = LlmChat(
                api_key=os.environ['EMERGENT_LLM_KEY'],
                session_id=f"hybrid-openai-{hash(prompt) % 10000}",
                system_message="You are VisionForge AI, helping creators build sophisticated characters and narratives."
            ).with_model("openai", "gpt-4o")
            
            response = await chat.send_message(UserMessage(text=prompt))
            return str(response)
            
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            raise
    
    async def _analyze_image_with_claude(self, image_data: str, prompt: str) -> str:
        """Analyze image using Claude via emergentintegrations"""
        try:
            from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent
            
            image_content = ImageContent(image_base64=image_data)
            
            chat = LlmChat(
                api_key=os.environ['EMERGENT_LLM_KEY'],
                session_id=f"hybrid-claude-vision-{hash(prompt) % 10000}",
                system_message="You are VisionForge AI, analyzing images for character creation and storytelling."
            ).with_model("anthropic", "claude-sonnet-4-20250514")
            
            response = await chat.send_message(UserMessage(
                text=prompt,
                file_contents=[image_content]
            ))
            return str(response)
            
        except Exception as e:
            logger.error(f"Claude vision analysis failed: {e}")
            raise
    
    async def _analyze_image_with_openai(self, image_data: str, prompt: str) -> str:
        """Analyze image using OpenAI via emergentintegrations"""
        try:
            from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent
            
            image_content = ImageContent(image_base64=image_data)
            
            chat = LlmChat(
                api_key=os.environ['EMERGENT_LLM_KEY'],
                session_id=f"hybrid-openai-vision-{hash(prompt) % 10000}",
                system_message="You are VisionForge AI, analyzing images for character creation and storytelling."
            ).with_model("openai", "gpt-4o")
            
            response = await chat.send_message(UserMessage(
                text=prompt,
                file_contents=[image_content]
            ))
            return str(response)
            
        except Exception as e:
            logger.error(f"OpenAI vision analysis failed: {e}")
            raise
    
    async def _generate_safe_fallback(self, original_prompt: str, 
                                    provider: AIProvider, 
                                    safety_level: ContentSafetyLevel) -> str:
        """Generate a safe fallback response when content is filtered"""
        
        fallback_prompt = f"""The original request contained content that doesn't meet {safety_level.value} safety guidelines. 
        Please provide a similar but appropriate response that follows these guidelines:
        
        {self.content_filter.get_safety_level_info(safety_level)['description']}
        
        Original intent: {original_prompt[:200]}..."""
        
        return await self.generate_text(fallback_prompt, provider, safety_level, temperature=0.5)
    
    async def _generate_safe_image_analysis(self, image_data: str, original_prompt: str,
                                          provider: AIProvider, 
                                          safety_level: ContentSafetyLevel) -> str:
        """Generate safe image analysis when content is filtered"""
        
        safe_prompt = f"""Analyze this image focusing on appropriate content for {safety_level.value} guidelines:
        
        Guidelines: {self.content_filter.get_safety_level_info(safety_level)['description']}
        
        Focus on: visual elements, artistic style, character appearance, setting details.
        Avoid: {', '.join([cat.value for cat in self.content_filter.get_safety_level_info(safety_level).get('forbidden_categories', [])])}"""
        
        return await self.analyze_image(image_data, safe_prompt, provider, safety_level)
    
    def set_default_provider(self, provider: AIProvider):
        """Set the default AI provider"""
        self.default_provider = provider
        logger.info(f"Default AI provider set to {provider.value}")
    
    def get_available_providers(self) -> List[Dict[str, Any]]:
        """Get list of available AI providers"""
        return [
            {
                "id": AIProvider.OLLAMA.value,
                "name": "Ollama (Local)",
                "description": "Local AI models for privacy and full content control",
                "strengths": ["Privacy", "No API costs", "NSFW-friendly", "Always available"],
                "best_for": ["Content freedom", "Offline work", "Cost control"]
            },
            {
                "id": AIProvider.CLAUDE.value,
                "name": "Claude Sonnet 4",
                "description": "Anthropic's advanced AI for high-quality prose and analysis",
                "strengths": ["Best prose quality", "Low 'cheese' factor", "Complex reasoning"],
                "best_for": ["Polished writing", "Character depth", "Narrative structure"]
            },
            {
                "id": AIProvider.OPENAI.value,
                "name": "OpenAI GPT-4o",
                "description": "OpenAI's multimodal AI for fast, reliable generation",
                "strengths": ["Speed", "Consistency", "Function calling", "Vision"],
                "best_for": ["Quick iteration", "Image analysis", "Structured output"]
            }
        ]
    
    def get_provider_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all providers"""
        status = {}
        
        for provider in AIProvider:
            try:
                # Test basic availability
                if provider == AIProvider.OLLAMA:
                    # Check if Ollama is running
                    import requests
                    response = requests.get("http://localhost:11434/api/tags", timeout=5)
                    available = response.status_code == 200
                else:
                    # Check if emergent key is available
                    available = bool(os.environ.get('EMERGENT_LLM_KEY'))
                
                status[provider.value] = {
                    "available": available,
                    "models": self.provider_models[provider],
                    "status": "ready" if available else "unavailable"
                }
                
            except Exception as e:
                status[provider.value] = {
                    "available": False,
                    "models": {},
                    "status": f"error: {str(e)}"
                }
        
        return status

# Singleton instance
hybrid_client = None

def get_hybrid_ai_client():
    """Get or create hybrid AI client instance"""
    global hybrid_client
    if hybrid_client is None:
        hybrid_client = HybridAIClient()
    return hybrid_client