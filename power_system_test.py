#!/usr/bin/env python3
"""
Minimal Power System Framework Test
Tests only the new power system endpoints without triggering heavy Ollama usage
"""

import asyncio
import aiohttp
import json
import sys

BACKEND_URL = "https://storycraft-102.preview.emergentagent.com/api"

async def test_power_system_themes():
    """Test power system themes endpoint"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BACKEND_URL}/power-system-themes") as response:
                if response.status == 200:
                    data = await response.json()
                    if "themes" in data and isinstance(data["themes"], list):
                        themes = data["themes"]
                        expected_theme_ids = [
                            "identity_crisis", "power_corruption", "inherited_trauma",
                            "technological_anxiety", "social_stratification", "existential_purpose"
                        ]
                        available_theme_ids = [theme["id"] for theme in themes]
                        themes_match = all(theme_id in available_theme_ids for theme_id in expected_theme_ids)
                        
                        if themes_match and len(themes) == 6:
                            print("✅ Power System Themes: All 6 narrative themes available")
                            print(f"   Available themes: {available_theme_ids}")
                            return True
                        else:
                            print(f"❌ Power System Themes: Expected 6 themes, got {len(themes)}")
                            print(f"   Available: {available_theme_ids}")
                            return False
                    else:
                        print("❌ Power System Themes: Invalid response format")
                        return False
                else:
                    print(f"❌ Power System Themes: HTTP {response.status}")
                    return False
    except Exception as e:
        print(f"❌ Power System Themes: Error - {str(e)}")
        return False

async def test_power_system_generation():
    """Test power system generation with simple request"""
    try:
        async with aiohttp.ClientSession() as session:
            # Test simple request first (should not trigger heavy Ollama usage)
            simple_payload = {}
            
            async with session.post(f"{BACKEND_URL}/generate-power-system",
                                   json=simple_payload,
                                   headers={"Content-Type": "application/json"}) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "power_system" in data:
                        power_system = data["power_system"]
                        
                        # Check required structure
                        required_fields = [
                            "power_source", "mechanic", "limitations", "progression",
                            "power_metrics", "narrative_elements", "creative_suggestions"
                        ]
                        has_required = all(field in power_system for field in required_fields)
                        
                        # Check power metrics (6 values 0.0-1.0)
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
                        
                        # Check creative suggestions
                        creative_suggestions = power_system.get("creative_suggestions", [])
                        suggestions_valid = isinstance(creative_suggestions, list) and len(creative_suggestions) == 5
                        
                        if has_required and metrics_valid and suggestions_valid:
                            print("✅ Power System Generation: Complete power system generated")
                            print(f"   Power Source: {power_system['power_source']['type']}")
                            print(f"   Mechanic: {power_system['mechanic']['type']}")
                            print(f"   Primary Limitation: {power_system['limitations']['primary']['type']}")
                            print(f"   Power Metrics: {len(power_metrics)} values in valid range")
                            print(f"   Creative Suggestions: {len(creative_suggestions)} applications")
                            return True
                        else:
                            print("❌ Power System Generation: Invalid structure")
                            print(f"   Required fields: {has_required}")
                            print(f"   Metrics valid: {metrics_valid}")
                            print(f"   Suggestions valid: {suggestions_valid}")
                            return False
                    else:
                        print("❌ Power System Generation: Invalid response format")
                        return False
                else:
                    error_text = await response.text()
                    print(f"❌ Power System Generation: HTTP {response.status}")
                    print(f"   Error: {error_text}")
                    return False
    except Exception as e:
        print(f"❌ Power System Generation: Error - {str(e)}")
        return False

async def main():
    """Run power system tests"""
    print("🔥 Testing Advanced Power System Framework")
    print("=" * 50)
    
    # Test themes endpoint
    themes_success = await test_power_system_themes()
    
    # Test generation endpoint
    generation_success = await test_power_system_generation()
    
    print("\n" + "=" * 50)
    print("📊 POWER SYSTEM TEST SUMMARY")
    print("=" * 50)
    
    total_tests = 2
    passed_tests = sum([themes_success, generation_success])
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 All Power System Framework tests PASSED!")
        return True
    else:
        print(f"\n⚠️ {total_tests - passed_tests} test(s) FAILED")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test error: {e}")
        sys.exit(1)