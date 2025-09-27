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
    
    async def test_beat_sheet_types(self):
        """Test beat sheet types endpoint at /api/beat-sheet-types"""
        try:
            async with self.session.get(f"{BACKEND_URL}/beat-sheet-types") as response:
                if response.status == 200:
                    data = await response.json()
                    if "sheet_types" in data and "tone_pacing" in data:
                        sheet_types = data["sheet_types"]
                        tone_pacing = data["tone_pacing"]
                        
                        # Verify expected sheet types
                        expected_types = ["save_the_cat", "dan_harmon", "three_act", "hero_journey", "kishōtenketsu"]
                        available_types = [st["value"] for st in sheet_types]
                        
                        # Verify expected tone pacing options
                        expected_pacing = ["slow_burn", "standard", "fast_paced", "explosive"]
                        available_pacing = [tp["value"] for tp in tone_pacing]
                        
                        types_match = all(t in available_types for t in expected_types)
                        pacing_match = all(p in available_pacing for p in expected_pacing)
                        
                        if types_match and pacing_match:
                            self.log_result("Beat Sheet Types", True, "All expected types and pacing options available", {
                                "sheet_types_count": len(sheet_types),
                                "tone_pacing_count": len(tone_pacing),
                                "available_types": available_types,
                                "available_pacing": available_pacing
                            })
                        else:
                            self.log_result("Beat Sheet Types", False, "Missing expected types or pacing options", {
                                "types_match": types_match,
                                "pacing_match": pacing_match,
                                "available_types": available_types,
                                "available_pacing": available_pacing
                            })
                    else:
                        self.log_result("Beat Sheet Types", False, "Invalid response format", data)
                else:
                    error_text = await response.text()
                    self.log_result("Beat Sheet Types", False, f"HTTP {response.status}", {"error": error_text})
        except Exception as e:
            self.log_result("Beat Sheet Types", False, f"Request error: {str(e)}")
    
    async def test_beat_sheet_generation(self):
        """Test beat sheet generation at /api/generate-beat-sheet"""
        try:
            # Test with different sheet types and configurations
            test_configs = [
                {
                    "sheet_type": "save_the_cat",
                    "tone_pacing": "standard",
                    "story_length": 110,
                    "character_data": {
                        "character_origin": "nootropic_enhanced",
                        "power_source": "nootropic_drug",
                        "social_status": "entrepreneurial",
                        "traits": [{"trait": "Strategic mastermind with enhanced cognition"}],
                        "backstory_seeds": ["Former entrepreneur who gained cognitive enhancement"],
                        "power_suggestions": [{"name": "Hypercognitive Processing", "description": "Enhanced mental processing"}]
                    }
                },
                {
                    "sheet_type": "dan_harmon",
                    "tone_pacing": "fast_paced",
                    "story_length": 90
                },
                {
                    "sheet_type": "three_act",
                    "tone_pacing": "explosive",
                    "story_length": 120
                }
            ]
            
            success_count = 0
            for i, config in enumerate(test_configs):
                try:
                    async with self.session.post(f"{BACKEND_URL}/generate-beat-sheet",
                                               json=config,
                                               headers={"Content-Type": "application/json"}) as response:
                        if response.status == 200:
                            data = await response.json()
                            if data.get("success") and "beat_sheet" in data:
                                beat_sheet = data["beat_sheet"]
                                
                                # Verify beat sheet structure
                                required_fields = ["sheet_type", "title", "description", "total_beats", "beats"]
                                has_required = all(field in beat_sheet for field in required_fields)
                                
                                # Verify beats structure
                                beats = beat_sheet.get("beats", [])
                                valid_beats = all(
                                    all(field in beat for field in ["beat_number", "beat_name", "description", "page_range"])
                                    for beat in beats
                                ) if beats else False
                                
                                if has_required and valid_beats and len(beats) > 0:
                                    success_count += 1
                                    self.log_result(f"Beat Sheet Generation ({config['sheet_type']})", True, 
                                                  f"Generated {len(beats)} beats successfully", {
                                                      "sheet_type": beat_sheet["sheet_type"],
                                                      "total_beats": beat_sheet["total_beats"],
                                                      "estimated_pages": beat_sheet.get("estimated_pages", "N/A"),
                                                      "has_character_integration": bool(config.get("character_data"))
                                                  })
                                else:
                                    self.log_result(f"Beat Sheet Generation ({config['sheet_type']})", False, 
                                                  "Invalid beat sheet structure", {
                                                      "has_required_fields": has_required,
                                                      "valid_beats": valid_beats,
                                                      "beats_count": len(beats)
                                                  })
                            else:
                                self.log_result(f"Beat Sheet Generation ({config['sheet_type']})", False, 
                                              "Invalid response format", data)
                        else:
                            error_text = await response.text()
                            self.log_result(f"Beat Sheet Generation ({config['sheet_type']})", False, 
                                          f"HTTP {response.status}", {"error": error_text})
                except Exception as e:
                    self.log_result(f"Beat Sheet Generation ({config['sheet_type']})", False, 
                                  f"Request error: {str(e)}")
            
            # Overall beat sheet generation result
            if success_count == len(test_configs):
                self.log_result("Beat Sheet Generation (Overall)", True, 
                              f"All {success_count} configurations successful", {
                                  "tested_configs": len(test_configs),
                                  "successful": success_count
                              })
            else:
                self.log_result("Beat Sheet Generation (Overall)", False, 
                              f"Only {success_count}/{len(test_configs)} configurations successful", {
                                  "tested_configs": len(test_configs),
                                  "successful": success_count
                              })
                
        except Exception as e:
            self.log_result("Beat Sheet Generation (Overall)", False, f"Test setup error: {str(e)}")
    
    async def test_trope_risk_analysis(self):
        """Test trope risk analysis at /api/analyze-trope-risk - CRITICAL: Test timeout fixes"""
        import time
        try:
            # Test with sophisticated Marcus-style character
            sophisticated_character = {
                "id": "test-character-sophisticated",
                "character_origin": "nootropic_enhanced",
                "power_source": "nootropic_drug",
                "social_status": "entrepreneurial",
                "geographic_context": "detroit",
                "archetype_tags": ["System Changer", "Power Broker"],
                "traits": [
                    {"trait": "Strategic mastermind with enhanced cognition"},
                    {"trait": "Systematic empire builder"}
                ],
                "backstory_seeds": [
                    "Former entrepreneur who gained cognitive enhancement",
                    "Uses intelligence to navigate complex power structures"
                ],
                "power_suggestions": [
                    {"name": "Hypercognitive Processing", "description": "Enhanced mental processing speed", "cost_level": 8},
                    {"name": "Strategic Network Analysis", "description": "Analyzes social and business networks", "cost_level": 7}
                ]
            }
            
            # Test with clichéd character for comparison
            cliched_character = {
                "id": "test-character-cliched",
                "character_origin": "human",
                "power_source": "magic",
                "traits": [{"trait": "Mysterious past"}],
                "backstory_seeds": ["Orphaned hero with dark past", "Chosen one destined to save world"],
                "power_suggestions": [
                    {"name": "Fire Control", "description": "Controls fire elements", "cost_level": 5},
                    {"name": "Super Strength", "description": "Incredible physical strength", "cost_level": 6}
                ]
            }
            
            test_characters = [
                ("Sophisticated Character", sophisticated_character),
                ("Clichéd Character", cliched_character)
            ]
            
            for char_name, character_data in test_characters:
                try:
                    test_payload = {"character_data": character_data}
                    
                    # CRITICAL: Monitor response time to verify timeout fixes
                    start_time = time.time()
                    
                    # Set client timeout to 35 seconds (should complete within 30 seconds per requirement)
                    timeout = aiohttp.ClientTimeout(total=35)
                    
                    async with self.session.post(f"{BACKEND_URL}/analyze-trope-risk",
                                               json=test_payload,
                                               headers={"Content-Type": "application/json"},
                                               timeout=timeout) as response:
                        
                        end_time = time.time()
                        response_time = end_time - start_time
                        
                        if response.status == 200:
                            data = await response.json()
                            if data.get("success") and "trope_analysis" in data:
                                analysis = data["trope_analysis"]
                                
                                # Verify analysis structure
                                required_fields = ["overall_freshness_score", "marcus_level_rating", "trope_analyses", 
                                                 "improvement_suggestions", "freshness_rating"]
                                has_required = all(field in analysis for field in required_fields)
                                
                                # Verify trope analyses structure
                                trope_analyses = analysis.get("trope_analyses", [])
                                valid_tropes = all(
                                    all(field in trope for field in ["trope_name", "cliche_score", "freshness_level"])
                                    for trope in trope_analyses
                                ) if trope_analyses else True  # Empty is valid
                                
                                freshness_score = analysis.get("overall_freshness_score", 0)
                                marcus_rating = analysis.get("marcus_level_rating", 0)
                                
                                # CRITICAL: Verify timeout fix - should complete within 30 seconds
                                timeout_fixed = response_time <= 30.0
                                
                                if has_required and valid_tropes and timeout_fixed:
                                    self.log_result(f"Trope Risk Analysis ({char_name})", True, 
                                                  f"Analysis completed in {response_time:.1f}s (timeout fix working)", {
                                                      "response_time_seconds": round(response_time, 2),
                                                      "timeout_requirement_met": timeout_fixed,
                                                      "freshness_score": round(freshness_score, 3),
                                                      "marcus_rating": round(marcus_rating, 3),
                                                      "freshness_rating": analysis.get("freshness_rating"),
                                                      "tropes_found": len(trope_analyses),
                                                      "has_suggestions": len(analysis.get("improvement_suggestions", [])) > 0
                                                  })
                                elif not timeout_fixed:
                                    self.log_result(f"Trope Risk Analysis ({char_name})", False, 
                                                  f"TIMEOUT ISSUE: Response took {response_time:.1f}s (>30s limit)", {
                                                      "response_time_seconds": round(response_time, 2),
                                                      "timeout_requirement_met": False,
                                                      "timeout_limit": 30.0
                                                  })
                                else:
                                    self.log_result(f"Trope Risk Analysis ({char_name})", False, 
                                                  f"Invalid analysis structure (completed in {response_time:.1f}s)", {
                                                      "response_time_seconds": round(response_time, 2),
                                                      "has_required_fields": has_required,
                                                      "valid_tropes": valid_tropes,
                                                      "tropes_count": len(trope_analyses)
                                                  })
                            else:
                                self.log_result(f"Trope Risk Analysis ({char_name})", False, 
                                              f"Invalid response format (completed in {response_time:.1f}s)", {
                                                  "response_time_seconds": round(response_time, 2),
                                                  "response_data": data
                                              })
                        else:
                            error_text = await response.text()
                            self.log_result(f"Trope Risk Analysis ({char_name})", False, 
                                          f"HTTP {response.status} after {response_time:.1f}s", {
                                              "response_time_seconds": round(response_time, 2),
                                              "error": error_text
                                          })
                            
                except asyncio.TimeoutError:
                    self.log_result(f"Trope Risk Analysis ({char_name})", False, 
                                  "CRITICAL: Request timed out (>35s) - timeout fixes not working", {
                                      "timeout_seconds": 35,
                                      "issue": "Ollama enhancement still causing delays"
                                  })
                except Exception as e:
                    self.log_result(f"Trope Risk Analysis ({char_name})", False, 
                                  f"Request error: {str(e)}")
                    
        except Exception as e:
            self.log_result("Trope Risk Analysis (Overall)", False, f"Test setup error: {str(e)}")
    
    async def test_power_system_themes(self):
        """Test power system themes endpoint at /api/power-system-themes"""
        try:
            async with self.session.get(f"{BACKEND_URL}/power-system-themes") as response:
                if response.status == 200:
                    data = await response.json()
                    if "themes" in data and isinstance(data["themes"], list):
                        themes = data["themes"]
                        
                        # Verify expected themes (6 narrative themes)
                        expected_theme_ids = [
                            "identity_crisis", "power_corruption", "inherited_trauma",
                            "technological_anxiety", "social_stratification", "existential_purpose"
                        ]
                        
                        available_theme_ids = [theme["id"] for theme in themes]
                        themes_match = all(theme_id in available_theme_ids for theme_id in expected_theme_ids)
                        
                        # Verify theme structure
                        valid_structure = all(
                            all(field in theme for field in ["id", "name", "description", "examples"])
                            for theme in themes
                        ) if themes else False
                        
                        if themes_match and valid_structure and len(themes) == 6:
                            self.log_result("Power System Themes", True, "All 6 narrative themes available", {
                                "themes_count": len(themes),
                                "available_themes": available_theme_ids,
                                "structure_valid": valid_structure
                            })
                        else:
                            self.log_result("Power System Themes", False, "Missing expected themes or invalid structure", {
                                "expected_count": 6,
                                "actual_count": len(themes),
                                "themes_match": themes_match,
                                "structure_valid": valid_structure,
                                "available_themes": available_theme_ids
                            })
                    else:
                        self.log_result("Power System Themes", False, "Invalid response format", data)
                else:
                    error_text = await response.text()
                    self.log_result("Power System Themes", False, f"HTTP {response.status}", {"error": error_text})
        except Exception as e:
            self.log_result("Power System Themes", False, f"Request error: {str(e)}")
    
    async def test_power_system_generation(self):
        """Test advanced power system generation at /api/generate-power-system"""
        try:
            # Test configurations as specified in the review request
            test_configs = [
                {
                    "name": "Simple Request (Default)",
                    "payload": {}
                },
                {
                    "name": "With Theme",
                    "payload": {
                        "narrative_focus": "power_corruption",
                        "complexity_level": "moderate"
                    }
                },
                {
                    "name": "With Character Context",
                    "payload": {
                        "character_context": {
                            "character_origin": "enhanced",
                            "social_status": "entrepreneur"
                        },
                        "complexity_level": "complex"
                    }
                }
            ]
            
            success_count = 0
            for config in test_configs:
                try:
                    async with self.session.post(f"{BACKEND_URL}/generate-power-system",
                                               json=config["payload"],
                                               headers={"Content-Type": "application/json"}) as response:
                        if response.status == 200:
                            data = await response.json()
                            if data.get("success") and "power_system" in data:
                                power_system = data["power_system"]
                                
                                # Verify expected response structure
                                required_fields = [
                                    "power_source", "mechanic", "limitations", "progression",
                                    "power_metrics", "narrative_elements", "creative_suggestions"
                                ]
                                has_required = all(field in power_system for field in required_fields)
                                
                                # Verify power_source structure
                                power_source_valid = (
                                    "power_source" in power_system and
                                    all(field in power_system["power_source"] for field in ["type", "name", "description"])
                                )
                                
                                # Verify mechanic structure
                                mechanic_valid = (
                                    "mechanic" in power_system and
                                    all(field in power_system["mechanic"] for field in ["type", "name", "description"])
                                )
                                
                                # Verify limitations structure
                                limitations_valid = (
                                    "limitations" in power_system and
                                    "primary" in power_system["limitations"] and
                                    all(field in power_system["limitations"]["primary"] for field in ["type", "name", "description"])
                                )
                                
                                # Verify power metrics (6 numerical values 0.0-1.0)
                                power_metrics = power_system.get("power_metrics", {})
                                expected_metrics = [
                                    "raw_power_level", "control_precision", "cost_severity",
                                    "social_impact", "progression_speed", "uniqueness_factor"
                                ]
                                metrics_valid = (
                                    len(power_metrics) == 6 and
                                    all(metric in power_metrics for metric in expected_metrics) and
                                    all(0.0 <= power_metrics[metric] <= 1.0 for metric in expected_metrics)
                                )
                                
                                # Verify reasonable metric ranges (0.1-0.9 as specified)
                                metrics_reasonable = all(
                                    0.1 <= power_metrics[metric] <= 0.9 for metric in expected_metrics
                                ) if metrics_valid else False
                                
                                # Verify narrative elements
                                narrative_valid = (
                                    "narrative_elements" in power_system and
                                    all(field in power_system["narrative_elements"] for field in ["thematic_resonance", "societal_role", "philosophical_question"])
                                )
                                
                                # Verify creative suggestions (5 specific applications)
                                creative_suggestions = power_system.get("creative_suggestions", [])
                                suggestions_valid = isinstance(creative_suggestions, list) and len(creative_suggestions) == 5
                                
                                if (has_required and power_source_valid and mechanic_valid and 
                                    limitations_valid and metrics_valid and metrics_reasonable and 
                                    narrative_valid and suggestions_valid):
                                    success_count += 1
                                    self.log_result(f"Power System Generation ({config['name']})", True, 
                                                  "Complete power system generated successfully", {
                                                      "power_source": power_system["power_source"]["type"],
                                                      "mechanic": power_system["mechanic"]["type"],
                                                      "primary_limitation": power_system["limitations"]["primary"]["type"],
                                                      "has_secondary_limitation": power_system["limitations"].get("secondary") is not None,
                                                      "power_metrics_valid": metrics_valid,
                                                      "metrics_in_range": metrics_reasonable,
                                                      "creative_suggestions_count": len(creative_suggestions),
                                                      "thematic_coherence": bool(power_system["narrative_elements"]["thematic_resonance"])
                                                  })
                                else:
                                    self.log_result(f"Power System Generation ({config['name']})", False, 
                                                  "Invalid power system structure", {
                                                      "has_required_fields": has_required,
                                                      "power_source_valid": power_source_valid,
                                                      "mechanic_valid": mechanic_valid,
                                                      "limitations_valid": limitations_valid,
                                                      "metrics_valid": metrics_valid,
                                                      "metrics_reasonable": metrics_reasonable,
                                                      "narrative_valid": narrative_valid,
                                                      "suggestions_valid": suggestions_valid,
                                                      "suggestions_count": len(creative_suggestions)
                                                  })
                            else:
                                self.log_result(f"Power System Generation ({config['name']})", False, 
                                              "Invalid response format", data)
                        else:
                            error_text = await response.text()
                            self.log_result(f"Power System Generation ({config['name']})", False, 
                                          f"HTTP {response.status}", {"error": error_text})
                except Exception as e:
                    self.log_result(f"Power System Generation ({config['name']})", False, 
                                  f"Request error: {str(e)}")
            
            # Overall power system generation result
            if success_count == len(test_configs):
                self.log_result("Power System Generation (Overall)", True, 
                              f"All {success_count} configurations successful", {
                                  "tested_configs": len(test_configs),
                                  "successful": success_count
                              })
            else:
                self.log_result("Power System Generation (Overall)", False, 
                              f"Only {success_count}/{len(test_configs)} configurations successful", {
                                  "tested_configs": len(test_configs),
                                  "successful": success_count
                              })
                
        except Exception as e:
            self.log_result("Power System Generation (Overall)", False, f"Test setup error: {str(e)}")

    async def test_continuity_check(self):
        """Test continuity checking at /api/check-continuity - NEW PHASE 3A FEATURE"""
        try:
            # Test basic content continuity check
            basic_test = {
                "content": {
                    "text": "Character shoots fire from hands"
                }
            }
            
            async with self.session.post(f"{BACKEND_URL}/check-continuity",
                                       json=basic_test,
                                       headers={"Content-Type": "application/json"}) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "continuity_check" in data:
                        check_result = data["continuity_check"]
                        
                        # Verify expected structure
                        required_fields = ["total_violations", "critical_count", "high_count", 
                                         "medium_count", "low_count", "violations"]
                        has_required = all(field in check_result for field in required_fields)
                        
                        # Verify violations structure
                        violations = check_result.get("violations", [])
                        valid_violations = all(
                            all(field in violation for field in ["type", "severity", "title", 
                                                               "description", "affected_elements", "suggested_fixes"])
                            for violation in violations
                        ) if violations else True
                        
                        if has_required and valid_violations:
                            self.log_result("Continuity Check (Basic)", True, 
                                          f"Continuity analysis completed with {check_result['total_violations']} violations", {
                                              "total_violations": check_result["total_violations"],
                                              "critical_count": check_result["critical_count"],
                                              "high_count": check_result["high_count"],
                                              "medium_count": check_result["medium_count"],
                                              "low_count": check_result["low_count"],
                                              "structure_valid": valid_violations
                                          })
                        else:
                            self.log_result("Continuity Check (Basic)", False, "Invalid response structure", {
                                "has_required_fields": has_required,
                                "valid_violations": valid_violations
                            })
                    else:
                        self.log_result("Continuity Check (Basic)", False, "Invalid response format", data)
                else:
                    error_text = await response.text()
                    self.log_result("Continuity Check (Basic)", False, f"HTTP {response.status}", {"error": error_text})
            
            # Test with character context
            context_test = {
                "content": {
                    "text": "Character shoots fire from hands but also controls ice"
                },
                "context_characters": [
                    {
                        "id": "test-char-1",
                        "powers": ["fire_control"],
                        "limitations": ["cannot_use_ice"]
                    }
                ]
            }
            
            async with self.session.post(f"{BACKEND_URL}/check-continuity",
                                       json=context_test,
                                       headers={"Content-Type": "application/json"}) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "continuity_check" in data:
                        check_result = data["continuity_check"]
                        
                        # Should detect power inconsistency
                        has_violations = check_result["total_violations"] > 0
                        has_power_violations = any(
                            "power" in violation.get("type", "").lower() or 
                            "inconsistency" in violation.get("type", "").lower()
                            for violation in check_result.get("violations", [])
                        )
                        
                        if has_violations:
                            self.log_result("Continuity Check (Context)", True, 
                                          f"Detected power inconsistency violations as expected", {
                                              "total_violations": check_result["total_violations"],
                                              "detected_power_issues": has_power_violations,
                                              "violation_types": [v.get("type") for v in check_result.get("violations", [])]
                                          })
                        else:
                            self.log_result("Continuity Check (Context)", False, 
                                          "Failed to detect obvious power inconsistency", {
                                              "expected_violations": "> 0",
                                              "actual_violations": check_result["total_violations"]
                                          })
                    else:
                        self.log_result("Continuity Check (Context)", False, "Invalid response format", data)
                else:
                    error_text = await response.text()
                    self.log_result("Continuity Check (Context)", False, f"HTTP {response.status}", {"error": error_text})
                    
        except Exception as e:
            self.log_result("Continuity Check", False, f"Request error: {str(e)}")
    
    async def test_add_to_continuity(self):
        """Test adding to continuity database at /api/add-to-continuity - NEW PHASE 3A FEATURE"""
        try:
            # Test adding character data
            character_data = {
                "id": "test-continuity-char",
                "traits": [
                    {"trait": "Strategic mastermind", "category": "Mental"}
                ],
                "power_suggestions": [
                    {"name": "Hypercognitive Processing", "description": "Enhanced mental processing", "cost_level": 8}
                ],
                "backstory_seeds": [
                    "Former entrepreneur who gained cognitive enhancement"
                ],
                "relationships": [],
                "timeline": [],
                "genre": "urban_realistic"
            }
            
            test_payload = {"character_data": character_data}
            
            async with self.session.post(f"{BACKEND_URL}/add-to-continuity",
                                       json=test_payload,
                                       headers={"Content-Type": "application/json"}) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        self.log_result("Add to Continuity Database", True, 
                                      "Character successfully added to continuity database", {
                                          "character_id": character_data["id"],
                                          "message": data.get("message", "")
                                      })
                    else:
                        self.log_result("Add to Continuity Database", False, "Success flag not set", data)
                else:
                    error_text = await response.text()
                    self.log_result("Add to Continuity Database", False, f"HTTP {response.status}", {"error": error_text})
                    
        except Exception as e:
            self.log_result("Add to Continuity Database", False, f"Request error: {str(e)}")
    
    async def test_enhanced_style_analysis(self):
        """Test enhanced style analysis at /api/analyze-style-enhanced - NEW PHASE 3A FEATURE"""
        try:
            # Test with clichéd text
            cliche_test = {
                "text": "The enigmatic character delved into the tapestry of emotions, meticulously examining the mysterious figure who was nestled in the shadows."
            }
            
            async with self.session.post(f"{BACKEND_URL}/analyze-style-enhanced",
                                       json=cliche_test,
                                       headers={"Content-Type": "application/json"}) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "style_analysis" in data:
                        analysis = data["style_analysis"]
                        
                        # Verify expected structure
                        required_fields = ["overall_score", "readability_score", "engagement_score", 
                                         "professionalism_score", "total_issues", "issues", 
                                         "strengths", "improvement_summary", "educational_notes"]
                        has_required = all(field in analysis for field in required_fields)
                        
                        # Verify issues structure with educational components
                        issues = analysis.get("issues", [])
                        valid_issues = all(
                            all(field in issue for field in ["type", "severity", "title", "explanation",
                                                           "problematic_text", "suggested_revision", 
                                                           "reasoning", "examples", "learning_resources"])
                            for issue in issues
                        ) if issues else True
                        
                        # Should detect clichés in the test text
                        has_cliche_issues = any(
                            "cliche" in issue.get("type", "").lower() or
                            any(cliche in issue.get("problematic_text", "").lower() 
                                for cliche in ["enigmatic", "delved", "tapestry", "nestled", "meticulous"])
                            for issue in issues
                        )
                        
                        # Check for educational value
                        has_reasoning = all(issue.get("reasoning") for issue in issues) if issues else True
                        has_examples = all(issue.get("examples") for issue in issues) if issues else True
                        has_learning_resources = all(issue.get("learning_resources") for issue in issues) if issues else True
                        
                        if has_required and valid_issues and has_cliche_issues:
                            self.log_result("Enhanced Style Analysis (Clichés)", True, 
                                          f"Detected {len(issues)} style issues with educational rationale", {
                                              "total_issues": analysis["total_issues"],
                                              "overall_score": round(analysis["overall_score"], 3),
                                              "detected_cliches": has_cliche_issues,
                                              "has_reasoning": has_reasoning,
                                              "has_examples": has_examples,
                                              "has_learning_resources": has_learning_resources,
                                              "issue_types": [issue.get("type") for issue in issues]
                                          })
                        else:
                            self.log_result("Enhanced Style Analysis (Clichés)", False, 
                                          "Failed to detect clichés or missing educational components", {
                                              "has_required_fields": has_required,
                                              "valid_issues": valid_issues,
                                              "detected_cliches": has_cliche_issues,
                                              "issues_count": len(issues)
                                          })
                    else:
                        self.log_result("Enhanced Style Analysis (Clichés)", False, "Invalid response format", data)
                else:
                    error_text = await response.text()
                    self.log_result("Enhanced Style Analysis (Clichés)", False, f"HTTP {response.status}", {"error": error_text})
            
            # Test with passive voice
            passive_test = {
                "text": "The door was opened by the mysterious figure. The secret was discovered by the protagonist."
            }
            
            async with self.session.post(f"{BACKEND_URL}/analyze-style-enhanced",
                                       json=passive_test,
                                       headers={"Content-Type": "application/json"}) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "style_analysis" in data:
                        analysis = data["style_analysis"]
                        issues = analysis.get("issues", [])
                        
                        # Should detect passive voice
                        has_passive_issues = any(
                            "passive" in issue.get("type", "").lower()
                            for issue in issues
                        )
                        
                        if has_passive_issues:
                            self.log_result("Enhanced Style Analysis (Passive Voice)", True, 
                                          "Detected passive voice issues with educational explanations", {
                                              "total_issues": analysis["total_issues"],
                                              "detected_passive_voice": has_passive_issues,
                                              "issue_types": [issue.get("type") for issue in issues]
                                          })
                        else:
                            self.log_result("Enhanced Style Analysis (Passive Voice)", False, 
                                          "Failed to detect obvious passive voice", {
                                              "expected": "passive voice detection",
                                              "issues_found": len(issues),
                                              "issue_types": [issue.get("type") for issue in issues]
                                          })
                    else:
                        self.log_result("Enhanced Style Analysis (Passive Voice)", False, "Invalid response format", data)
                else:
                    error_text = await response.text()
                    self.log_result("Enhanced Style Analysis (Passive Voice)", False, f"HTTP {response.status}", {"error": error_text})
            
            # Test with telling vs showing
            telling_test = {
                "text": "She was angry and felt nervous. He was a tall man who seemed mysterious."
            }
            
            async with self.session.post(f"{BACKEND_URL}/analyze-style-enhanced",
                                       json=telling_test,
                                       headers={"Content-Type": "application/json"}) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "style_analysis" in data:
                        analysis = data["style_analysis"]
                        issues = analysis.get("issues", [])
                        
                        # Should detect telling vs showing issues
                        has_telling_issues = any(
                            "telling" in issue.get("type", "").lower() or
                            "showing" in issue.get("type", "").lower()
                            for issue in issues
                        )
                        
                        if has_telling_issues:
                            self.log_result("Enhanced Style Analysis (Telling vs Showing)", True, 
                                          "Detected telling vs showing issues with educational guidance", {
                                              "total_issues": analysis["total_issues"],
                                              "detected_telling_issues": has_telling_issues,
                                              "issue_types": [issue.get("type") for issue in issues]
                                          })
                        else:
                            self.log_result("Enhanced Style Analysis (Telling vs Showing)", False, 
                                          "Failed to detect telling vs showing issues", {
                                              "expected": "telling vs showing detection",
                                              "issues_found": len(issues),
                                              "issue_types": [issue.get("type") for issue in issues]
                                          })
                    else:
                        self.log_result("Enhanced Style Analysis (Telling vs Showing)", False, "Invalid response format", data)
                else:
                    error_text = await response.text()
                    self.log_result("Enhanced Style Analysis (Telling vs Showing)", False, f"HTTP {response.status}", {"error": error_text})
                    
        except Exception as e:
            self.log_result("Enhanced Style Analysis", False, f"Request error: {str(e)}")
    
    async def test_style_coach_help(self):
        """Test style coach help at /api/style-coach-help - NEW PHASE 3A FEATURE"""
        try:
            async with self.session.get(f"{BACKEND_URL}/style-coach-help") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "educational_resources" in data and "issue_types" in data:
                        educational_resources = data["educational_resources"]
                        issue_types = data["issue_types"]
                        
                        # Verify issue types structure
                        expected_issue_types = [
                            "cliche_language", "telling_not_showing", "passive_voice", 
                            "weak_verbs", "filter_words", "ai_telltales"
                        ]
                        
                        available_types = [issue_type.get("type") for issue_type in issue_types]
                        types_match = all(expected_type in available_types for expected_type in expected_issue_types)
                        
                        # Verify issue type structure
                        valid_structure = all(
                            all(field in issue_type for field in ["type", "name", "description"])
                            for issue_type in issue_types
                        ) if issue_types else False
                        
                        if types_match and valid_structure and educational_resources:
                            self.log_result("Style Coach Help", True, 
                                          f"Educational resources and {len(issue_types)} issue types available", {
                                              "issue_types_count": len(issue_types),
                                              "available_types": available_types,
                                              "has_educational_resources": bool(educational_resources),
                                              "structure_valid": valid_structure
                                          })
                        else:
                            self.log_result("Style Coach Help", False, 
                                          "Missing expected issue types or invalid structure", {
                                              "types_match": types_match,
                                              "structure_valid": valid_structure,
                                              "has_resources": bool(educational_resources),
                                              "available_types": available_types
                                          })
                    else:
                        self.log_result("Style Coach Help", False, "Invalid response format", data)
                else:
                    error_text = await response.text()
                    self.log_result("Style Coach Help", False, f"HTTP {response.status}", {"error": error_text})
                    
        except Exception as e:
            self.log_result("Style Coach Help", False, f"Request error: {str(e)}")

    async def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting VisionForge Backend Tests - Phase 3A Continuity Engine & Enhanced Style Coach")
        print(f"Testing against: {BACKEND_URL}")
        print("=" * 60)
        
        # Run existing tests first
        print("📋 EXISTING FEATURES:")
        await self.test_health_check()
        await self.test_get_genres()
        await self.test_ollama_models_availability()
        await self.test_text_generation()
        await self.test_style_analysis()
        await self.test_image_analysis()  # Most complex test
        await self.test_analyses_history()
        
        print("\n🆕 PHASE 2 FEATURES:")
        # Run Phase 2 tests
        await self.test_beat_sheet_types()
        await self.test_beat_sheet_generation()
        await self.test_trope_risk_analysis()
        
        print("\n🔥 ADVANCED POWER SYSTEM FRAMEWORK:")
        # Run Power System Framework tests
        await self.test_power_system_themes()
        await self.test_power_system_generation()
        
        print("\n🎯 NEW PHASE 3A FEATURES - CONTINUITY ENGINE & ENHANCED STYLE COACH:")
        # Run new Phase 3A tests
        await self.test_continuity_check()
        await self.test_add_to_continuity()
        await self.test_enhanced_style_analysis()
        await self.test_style_coach_help()
        
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
        
        # Separate existing vs Phase 2 vs Power System vs Phase 3A results
        existing_tests = [r for r in self.test_results if not any(feature in r["test"] for feature in ["Beat Sheet", "Trope Risk", "Power System", "Continuity", "Enhanced Style", "Style Coach"])]
        phase2_tests = [r for r in self.test_results if any(phase2 in r["test"] for phase2 in ["Beat Sheet", "Trope Risk"])]
        power_system_tests = [r for r in self.test_results if "Power System" in r["test"]]
        phase3a_tests = [r for r in self.test_results if any(phase3a in r["test"] for phase3a in ["Continuity", "Enhanced Style", "Style Coach"])]
        
        existing_passed = sum(1 for r in existing_tests if r["success"])
        phase2_passed = sum(1 for r in phase2_tests if r["success"])
        power_system_passed = sum(1 for r in power_system_tests if r["success"])
        phase3a_passed = sum(1 for r in phase3a_tests if r["success"])
        
        print(f"\n📋 EXISTING FEATURES: {existing_passed}/{len(existing_tests)} passed")
        print(f"🆕 PHASE 2 FEATURES: {phase2_passed}/{len(phase2_tests)} passed")
        print(f"🔥 POWER SYSTEM FRAMEWORK: {power_system_passed}/{len(power_system_tests)} passed")
        print(f"🎯 PHASE 3A FEATURES: {phase3a_passed}/{len(phase3a_tests)} passed")
        
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