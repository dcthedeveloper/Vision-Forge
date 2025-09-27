#!/usr/bin/env python3
"""
Quick endpoint test for VisionForge - Final comprehensive test
"""
import requests
import json
import time

BACKEND_URL = "https://storycraft-102.preview.emergentagent.com/api"

def test_endpoint(name, method, url, data=None, timeout=30):
    """Test a single endpoint with timeout"""
    try:
        start_time = time.time()
        
        if method == "GET":
            response = requests.get(url, timeout=timeout)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=timeout)
        
        end_time = time.time()
        response_time = end_time - start_time
        
        if response.status_code == 200:
            try:
                json_data = response.json()
                return {
                    "name": name,
                    "status": "✅ PASS",
                    "response_time": f"{response_time:.1f}s",
                    "details": json_data if isinstance(json_data, dict) and len(str(json_data)) < 200 else "Response received"
                }
            except:
                return {
                    "name": name,
                    "status": "✅ PASS",
                    "response_time": f"{response_time:.1f}s",
                    "details": "Non-JSON response"
                }
        else:
            return {
                "name": name,
                "status": "❌ FAIL",
                "response_time": f"{response_time:.1f}s",
                "details": f"HTTP {response.status_code}"
            }
    except requests.exceptions.Timeout:
        return {
            "name": name,
            "status": "❌ TIMEOUT",
            "response_time": f">{timeout}s",
            "details": "Request timed out"
        }
    except Exception as e:
        return {
            "name": name,
            "status": "❌ ERROR",
            "response_time": "N/A",
            "details": str(e)
        }

def main():
    print("🚀 VisionForge Final Comprehensive Test - All 9 Endpoints")
    print("=" * 60)
    
    # Define all 9 endpoints to test
    tests = [
        # CORE ENDPOINTS (6)
        ("1. Health Check", "GET", f"{BACKEND_URL}/"),
        ("2. Genres", "GET", f"{BACKEND_URL}/genres"),
        ("3. Text Generation", "POST", f"{BACKEND_URL}/generate-text", {
            "prompt": "Test character creation",
            "generation_type": "character"
        }),
        ("4. Style Analysis", "POST", f"{BACKEND_URL}/analyze-style", {
            "text": "The mysterious figure delved into the enigmatic tapestry"
        }),
        ("5. Analysis History", "GET", f"{BACKEND_URL}/analyses"),
        
        # PHASE 2 ENDPOINTS (3)
        ("6. Beat Sheet Types", "GET", f"{BACKEND_URL}/beat-sheet-types"),
        ("7. Beat Sheet Generation", "POST", f"{BACKEND_URL}/generate-beat-sheet", {
            "sheet_type": "save_the_cat",
            "tone_pacing": "standard",
            "story_length": 110
        }),
        ("8. Trope Risk Analysis", "POST", f"{BACKEND_URL}/analyze-trope-risk", {
            "character_data": {
                "id": "test-character",
                "character_origin": "nootropic_enhanced",
                "power_source": "nootropic_drug",
                "traits": [{"trait": "Strategic mastermind"}],
                "backstory_seeds": ["Enhanced entrepreneur"],
                "power_suggestions": [{"name": "Hypercognitive Processing", "description": "Enhanced thinking", "cost_level": 8}]
            }
        })
    ]
    
    # Note: Image analysis (#3) requires multipart form data, testing separately
    
    results = []
    
    # Test each endpoint
    for test_name, method, url, data in tests:
        print(f"Testing {test_name}...")
        
        # Special timeout for trope analysis (should complete within 30s per requirement)
        timeout = 35 if "Trope Risk" in test_name else 30
        
        result = test_endpoint(test_name, method, url, data, timeout)
        results.append(result)
        
        print(f"  {result['status']} - {result['response_time']} - {result['details']}")
    
    # Test image analysis separately (requires multipart form)
    print("Testing 9. Image Analysis...")
    try:
        # Create a simple test image
        import io
        from PIL import Image
        img = Image.new('RGB', (100, 100), color='blue')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        files = {'file': ('test.jpg', img_bytes, 'image/jpeg')}
        data = {
            'genre': 'urban_realistic',
            'origin': 'nootropic_enhanced',
            'social_status': 'entrepreneurial',
            'power_source': 'nootropic_drug',
            'op_mode': 'false'
        }
        
        start_time = time.time()
        response = requests.post(f"{BACKEND_URL}/analyze-image", files=files, data=data, timeout=60)
        end_time = time.time()
        response_time = end_time - start_time
        
        if response.status_code == 200:
            result = {
                "name": "9. Image Analysis",
                "status": "✅ PASS",
                "response_time": f"{response_time:.1f}s",
                "details": "Image analysis completed"
            }
        else:
            result = {
                "name": "9. Image Analysis",
                "status": "❌ FAIL",
                "response_time": f"{response_time:.1f}s",
                "details": f"HTTP {response.status_code}"
            }
    except Exception as e:
        result = {
            "name": "9. Image Analysis",
            "status": "❌ ERROR",
            "response_time": "N/A",
            "details": str(e)
        }
    
    results.append(result)
    print(f"  {result['status']} - {result['response_time']} - {result['details']}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 FINAL TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for r in results if r["status"] == "✅ PASS")
    total = len(results)
    
    print(f"Total Endpoints: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    # Detailed results
    print("\n🔍 DETAILED RESULTS:")
    for result in results:
        print(f"{result['status']} {result['name']} ({result['response_time']})")
        if result['status'] != "✅ PASS":
            print(f"    Issue: {result['details']}")
    
    # Special focus on timeout fixes
    trope_result = next((r for r in results if "Trope Risk" in r["name"]), None)
    if trope_result:
        print(f"\n🎯 TIMEOUT FIX VERIFICATION:")
        if trope_result["status"] == "✅ PASS":
            response_time = float(trope_result["response_time"].replace("s", ""))
            if response_time <= 30.0:
                print(f"✅ Trope analysis completed in {response_time:.1f}s (≤30s requirement met)")
            else:
                print(f"⚠️ Trope analysis took {response_time:.1f}s (>30s - timeout fix needs improvement)")
        else:
            print(f"❌ Trope analysis failed: {trope_result['details']}")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)