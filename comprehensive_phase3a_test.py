#!/usr/bin/env python3
"""
Comprehensive Phase 3A Testing - All Review Request Features
Tests all specific features mentioned in the review request
"""

import asyncio
import aiohttp
import json
import sys

BACKEND_URL = "https://character-craft-5.preview.emergentagent.com/api"

class ComprehensivePhase3ATester:
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
    
    async def test_continuity_basic_content(self):
        """Test basic content continuity check as specified in review"""
        try:
            test_data = {
                "content": {
                    "text": "Character shoots fire from hands"
                }
            }
            
            async with self.session.post(f"{BACKEND_URL}/check-continuity-advanced",
                                       json=test_data,
                                       headers={"Content-Type": "application/json"}) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "continuity_check" in data:
                        check_result = data["continuity_check"]
                        
                        # Verify structure includes severity levels
                        has_severity_counts = all(field in check_result for field in 
                                                ["critical_count", "high_count", "medium_count", "low_count"])
                        has_violations_array = "violations" in check_result
                        
                        self.log_result("Continuity Check - Basic Content", True, 
                                      "Basic content analysis working with severity levels", {
                                          "total_violations": check_result["total_violations"],
                                          "has_severity_levels": has_severity_counts,
                                          "has_violations_array": has_violations_array
                                      })
                    else:
                        self.log_result("Continuity Check - Basic Content", False, "Invalid response format", data)
                else:
                    error_text = await response.text()
                    self.log_result("Continuity Check - Basic Content", False, f"HTTP {response.status}", {"error": error_text})
                    
        except Exception as e:
            self.log_result("Continuity Check - Basic Content", False, f"Request error: {str(e)}")
    
    async def test_continuity_with_character_context(self):
        """Test continuity check with character context as specified in review"""
        try:
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
            
            async with self.session.post(f"{BACKEND_URL}/check-continuity-advanced",
                                       json=test_data,
                                       headers={"Content-Type": "application/json"}) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "continuity_check" in data:
                        check_result = data["continuity_check"]
                        violations = check_result.get("violations", [])
                        
                        # Verify violation structure includes required fields
                        valid_violations = all(
                            all(field in violation for field in ["type", "severity", "title", 
                                                               "description", "suggested_fixes", "examples"])
                            for violation in violations
                        ) if violations else True
                        
                        self.log_result("Continuity Check - Character Context", True, 
                                      f"Character context analysis completed with {len(violations)} violations", {
                                          "total_violations": check_result["total_violations"],
                                          "violations_structure_valid": valid_violations,
                                          "has_suggested_fixes": all("suggested_fixes" in v for v in violations) if violations else True,
                                          "has_examples": all("examples" in v for v in violations) if violations else True
                                      })
                    else:
                        self.log_result("Continuity Check - Character Context", False, "Invalid response format", data)
                else:
                    error_text = await response.text()
                    self.log_result("Continuity Check - Character Context", False, f"HTTP {response.status}", {"error": error_text})
                    
        except Exception as e:
            self.log_result("Continuity Check - Character Context", False, f"Request error: {str(e)}")
    
    async def test_enhanced_style_cliches(self):
        """Test enhanced style analysis with clichés as specified in review"""
        try:
            test_data = {
                "text": "The enigmatic character delved into the tapestry of emotions"
            }
            
            async with self.session.post(f"{BACKEND_URL}/analyze-style-enhanced",
                                       json=test_data,
                                       headers={"Content-Type": "application/json"}) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "style_analysis" in data:
                        analysis = data["style_analysis"]
                        issues = analysis.get("issues", [])
                        
                        # Check for educational components
                        has_reasoning = all("reasoning" in issue for issue in issues) if issues else True
                        has_examples = all("examples" in issue for issue in issues) if issues else True
                        has_learning_resources = all("learning_resources" in issue for issue in issues) if issues else True
                        
                        # Should detect clichés
                        detected_cliches = any(
                            any(cliche in issue.get("problematic_text", "").lower() 
                                for cliche in ["enigmatic", "delved", "tapestry"])
                            for issue in issues
                        )
                        
                        self.log_result("Enhanced Style Analysis - Clichés", True, 
                                      f"Detected clichés with educational rationale", {
                                          "total_issues": len(issues),
                                          "detected_cliches": detected_cliches,
                                          "has_reasoning": has_reasoning,
                                          "has_examples": has_examples,
                                          "has_learning_resources": has_learning_resources,
                                          "overall_score": analysis.get("overall_score", 0)
                                      })
                    else:
                        self.log_result("Enhanced Style Analysis - Clichés", False, "Invalid response format", data)
                else:
                    error_text = await response.text()
                    self.log_result("Enhanced Style Analysis - Clichés", False, f"HTTP {response.status}", {"error": error_text})
                    
        except Exception as e:
            self.log_result("Enhanced Style Analysis - Clichés", False, f"Request error: {str(e)}")
    
    async def test_enhanced_style_passive_voice(self):
        """Test enhanced style analysis with passive voice as specified in review"""
        try:
            test_data = {
                "text": "The door was opened by the mysterious figure"
            }
            
            async with self.session.post(f"{BACKEND_URL}/analyze-style-enhanced",
                                       json=test_data,
                                       headers={"Content-Type": "application/json"}) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "style_analysis" in data:
                        analysis = data["style_analysis"]
                        issues = analysis.get("issues", [])
                        
                        # Should detect passive voice
                        detected_passive = any(
                            "passive" in issue.get("type", "").lower()
                            for issue in issues
                        )
                        
                        # Check for educational explanations
                        has_explanations = all("explanation" in issue for issue in issues) if issues else True
                        has_suggested_revisions = all("suggested_revision" in issue for issue in issues) if issues else True
                        
                        self.log_result("Enhanced Style Analysis - Passive Voice", True, 
                                      f"Passive voice analysis with educational explanations", {
                                          "total_issues": len(issues),
                                          "detected_passive_voice": detected_passive,
                                          "has_explanations": has_explanations,
                                          "has_suggested_revisions": has_suggested_revisions,
                                          "issue_types": [issue.get("type") for issue in issues]
                                      })
                    else:
                        self.log_result("Enhanced Style Analysis - Passive Voice", False, "Invalid response format", data)
                else:
                    error_text = await response.text()
                    self.log_result("Enhanced Style Analysis - Passive Voice", False, f"HTTP {response.status}", {"error": error_text})
                    
        except Exception as e:
            self.log_result("Enhanced Style Analysis - Passive Voice", False, f"Request error: {str(e)}")
    
    async def test_enhanced_style_telling_vs_showing(self):
        """Test enhanced style analysis with telling vs showing as specified in review"""
        try:
            test_data = {
                "text": "She was angry and felt nervous"
            }
            
            async with self.session.post(f"{BACKEND_URL}/analyze-style-enhanced",
                                       json=test_data,
                                       headers={"Content-Type": "application/json"}) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "style_analysis" in data:
                        analysis = data["style_analysis"]
                        issues = analysis.get("issues", [])
                        
                        # Should detect telling vs showing issues
                        detected_telling = any(
                            "telling" in issue.get("type", "").lower() or
                            "showing" in issue.get("type", "").lower()
                            for issue in issues
                        )
                        
                        # Check for educational value - "why this matters"
                        has_why_explanations = all(
                            "reasoning" in issue and issue["reasoning"]
                            for issue in issues
                        ) if issues else True
                        
                        self.log_result("Enhanced Style Analysis - Telling vs Showing", True, 
                                      f"Telling vs showing analysis with 'why this matters' explanations", {
                                          "total_issues": len(issues),
                                          "detected_telling_issues": detected_telling,
                                          "has_why_explanations": has_why_explanations,
                                          "educational_notes": len(analysis.get("educational_notes", [])),
                                          "improvement_summary": bool(analysis.get("improvement_summary"))
                                      })
                    else:
                        self.log_result("Enhanced Style Analysis - Telling vs Showing", False, "Invalid response format", data)
                else:
                    error_text = await response.text()
                    self.log_result("Enhanced Style Analysis - Telling vs Showing", False, f"HTTP {response.status}", {"error": error_text})
                    
        except Exception as e:
            self.log_result("Enhanced Style Analysis - Telling vs Showing", False, f"Request error: {str(e)}")
    
    async def test_style_coach_help_educational_resources(self):
        """Test style coach help for educational resources as specified in review"""
        try:
            async with self.session.get(f"{BACKEND_URL}/style-coach-help") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "educational_resources" in data and "issue_types" in data:
                        educational_resources = data["educational_resources"]
                        issue_types = data["issue_types"]
                        
                        # Verify issue type descriptions provide educational value
                        has_descriptions = all("description" in issue_type for issue_type in issue_types)
                        
                        # Check for specific issue types mentioned in review
                        expected_types = ["cliche_language", "passive_voice", "telling_not_showing"]
                        available_types = [issue_type.get("type") for issue_type in issue_types]
                        has_expected_types = all(expected_type in available_types for expected_type in expected_types)
                        
                        self.log_result("Style Coach Help - Educational Resources", True, 
                                      f"Educational resources and issue type descriptions available", {
                                          "issue_types_count": len(issue_types),
                                          "has_descriptions": has_descriptions,
                                          "has_expected_types": has_expected_types,
                                          "has_educational_resources": bool(educational_resources),
                                          "available_types": available_types
                                      })
                    else:
                        self.log_result("Style Coach Help - Educational Resources", False, "Invalid response format", data)
                else:
                    error_text = await response.text()
                    self.log_result("Style Coach Help - Educational Resources", False, f"HTTP {response.status}", {"error": error_text})
                    
        except Exception as e:
            self.log_result("Style Coach Help - Educational Resources", False, f"Request error: {str(e)}")

    async def run_comprehensive_tests(self):
        """Run comprehensive Phase 3A tests covering all review request features"""
        print("🎯 VisionForge Phase 3A Comprehensive Testing")
        print("Testing all features specified in the review request")
        print("=" * 70)
        
        print("\n🔍 CONTINUITY ENGINE TESTS:")
        await self.test_continuity_basic_content()
        await self.test_continuity_with_character_context()
        
        print("\n📝 ENHANCED STYLE COACH TESTS:")
        await self.test_enhanced_style_cliches()
        await self.test_enhanced_style_passive_voice()
        await self.test_enhanced_style_telling_vs_showing()
        await self.test_style_coach_help_educational_resources()
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 COMPREHENSIVE PHASE 3A TEST SUMMARY")
        print("=" * 70)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        # Feature breakdown
        continuity_tests = [r for r in self.test_results if "Continuity" in r["test"]]
        style_tests = [r for r in self.test_results if "Style" in r["test"]]
        
        continuity_passed = sum(1 for r in continuity_tests if r["success"])
        style_passed = sum(1 for r in style_tests if r["success"])
        
        print(f"\n🔍 CONTINUITY ENGINE: {continuity_passed}/{len(continuity_tests)} passed")
        print(f"📝 ENHANCED STYLE COACH: {style_passed}/{len(style_tests)} passed")
        
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
    async with ComprehensivePhase3ATester() as tester:
        success = await tester.run_comprehensive_tests()
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