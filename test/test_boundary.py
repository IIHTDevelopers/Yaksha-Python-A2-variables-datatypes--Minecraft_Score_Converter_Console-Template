import unittest
import os
import importlib
import sys
import io
import contextlib
import inspect
from test.TestUtils import TestUtils

def check_file_exists(filename):
    """Check if a file exists in the current directory."""
    return os.path.exists(filename)

def safely_import_module(module_name):
    """Safely import a module, returning None if import fails."""
    try:
        return importlib.import_module(module_name)
    except ImportError:
        return None

def check_function_exists(module, function_name):
    """Check if a function exists in a module."""
    return hasattr(module, function_name) and callable(getattr(module, function_name))

def safely_call_function(module, function_name, *args, **kwargs):
    """Safely call a function, returning None if it fails."""
    if not check_function_exists(module, function_name):
        return None
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            return getattr(module, function_name)(*args, **kwargs)
    except Exception:
        return None

def is_function_implemented(module, function_name):
    """Check if a function is actually implemented (not just a pass statement)."""
    if not check_function_exists(module, function_name):
        return False
    
    try:
        func = getattr(module, function_name)
        source = inspect.getsource(func)
        
        # Remove everything except the actual implementation
        lines = source.split('\n')
        implementation_lines = []
        in_docstring = False
        
        for line in lines:
            stripped = line.strip()
            
            # Skip empty lines
            if not stripped:
                continue
                
            # Skip function definition line
            if stripped.startswith('def '):
                continue
                
            # Handle docstrings (both single and multi-line)
            if stripped.startswith('"""') or stripped.startswith("'''"):
                if stripped.count('"""') == 2 or stripped.count("'''") == 2:
                    # Single line docstring, skip it
                    continue
                else:
                    # Start/end of multi-line docstring
                    in_docstring = not in_docstring
                    continue
            
            # Skip lines inside docstring
            if in_docstring:
                continue
                
            # Skip comments (including TODO comments)
            if stripped.startswith('#'):
                continue
                
            # What's left should be actual implementation
            implementation_lines.append(stripped)
        
        # Check if we only have 'pass' statements or no implementation at all
        if not implementation_lines:
            return False
            
        # If all remaining lines are just 'pass', 'return None', or similar, it's not implemented
        non_implementation_lines = [line for line in implementation_lines 
                                  if line not in ['pass', 'return None', 'return', '...', 'raise NotImplementedError()']]
        return len(non_implementation_lines) > 0
        
    except Exception:
        return True  # If we can't check, assume it's implemented

def load_module_dynamically():
    """Load the student's module for testing"""
    return safely_import_module("skeleton")

