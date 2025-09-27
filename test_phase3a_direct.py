#!/usr/bin/env python3
"""
Direct test of Phase 3A endpoints to verify they exist and work
"""

import asyncio
import aiohttp
import json

BACKEND_URL = "https://storycraft-102.preview.emergentagent.com/api"

async def test_new_continuity_endpoint():
    """Test the new Phase 3A continuity endpoint directly"""
    async with aiohttp.ClientSession() as session:
        # Test the new continuity check format
        test_data = {
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
        
        print("Testing new Phase 3A continuity endpoint...")
        async with session.post(f"{BACKEND_URL}/check-continuity-advanced", 
                              json=test_data,
                              headers={"Content-Type": "application/json"}) as response:
            print(f"Status: {response.status}")
            data = await response.json()
            print(f"Response: {json.dumps(data, indent=2)}")

async def test_enhanced_style_endpoint():
    """Test the enhanced style analysis endpoint"""
    async with aiohttp.ClientSession() as session:
        test_data = {
            "text": "The enigmatic character delved into the tapestry of emotions",
            "focus_areas": ["cliche_language", "passive_voice"]
        }
        
        print("\nTesting enhanced style analysis endpoint...")
        async with session.post(f"{BACKEND_URL}/analyze-style-enhanced",
                              json=test_data,
                              headers={"Content-Type": "application/json"}) as response:
            print(f"Status: {response.status}")
            data = await response.json()
            print(f"Response keys: {list(data.keys())}")
            if "style_analysis" in data:
                analysis = data["style_analysis"]
                print(f"Issues found: {analysis.get('total_issues', 0)}")
                print(f"Overall score: {analysis.get('overall_score', 0)}")

if __name__ == "__main__":
    asyncio.run(test_new_continuity_endpoint())
    asyncio.run(test_enhanced_style_endpoint())