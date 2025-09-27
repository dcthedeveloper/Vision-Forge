#!/usr/bin/env python3
"""
VisionForge Backend Testing Suite
Tests Ollama integration and all API endpoints
"""

import asyncio
import aiohttp
import json
import base64
import os
import sys
from pathlib import Path
import tempfile
from PIL import Image
import io

# Test configuration
BACKEND_URL = "https://storycraft-102.preview.emergentagent.com/api"
TEST_IMAGE_SIZE = (256, 256)

class VisionForgeBackendTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_result(self, test_name: str, success: bool, message: str, details: dict = None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details or {}
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def create_test_image(self) -> bytes:
        """Create a simple test image"""
        # Create a simple colored image for testing
        img = Image.new('RGB', TEST_IMAGE_SIZE, color='blue')
        # Add some simple shapes to make it more interesting
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        draw.rectangle([50, 50, 150, 150], fill='red')
        draw.ellipse([100, 100, 200, 200], fill='green')
        
        # Convert to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        return img_bytes.getvalue()
    
    async def test_health_check(self):
        """Test basic API health check at /api/"""
        try:
            async with self.session.get(f"{BACKEND_URL}/") as response:
                if response.status == 200:
                    data = await response.json()
                    if "message" in data and "VisionForge" in data["message"]:
                        self.log_result("Health Check", True, "API is responding correctly", data)
                    else:
                        self.log_result("Health Check", False, "Unexpected response format", data)
                else:
                    self.log_result("Health Check", False, f"HTTP {response.status}", {"status": response.status})
        except Exception as e:
            self.log_result("Health Check", False, f"Connection error: {str(e)}")
    
    async def test_get_genres(self):
        """Test get available genres at /api/genres"""
        try:
            async with self.session.get(f"{BACKEND_URL}/genres") as response:
                if response.status == 200:
                    data = await response.json()
                    if "genres" in data and isinstance(data["genres"], dict):
                        genre_count = len(data["genres"])
                        sample_genres = list(data["genres"].keys())[:3]
                        self.log_result("Get Genres", True, f"Retrieved {genre_count} genres", 
                                      {"sample_genres": sample_genres, "total_count": genre_count})
                    else:
                        self.log_result("Get Genres", False, "Invalid genres response format", data)
                else:
                    self.log_result("Get Genres", False, f"HTTP {response.status}", {"status": response.status})
        except Exception as e:
            self.log_result("Get Genres", False, f"Request error: {str(e)}")
    
    async def test_image_analysis(self):
        """Test image analysis functionality at /api/analyze-image (core feature)"""
        try:
            # Create test image
            test_image = self.create_test_image()
            
            # Prepare multipart form data
            data = aiohttp.FormData()
            data.add_field('file', test_image, filename='test_image.jpg', content_type='image/jpeg')
            data.add_field('genre', 'urban_realistic')
            data.add_field('origin', 'nootropic_enhanced')
            data.add_field('social_status', 'entrepreneurial')
            data.add_field('power_source', 'nootropic_drug')
            data.add_field('evolution_stage', 'synergistic')
            data.add_field('geographic_context', 'detroit')
            data.add_field('op_mode', 'false')
            
            async with self.session.post(f"{BACKEND_URL}/analyze-image", data=data) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "analysis" in data:
                        analysis = data["analysis"]
                        # Check for key components of analysis
                        has_traits = "traits" in analysis and len(analysis["traits"]) > 0
                        has_powers = "power_suggestions" in analysis and len(analysis["power_suggestions"]) > 0
                        has_backstory = "backstory_seeds" in analysis and len(analysis["backstory_seeds"]) > 0
                        has_persona = "persona_summary" in analysis and analysis["persona_summary"]
                        
                        if has_traits and has_powers and has_backstory and has_persona:
                            self.log_result("Image Analysis (LLaVA)", True, "Complete character analysis generated", {
                                "traits_count": len(analysis["traits"]),
                                "powers_count": len(analysis["power_suggestions"]),
                                "backstory_seeds": len(analysis["backstory_seeds"]),
                                "has_persona": bool(analysis["persona_summary"])
                            })
                        else:
                            self.log_result("Image Analysis (LLaVA)", False, "Incomplete analysis response", {
                                "has_traits": has_traits,
                                "has_powers": has_powers,
                                "has_backstory": has_backstory,
                                "has_persona": has_persona
                            })
                    else:
                        self.log_result("Image Analysis (LLaVA)", False, "Invalid response format", data)
                else:
                    error_text = await response.text()
                    self.log_result("Image Analysis (LLaVA)", False, f"HTTP {response.status}", {"error": error_text})
        except Exception as e:
            self.log_result("Image Analysis (LLaVA)", False, f"Request error: {str(e)}")
    
    async def test_text_generation(self):
        """Test text generation at /api/generate-text with Llama3.2"""
        try:
            test_payload = {
                "prompt": "Create a compelling backstory for a cyberpunk hacker who discovered they have telepathic abilities",
                "generation_type": "backstory",
                "style_preferences": {"tone": "gritty", "length": "medium"}
            }
            
            async with self.session.post(f"{BACKEND_URL}/generate-text", 
                                       json=test_payload,
                                       headers={"Content-Type": "application/json"}) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "generated_text" in data:
                        generated_text = data["generated_text"]
                        text_length = len(generated_text)
                        has_cliche_score = "cliche_score" in data
                        
                        if text_length > 50:  # Reasonable minimum length
                            self.log_result("Text Generation (Llama3.2)", True, "Creative text generated successfully", {
                                "text_length": text_length,
                                "cliche_score": data.get("cliche_score", "N/A"),
                                "has_suggestions": bool(data.get("suggestions"))
                            })
                        else:
                            self.log_result("Text Generation (Llama3.2)", False, "Generated text too short", {
                                "text_length": text_length,
                                "text_preview": generated_text[:100]
                            })
                    else:
                        self.log_result("Text Generation (Llama3.2)", False, "Invalid response format", data)
                else:
                    error_text = await response.text()
                    self.log_result("Text Generation (Llama3.2)", False, f"HTTP {response.status}", {"error": error_text})
        except Exception as e:
            self.log_result("Text Generation (Llama3.2)", False, f"Request error: {str(e)}")
    
    async def test_style_analysis(self):
        """Test style analysis at /api/analyze-style"""
        try:
            test_text = """The mysterious figure delved into the enigmatic tapestry of shadows, 
            their meticulous movements betraying a hidden agenda. The ancient prophecy spoke of 
            a chosen one who would manipulate the very fabric of reality through their kinetic abilities."""
            
            test_payload = {
                "text": test_text
            }
            
            async with self.session.post(f"{BACKEND_URL}/analyze-style",
                                       json=test_payload,
                                       headers={"Content-Type": "application/json"}) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "cliche_score" in data:
                        cliche_score = data["cliche_score"]
                        has_issues = "issues" in data and len(data["issues"]) > 0
                        has_suggestions = "suggestions" in data and len(data["suggestions"]) > 0
                        
                        # The test text contains many clichés, so we expect a high score
                        if cliche_score > 0.3:  # Should detect the clichés
                            self.log_result("Style Analysis", True, "Cliché detection working correctly", {
                                "cliche_score": cliche_score,
                                "issues_found": len(data.get("issues", [])),
                                "suggestions_provided": len(data.get("suggestions", []))
                            })
                        else:
                            self.log_result("Style Analysis", False, "Failed to detect obvious clichés", {
                                "cliche_score": cliche_score,
                                "expected": "> 0.3"
                            })
                    else:
                        self.log_result("Style Analysis", False, "Invalid response format", data)
                else:
                    error_text = await response.text()
                    self.log_result("Style Analysis", False, f"HTTP {response.status}", {"error": error_text})
        except Exception as e:
            self.log_result("Style Analysis", False, f"Request error: {str(e)}")
    
    async def test_analyses_history(self):
        """Test history endpoint at /api/analyses"""
        try:
            async with self.session.get(f"{BACKEND_URL}/analyses") as response:
                if response.status == 200:
                    data = await response.json()
                    if isinstance(data, list):
                        analysis_count = len(data)
                        # Check if we have any analyses and if they have expected structure
                        if analysis_count > 0:
                            sample_analysis = data[0]
                            has_id = "id" in sample_analysis
                            has_created_at = "created_at" in sample_analysis
                            
                            self.log_result("Analyses History", True, f"Retrieved {analysis_count} analyses", {
                                "count": analysis_count,
                                "has_proper_structure": has_id and has_created_at,
                                "sample_keys": list(sample_analysis.keys())[:5]
                            })
                        else:
                            self.log_result("Analyses History", True, "Empty analyses list (expected for new system)", {
                                "count": 0
                            })
                    else:
                        self.log_result("Analyses History", False, "Response is not a list", {"type": type(data).__name__})
                else:
                    error_text = await response.text()
                    self.log_result("Analyses History", False, f"HTTP {response.status}", {"error": error_text})
        except Exception as e:
            self.log_result("Analyses History", False, f"Request error: {str(e)}")
    
    async def test_ollama_models_availability(self):
        """Test if Ollama models are available and responding"""
        try:
            # Test a simple text generation to verify Llama3.2 is working
            simple_payload = {
                "prompt": "Hello, this is a test. Please respond with 'Ollama is working correctly.'",
                "generation_type": "character"
            }
            
            async with self.session.post(f"{BACKEND_URL}/generate-text",
                                       json=simple_payload,
                                       headers={"Content-Type": "application/json"}) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "generated_text" in data:
                        response_text = data["generated_text"].lower()
                        if "ollama" in response_text or len(data["generated_text"]) > 10:
                            self.log_result("Ollama Models Availability", True, "Ollama models responding", {
                                "llama3.2_status": "working",
                                "response_length": len(data["generated_text"])
                            })
                        else:
                            self.log_result("Ollama Models Availability", False, "Unexpected model response", {
                                "response": data["generated_text"]
                            })
                    else:
                        self.log_result("Ollama Models Availability", False, "No text generated", data)
                else:
                    self.log_result("Ollama Models Availability", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_result("Ollama Models Availability", False, f"Model test error: {str(e)}")
    
    async def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting VisionForge Backend Tests with Ollama Integration")
        print(f"Testing against: {BACKEND_URL}")
        print("=" * 60)
        
        # Run tests in order of importance
        await self.test_health_check()
        await self.test_get_genres()
        await self.test_ollama_models_availability()
        await self.test_text_generation()
        await self.test_style_analysis()
        await self.test_image_analysis()  # Most complex test last
        await self.test_analyses_history()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if total - passed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")
        
        print("\n🔍 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if result["details"]:
                for key, value in result["details"].items():
                    print(f"    {key}: {value}")
        
        return passed == total

async def main():
    """Main test runner"""
    async with VisionForgeBackendTester() as tester:
        success = await tester.run_all_tests()
        return 0 if success else 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test runner error: {e}")
        sys.exit(1)