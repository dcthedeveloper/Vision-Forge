#!/usr/bin/env python3
"""
Quick Phase 2 Feature Tests for VisionForge
"""

import asyncio
import aiohttp
import json

BACKEND_URL = "https://character-craft-5.preview.emergentagent.com/api"

async def test_phase2_features():
    """Test Phase 2 features quickly"""
    async with aiohttp.ClientSession() as session:
        results = []
        
        # Test 1: Beat Sheet Types
        print("🧪 Testing Beat Sheet Types...")
        try:
            async with session.get(f"{BACKEND_URL}/beat-sheet-types") as response:
                if response.status == 200:
                    data = await response.json()
                    if "sheet_types" in data and "tone_pacing" in data:
                        print("✅ Beat Sheet Types: Working")
                        results.append(("Beat Sheet Types", True, f"Found {len(data['sheet_types'])} types"))
                    else:
                        print("❌ Beat Sheet Types: Invalid format")
                        results.append(("Beat Sheet Types", False, "Invalid response format"))
                else:
                    print(f"❌ Beat Sheet Types: HTTP {response.status}")
                    results.append(("Beat Sheet Types", False, f"HTTP {response.status}"))
        except Exception as e:
            print(f"❌ Beat Sheet Types: {e}")
            results.append(("Beat Sheet Types", False, str(e)))
        
        # Test 2: Beat Sheet Generation
        print("🧪 Testing Beat Sheet Generation...")
        try:
            payload = {
                "sheet_type": "save_the_cat",
                "tone_pacing": "standard", 
                "story_length": 110
            }
            async with session.post(f"{BACKEND_URL}/generate-beat-sheet", 
                                  json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "beat_sheet" in data:
                        beat_sheet = data["beat_sheet"]
                        beats_count = len(beat_sheet.get("beats", []))
                        print(f"✅ Beat Sheet Generation: Working ({beats_count} beats)")
                        results.append(("Beat Sheet Generation", True, f"{beats_count} beats generated"))
                    else:
                        print("❌ Beat Sheet Generation: Invalid response")
                        results.append(("Beat Sheet Generation", False, "Invalid response"))
                else:
                    error = await response.text()
                    print(f"❌ Beat Sheet Generation: HTTP {response.status}")
                    results.append(("Beat Sheet Generation", False, f"HTTP {response.status}: {error[:100]}"))
        except Exception as e:
            print(f"❌ Beat Sheet Generation: {e}")
            results.append(("Beat Sheet Generation", False, str(e)))
        
        # Test 3: Trope Risk Analysis (simplified)
        print("🧪 Testing Trope Risk Analysis...")
        try:
            payload = {
                "character_data": {
                    "id": "test-char",
                    "character_origin": "nootropic_enhanced",
                    "power_source": "nootropic_drug",
                    "traits": [{"trait": "Enhanced cognition"}],
                    "power_suggestions": [{"name": "Hypercognitive Processing"}]
                }
            }
            
            # Set a timeout for this request
            timeout = aiohttp.ClientTimeout(total=30)
            async with session.post(f"{BACKEND_URL}/analyze-trope-risk", 
                                  json=payload, timeout=timeout) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "trope_analysis" in data:
                        analysis = data["trope_analysis"]
                        freshness = analysis.get("overall_freshness_score", 0)
                        print(f"✅ Trope Risk Analysis: Working (freshness: {freshness:.2f})")
                        results.append(("Trope Risk Analysis", True, f"Freshness score: {freshness:.2f}"))
                    else:
                        print("❌ Trope Risk Analysis: Invalid response")
                        results.append(("Trope Risk Analysis", False, "Invalid response"))
                else:
                    error = await response.text()
                    print(f"❌ Trope Risk Analysis: HTTP {response.status}")
                    results.append(("Trope Risk Analysis", False, f"HTTP {response.status}: {error[:100]}"))
        except asyncio.TimeoutError:
            print("❌ Trope Risk Analysis: Timeout (>30s)")
            results.append(("Trope Risk Analysis", False, "Timeout - likely Ollama processing delay"))
        except Exception as e:
            print(f"❌ Trope Risk Analysis: {e}")
            results.append(("Trope Risk Analysis", False, str(e)))
        
        # Summary
        print("\n" + "="*50)
        print("📊 PHASE 2 TEST SUMMARY")
        print("="*50)
        
        passed = sum(1 for _, success, _ in results if success)
        total = len(results)
        
        for test_name, success, details in results:
            status = "✅" if success else "❌"
            print(f"{status} {test_name}: {details}")
        
        print(f"\nPassed: {passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        return results

if __name__ == "__main__":
    asyncio.run(test_phase2_features())