class TestMinecraftBoundary(unittest.TestCase):
    """Test class for comprehensive boundary value testing of the Minecraft Score Converter."""
    
    def setUp(self):
        """Setup test data before each test method."""
        self.test_obj = TestUtils()
        self.module_obj = load_module_dynamically()
    
    def test_comprehensive_boundary_scenarios(self):
        """Test all boundary scenarios across all conversion functions with complete coverage"""
        try:
            # Check if module exists
            if self.module_obj is None:
                self.test_obj.yakshaAssert("TestComprehensiveBoundaryScenarios", False, "boundary")
                print("TestComprehensiveBoundaryScenarios = Failed")
                return
            
            # Check all required functions
            required_functions = [
                "convert_string_to_int", "convert_float_to_int", 
                "convert_hex_to_int", "convert_score_to_string", "create_player_list"
            ]
            
            missing_functions = []
            for func_name in required_functions:
                if not check_function_exists(self.module_obj, func_name):
                    missing_functions.append(func_name)
            
            if missing_functions:
                self.test_obj.yakshaAssert("TestComprehensiveBoundaryScenarios", False, "boundary")
                print("TestComprehensiveBoundaryScenarios = Failed")
                return
            
            # Create a list to collect errors
            errors = []
            
            # Check if all functions are implemented
            unimplemented_functions = []
            for func_name in required_functions:
                if not is_function_implemented(self.module_obj, func_name):
                    unimplemented_functions.append(func_name)
            
            if unimplemented_functions:
                errors.append(f"Functions not implemented (contain only pass/return None): {', '.join(unimplemented_functions)}")
            
            # === STRING CONVERSION BOUNDARY TESTS ===
            if is_function_implemented(self.module_obj, "convert_string_to_int"):
                string_test_cases = [
                    ("0", 0, "zero string - minimum boundary"),
                    ("1", 1, "single digit - minimum positive"),
                    ("42", 42, "typical two-digit mining score"),
                    ("100", 100, "typical mining score from SRS"),
                    ("123", 123, "multiple digits"),
                    ("999", 999, "high three-digit score"),
                    ("9999", 9999, "four-digit boundary"),
                    ("999999", 999999, "large string - upper boundary test")
                ]
                
                for input_val, expected, description in string_test_cases:
                    result = safely_call_function(self.module_obj, "convert_string_to_int", input_val)
                    if result is None:
                        errors.append(f"convert_string_to_int returned None for {description}")
                    elif result != expected:
                        errors.append(f"convert_string_to_int('{input_val}') should be {expected} for {description}, got {result}")
            
            # === FLOAT CONVERSION BOUNDARY TESTS (with truncation) ===
            if is_function_implemented(self.module_obj, "convert_float_to_int"):
                float_test_cases = [
                    (0.0, 0, "zero float - minimum boundary"),
                    (0.1, 0, "small positive float - truncation test"),
                    (0.9, 0, "just below 1.0 - truncation boundary"),
                    (1.0, 1, "whole number float"),
                    (1.1, 1, "low combat score - truncation"),
                    (1.9, 1, "truncation test - should not round up"),
                    (50.5, 50, "medium combat score - exact half truncation"),
                    (98.7, 98, "typical combat score from SRS"),
                    (99.9, 99, "high combat score - near perfect"),
                    (100.0, 100, "perfect combat score"),
                    (999.99, 999, "large float with decimals"),
                    (999999.9, 999999, "very large float - upper boundary")
                ]
                
                for input_val, expected, description in float_test_cases:
                    result = safely_call_function(self.module_obj, "convert_float_to_int", input_val)
                    if result is None:
                        errors.append(f"convert_float_to_int returned None for {description}")
                    elif result != expected:
                        errors.append(f"convert_float_to_int({input_val}) should be {expected} for {description}, got {result}")
            
            # === HEX CONVERSION BOUNDARY TESTS ===
            if is_function_implemented(self.module_obj, "convert_hex_to_int"):
                hex_test_cases = [
                    ("0", 0, "zero hex - minimum boundary"),
                    ("1", 1, "single digit hex"),
                    ("9", 9, "highest single digit"),
                    ("A", 10, "single hex letter - lowercase boundary"),
                    ("F", 15, "max single hex digit"),
                    ("10", 16, "hex 10 = decimal 16"),
                    ("1F", 31, "typical achievement bonus from SRS"),
                    ("FF", 255, "max single byte hex - important boundary"),
                    ("100", 256, "hex 100 = decimal 256"),
                    ("ABC", 2748, "multi-character uppercase hex"),
                    ("abc", 2748, "multi-character lowercase hex"),
                    ("ff", 255, "lowercase version of FF"),
                    ("ABCD", 43981, "four-character hex"),
                    ("DEAD", 57005, "complex hex value"),
                    ("BEEF", 48879, "another complex hex value"),
                    ("1234", 4660, "numeric-looking hex"),
                    ("FFFF", 65535, "max 16-bit value")
                ]
                
                for input_val, expected, description in hex_test_cases:
                    result = safely_call_function(self.module_obj, "convert_hex_to_int", input_val)
                    if result is None:
                        errors.append(f"convert_hex_to_int returned None for {description}")
                    elif result != expected:
                        errors.append(f"convert_hex_to_int('{input_val}') should be {expected} for {description}, got {result}")
            
            # === SCORE DISPLAY CONVERSION BOUNDARY TESTS ===
            if is_function_implemented(self.module_obj, "convert_score_to_string"):
                score_test_cases = [
                    (0, "0", "zero score - minimum boundary"),
                    (1, "1", "minimum positive score"),
                    (42, "42", "small score"),
                    (100, "100", "round number score"),
                    (150, "150", "typical total score from SRS"),
                    (229, "229", "SRS example total (100+98+31)"),
                    (999, "999", "three-digit boundary"),
                    (1000, "1000", "four-digit threshold"),
                    (1234, "1234", "four digit score"),
                    (9999, "9999", "four-digit boundary"),
                    (10000, "10000", "five-digit threshold"),
                    (99999, "99999", "five-digit boundary"),
                    (999999, "999999", "very high score - upper boundary")
                ]
                
                for input_val, expected, description in score_test_cases:
                    result = safely_call_function(self.module_obj, "convert_score_to_string", input_val)
                    if result is None:
                        errors.append(f"convert_score_to_string returned None for {description}")
                    elif result != expected:
                        errors.append(f"convert_score_to_string({input_val}) should be '{expected}' for {description}, got '{result}'")
                    elif not isinstance(result, str):
                        errors.append(f"convert_score_to_string({input_val}) should return string, got {type(result)}")
            
            # === PLAYER LIST CREATION BOUNDARY TESTS ===
            if is_function_implemented(self.module_obj, "create_player_list"):
                player_test_cases = [
                    ("A", 0, ["A", 0], "single char name, zero score - minimum boundaries"),
                    ("x", 1, ["x", 1], "minimal name, minimal positive score"),
                    ("Steve", 100, ["Steve", 100], "typical player from SRS"),
                    ("Alex", 250, ["Alex", 250], "high score player from SRS"),
                    ("TestPlayer", 42, ["TestPlayer", 42], "normal test case"),
                    ("Player123", 999, ["Player123", 999], "alphanumeric name, high score"),
                    ("VeryLongPlayerName", 1337, ["VeryLongPlayerName", 1337], "long name boundary"),
                    ("Notch", 99999, ["Notch", 99999], "creator reference with very high score"),
                    ("Z", 999999, ["Z", 999999], "single char with maximum score boundary")
                ]
                
                for name, score, expected, description in player_test_cases:
                    result = safely_call_function(self.module_obj, "create_player_list", name, score)
                    if result is None:
                        errors.append(f"create_player_list returned None for {description}")
                    elif result != expected:
                        errors.append(f"create_player_list('{name}', {score}) should be {expected} for {description}, got {result}")
                    elif not isinstance(result, list):
                        errors.append(f"create_player_list('{name}', {score}) should return list for {description}, got {type(result)}")
                    elif len(result) != 2:
                        errors.append(f"create_player_list('{name}', {score}) should return list with 2 elements for {description}, got {len(result)} elements")
                    elif result[0] != name:
                        errors.append(f"create_player_list first element should be '{name}' for {description}, got '{result[0]}'")
                    elif result[1] != score:
                        errors.append(f"create_player_list second element should be {score} for {description}, got {result[1]}")
            
            # === COMPREHENSIVE INTEGRATION BOUNDARY TESTS ===
            if all(is_function_implemented(self.module_obj, func) for func in required_functions):
                integration_test_cases = [
                    {
                        # Minimum boundary scenario
                        "mining": "0", "combat": 0.0, "hex": "0", "name": "MinPlayer",
                        "expected_mining": 0, "expected_combat": 0, "expected_hex": 0,
                        "expected_total": 0, "expected_display": "0",
                        "expected_stats": ["MinPlayer", 0], 
                        "description": "absolute minimum values across all conversions"
                    },
                    {
                        # SRS example scenario
                        "mining": "100", "combat": 98.7, "hex": "1F", "name": "Steve",
                        "expected_mining": 100, "expected_combat": 98, "expected_hex": 31,
                        "expected_total": 229, "expected_display": "229",
                        "expected_stats": ["Steve", 229], 
                        "description": "SRS example scenario - typical game values"
                    },
                    {
                        # High boundary scenario
                        "mining": "999", "combat": 99.9, "hex": "FF", "name": "ProGamer",
                        "expected_mining": 999, "expected_combat": 99, "expected_hex": 255,
                        "expected_total": 1353, "expected_display": "1353",
                        "expected_stats": ["ProGamer", 1353], 
                        "description": "high values boundary test"
                    },
                    {
                        # Truncation boundary test
                        "mining": "1", "combat": 1.9, "hex": "1", "name": "TruncTest",
                        "expected_mining": 1, "expected_combat": 1, "expected_hex": 1,
                        "expected_total": 3, "expected_display": "3",
                        "expected_stats": ["TruncTest", 3], 
                        "description": "truncation boundary - 1.9 should become 1, not 2"
                    },
                    {
                        # Large hex boundary test
                        "mining": "500", "combat": 50.5, "hex": "DEAD", "name": "HexMaster",
                        "expected_mining": 500, "expected_combat": 50, "expected_hex": 57005,
                        "expected_total": 57555, "expected_display": "57555",
                        "expected_stats": ["HexMaster", 57555], 
                        "description": "large hex value integration test"
                    },
                    {
                        # Edge case: all ones
                        "mining": "1", "combat": 1.0, "hex": "1", "name": "X",
                        "expected_mining": 1, "expected_combat": 1, "expected_hex": 1,
                        "expected_total": 3, "expected_display": "3",
                        "expected_stats": ["X", 3], 
                        "description": "all ones boundary test"
                    },
                    {
                        # Large mining score boundary
                        "mining": "9999", "combat": 0.1, "hex": "A", "name": "Miner",
                        "expected_mining": 9999, "expected_combat": 0, "expected_hex": 10,
                        "expected_total": 10009, "expected_display": "10009",
                        "expected_stats": ["Miner", 10009], 
                        "description": "large mining score with small other values"
                    }
                ]
                
                for test_case in integration_test_cases:
                    # Test individual conversions
                    mining_result = safely_call_function(self.module_obj, "convert_string_to_int", test_case["mining"])
                    if mining_result != test_case["expected_mining"]:
                        errors.append(f"Mining conversion failed for {test_case['description']}: expected {test_case['expected_mining']}, got {mining_result}")
                    
                    combat_result = safely_call_function(self.module_obj, "convert_float_to_int", test_case["combat"])
                    if combat_result != test_case["expected_combat"]:
                        errors.append(f"Combat conversion failed for {test_case['description']}: expected {test_case['expected_combat']}, got {combat_result}")
                    
                    hex_result = safely_call_function(self.module_obj, "convert_hex_to_int", test_case["hex"])
                    if hex_result != test_case["expected_hex"]:
                        errors.append(f"Hex conversion failed for {test_case['description']}: expected {test_case['expected_hex']}, got {hex_result}")
                    
                    # Test total calculation and subsequent conversions
                    if mining_result is not None and combat_result is not None and hex_result is not None:
                        total_score = mining_result + combat_result + hex_result
                        if total_score != test_case["expected_total"]:
                            errors.append(f"Total score calculation failed for {test_case['description']}: expected {test_case['expected_total']}, got {total_score}")
                        
                        # Test score display conversion
                        display_result = safely_call_function(self.module_obj, "convert_score_to_string", total_score)
                        if display_result != test_case["expected_display"]:
                            errors.append(f"Score display conversion failed for {test_case['description']}: expected '{test_case['expected_display']}', got '{display_result}'")
                        
                        # Test player stats creation
                        stats_result = safely_call_function(self.module_obj, "create_player_list", test_case["name"], total_score)
                        if stats_result != test_case["expected_stats"]:
                            errors.append(f"Player stats creation failed for {test_case['description']}: expected {test_case['expected_stats']}, got {stats_result}")
            
            # === SPECIFIC BOUNDARY EDGE CASES ===
            
            # Test float truncation edge cases (not rounding)
            if is_function_implemented(self.module_obj, "convert_float_to_int"):
                truncation_edge_cases = [
                    (0.999, 0, "0.999 should truncate to 0, not round to 1"),
                    (1.999, 1, "1.999 should truncate to 1, not round to 2"),
                    (99.999, 99, "99.999 should truncate to 99, not round to 100"),
                    (0.5, 0, "0.5 should truncate to 0, not round to 1"),
                    (1.5, 1, "1.5 should truncate to 1, not round to 2"),
                    (2.7, 2, "2.7 should truncate to 2, not round to 3")
                ]
                
                for input_val, expected, description in truncation_edge_cases:
                    result = safely_call_function(self.module_obj, "convert_float_to_int", input_val)
                    if result != expected:
                        errors.append(f"Truncation edge case failed: {description}, got {result}")
            
            # Test hex case sensitivity boundary
            if is_function_implemented(self.module_obj, "convert_hex_to_int"):
                case_sensitivity_tests = [
                    ("a", 10, "lowercase a should equal 10"),
                    ("A", 10, "uppercase A should equal 10"),
                    ("f", 15, "lowercase f should equal 15"),
                    ("F", 15, "uppercase F should equal 15"),
                    ("aB", 171, "mixed case aB should work"),
                    ("Ab", 171, "mixed case Ab should work"),
                    ("fF", 255, "mixed case fF should work"),
                    ("Ff", 255, "mixed case Ff should work")
                ]
                
                for input_val, expected, description in case_sensitivity_tests:
                    result = safely_call_function(self.module_obj, "convert_hex_to_int", input_val)
                    if result != expected:
                        errors.append(f"Hex case sensitivity test failed: {description}, got {result}")
            
            # === TYPE VERIFICATION BOUNDARY TESTS ===
            
            # Verify return types are correct at boundaries
            type_verification_tests = [
                ("convert_string_to_int", ["0"], int, "zero string should return int"),
                ("convert_string_to_int", ["999999"], int, "large string should return int"),
                ("convert_float_to_int", [0.0], int, "zero float should return int"),
                ("convert_float_to_int", [999999.9], int, "large float should return int"),
                ("convert_hex_to_int", ["0"], int, "zero hex should return int"),
                ("convert_hex_to_int", ["FFFF"], int, "large hex should return int"),
                ("convert_score_to_string", [0], str, "zero score should return str"),
                ("convert_score_to_string", [999999], str, "large score should return str"),
                ("create_player_list", ["A", 0], list, "minimal inputs should return list"),
                ("create_player_list", ["VeryLongName", 999999], list, "large inputs should return list")
            ]
            
            for func_name, args, expected_type, description in type_verification_tests:
                if is_function_implemented(self.module_obj, func_name):
                    result = safely_call_function(self.module_obj, func_name, *args)
                    if result is not None and not isinstance(result, expected_type):
                        errors.append(f"Type verification failed: {description} - expected {expected_type.__name__}, got {type(result).__name__}")
            
            # Final assertion
            if errors:
                self.test_obj.yakshaAssert("TestComprehensiveBoundaryScenarios", False, "boundary")
                print("TestComprehensiveBoundaryScenarios = Failed")
            else:
                self.test_obj.yakshaAssert("TestComprehensiveBoundaryScenarios", True, "boundary")
                print("TestComprehensiveBoundaryScenarios = Passed")
                
        except Exception as e:
            self.test_obj.yakshaAssert("TestComprehensiveBoundaryScenarios", False, "boundary")
            print("TestComprehensiveBoundaryScenarios = Failed")

if __name__ == '__main__':
    unittest.main()