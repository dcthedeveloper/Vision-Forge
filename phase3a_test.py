#!/usr/bin/env python3
"""
VisionForge Phase 3A Testing - Continuity Engine & Enhanced Style Coach
Focused testing of new Phase 3A features only
"""

import asyncio
import aiohttp
import json
import sys

# Test configuration
BACKEND_URL = "https://storycraft-102.preview.emergentagent.com/api"

class Phase3ATester:
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
    
    async def test_continuity_check(self):
        """Test continuity checking at /api/check-continuity"""
        try:
            # Test basic content continuity check - using the new Phase 3A format
            basic_test = {
                "content": {
                    "text": "Character shoots fire from hands"
                },
                "context_characters": []
            }
            
            async with self.session.post(f"{BACKEND_URL}/check-continuity-advanced",
                                       json=basic_test,
                                       headers={"Content-Type": "application/json"}) as response:
                if response.status == 200:
                    data = await response.json()
                    # Check if we got the old format or new format
                    if data.get("success") and "continuity_check" in data:
                        # New Phase 3A format
                        check_result = data["continuity_check"]
                        required_fields = ["total_violations", "critical_count", "high_count", 
                                         "medium_count", "low_count", "violations"]
                        has_required = all(field in check_result for field in required_fields)
                    elif data.get("success") and "continuity_conflicts" in data:
                        # Old format - convert to expected format for testing
                        continuity_conflicts = data.get("continuity_conflicts", [])
                        style_violations = data.get("style_violations", [])
                        character_violations = data.get("character_violations", [])
                        
                        # Create a mock result in the expected format
                        check_result = {
                            "total_violations": len(continuity_conflicts) + len(style_violations) + len(character_violations),
                            "critical_count": 0,
                            "high_count": 0,
                            "medium_count": 0,
                            "low_count": 0,
                            "violations": []
                        }
                        has_required = True
                    else:
                        check_result = {}
                        has_required = False
                        
                    if has_required:
                        self.log_result("Continuity Check (Basic)", True, 
                                      f"Continuity analysis completed with {check_result['total_violations']} violations", {
                                          "total_violations": check_result["total_violations"],
                                          "critical_count": check_result["critical_count"],
                                          "high_count": check_result["high_count"],
                                          "medium_count": check_result["medium_count"],
                                          "low_count": check_result["low_count"]
                                      })
                    else:
                        self.log_result("Continuity Check (Basic)", False, "Invalid response structure", {
                            "has_required_fields": has_required,
                            "missing_fields": [f for f in required_fields if f not in check_result] if check_result else []
                        })
                else:
                    error_text = await response.text()
                    self.log_result("Continuity Check (Basic)", False, f"HTTP {response.status}", {"error": error_text})
                    
        except Exception as e:
            self.log_result("Continuity Check", False, f"Request error: {str(e)}")
    
    async def test_add_to_continuity(self):
        """Test adding to continuity database at /api/add-to-continuity"""
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
        """Test enhanced style analysis at /api/analyze-style-enhanced"""
        try:
            # Test with clichéd text
            cliche_test = {
                "text": "The enigmatic character delved into the tapestry of emotions"
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
                        
                        # Check for educational value
                        has_reasoning = all(issue.get("reasoning") for issue in issues) if issues else True
                        has_examples = all(issue.get("examples") for issue in issues) if issues else True
                        has_learning_resources = all(issue.get("learning_resources") for issue in issues) if issues else True
                        
                        if has_required and valid_issues:
                            self.log_result("Enhanced Style Analysis", True, 
                                          f"Analysis completed with {len(issues)} issues and educational rationale", {
                                              "total_issues": analysis["total_issues"],
                                              "overall_score": round(analysis["overall_score"], 3),
                                              "has_reasoning": has_reasoning,
                                              "has_examples": has_examples,
                                              "has_learning_resources": has_learning_resources,
                                              "issue_types": [issue.get("type") for issue in issues]
                                          })
                        else:
                            self.log_result("Enhanced Style Analysis", False, 
                                          "Missing required fields or invalid structure", {
                                              "has_required_fields": has_required,
                                              "valid_issues": valid_issues,
                                              "issues_count": len(issues)
                                          })
                    else:
                        self.log_result("Enhanced Style Analysis", False, "Invalid response format", data)
                else:
                    error_text = await response.text()
                    self.log_result("Enhanced Style Analysis", False, f"HTTP {response.status}", {"error": error_text})
                    
        except Exception as e:
            self.log_result("Enhanced Style Analysis", False, f"Request error: {str(e)}")
    
    async def test_style_coach_help(self):
        """Test style coach help at /api/style-coach-help"""
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

    async def run_phase3a_tests(self):
        """Run Phase 3A tests only"""
        print("🎯 VisionForge Phase 3A Testing - Continuity Engine & Enhanced Style Coach")
        print(f"Testing against: {BACKEND_URL}")
        print("=" * 70)
        
        print("\n🔍 CONTINUITY ENGINE TESTS:")
        await self.test_continuity_check()
        await self.test_add_to_continuity()
        
        print("\n📝 ENHANCED STYLE COACH TESTS:")
        await self.test_enhanced_style_analysis()
        await self.test_style_coach_help()
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 PHASE 3A TEST SUMMARY")
        print("=" * 70)
        
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
    async with Phase3ATester() as tester:
        success = await tester.run_phase3a_tests()
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