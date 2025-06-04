import unittest
import os
import importlib
import sys
import io
import contextlib
import inspect
import re
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
    module_obj = safely_import_module("skeleton")
    if module_obj is None:
        module_obj = safely_import_module("skeleton")
    return module_obj

class TestMinecraftFunctional(unittest.TestCase):
    """Test class for functional testing of the Minecraft Score Converter."""
    
    def setUp(self):
        """Setup test data before each test method."""
        self.test_obj = TestUtils()
        self.module_obj = load_module_dynamically()
    
    def test_required_variables(self):
        """Test if all required variables are defined with exact naming per SRS Section 3.1"""
        try:
            # Check if main file exists
            main_file = None
            for filename in ['skeleton.py']:
                if check_file_exists(filename):
                    main_file = filename
                    break
            
            if main_file is None:
                self.test_obj.yakshaAssert("TestRequiredVariables", False, "functional")
                print("TestRequiredVariables = Failed")
                return
            
            # Create a list to collect errors
            errors = []
            
            with open(main_file, 'r') as file:
                content = file.read()
            
            # SRS Section 3.1: Required Variable Names with exact specifications
            required_vars = {
                'mining_score': r'mining_score\s*=.*input',  # Must be string input from user
                'mining_points': r'mining_points\s*=',       # Converted integer from mining_score
                'combat_score': r'combat_score\s*=',         # Must be float from user input
                'combat_points': r'combat_points\s*=',       # Converted integer from combat_score
                'achievement_hex': r'achievement_hex\s*=.*input',  # Must be string input (hex)
                'achievement_bonus': r'achievement_bonus\s*=',     # Converted integer from hex
                'total_score': r'total_score\s*=',           # Sum of all converted scores
                'score_display': r'score_display\s*=',       # Total score as string for display
                'player_stats': r'player_stats\s*='          # List with [player_name, total_score]
            }
            
            # Check if main execution block exists (SRS Section 4: Template Code Structure)
            if 'if __name__ == "__main__"' not in content:
                errors.append("Missing main execution block (if __name__ == '__main__') - Required by SRS Section 4")
            
            # Only check for variables if main block exists and is implemented
            main_block_content = ""
            if 'if __name__ == "__main__"' in content:
                main_block_start = content.find('if __name__ == "__main__"')
                main_block_content = content[main_block_start:]
                
                # Check if main block has actual implementation
                main_lines = [line.strip() for line in main_block_content.split('\n') 
                             if line.strip() and not line.strip().startswith('#') 
                             and line.strip() not in ['if __name__ == "__main__":', 'pass', '...']]
                
                if len(main_lines) <= 1:  # Only has the if statement
                    errors.append("Main execution block is not implemented (contains only pass or comments) - Required by SRS Section 5.3")
                else:
                    # Check for required variables only if main block is implemented
                    for var_name, pattern in required_vars.items():
                        if not re.search(pattern, main_block_content, re.IGNORECASE):
                            errors.append(f"Required variable '{var_name}' not found in main block or incorrectly named - SRS Section 3.1 requirement")
                    
                    # Additional SRS Section 3.1 validations
                    # Check for player_name variable (Section 3.1.4)
                    if not re.search(r'player_name\s*=.*input', main_block_content, re.IGNORECASE):
                        errors.append("Required variable 'player_name' not found - must get name as string input (SRS Section 3.1.4)")
                    
                    # Check that mining_score is treated as string (SRS Section 3.1.1)
                    mining_pattern = r'mining_score\s*=\s*input\s*\('
                    if not re.search(mining_pattern, main_block_content):
                        errors.append("mining_score must be stored as string from input() - SRS Section 3.1.1")
                    
                    # Check that combat_score involves float conversion (SRS Section 3.1.2)
                    combat_pattern = r'float\s*\('
                    if not re.search(combat_pattern, main_block_content):
                        errors.append("combat_score must be converted to float - SRS Section 3.1.2")
                    
                    # Check that achievement_hex is string input (SRS Section 3.1.3)
                    hex_pattern = r'achievement_hex\s*=\s*input\s*\('
                    if not re.search(hex_pattern, main_block_content):
                        errors.append("achievement_hex must be stored as string from input() - SRS Section 3.1.3")
            
            # Final assertion
            if errors:
                self.test_obj.yakshaAssert("TestRequiredVariables", False, "functional")
                print("TestRequiredVariables = Failed")
            else:
                self.test_obj.yakshaAssert("TestRequiredVariables", True, "functional")
                print("TestRequiredVariables = Passed")
                
        except Exception as e:
            self.test_obj.yakshaAssert("TestRequiredVariables", False, "functional")
            print("TestRequiredVariables = Failed")

    def test_conversion_implementations(self):
        """Test all conversion functions per SRS Section 5.1 and 5.2 specifications"""
        try:
            # Check if module exists
            if self.module_obj is None:
                self.test_obj.yakshaAssert("TestConversionImplementations", False, "functional")
                print("TestConversionImplementations = Failed")
                return
            
            # SRS Section 5.1: Required conversion functions
            required_functions = ["convert_string_to_int", "convert_float_to_int", "convert_hex_to_int"]
            
            missing_functions = []
            for func_name in required_functions:
                if not check_function_exists(self.module_obj, func_name):
                    missing_functions.append(func_name)
            
            if missing_functions:
                self.test_obj.yakshaAssert("TestConversionImplementations", False, "functional")
                print("TestConversionImplementations = Failed")
                return
            
            # Create a list to collect errors
            errors = []
            
            # Check if functions are implemented
            unimplemented_functions = []
            for func_name in required_functions:
                if not is_function_implemented(self.module_obj, func_name):
                    unimplemented_functions.append(func_name)
            
            if unimplemented_functions:
                errors.append(f"Functions not implemented (contain only pass/return None): {', '.join(unimplemented_functions)}")
            
            # SRS Section 5.1.1: Test string conversion (Mining Points Conversion)
            if is_function_implemented(self.module_obj, "convert_string_to_int"):
                string_test_cases = [
                    ("100", 100, "SRS example: mining score '100' should return 100"),
                    ("0", 0, "SRS requirement: zero string should return 0"),
                    ("42", 42, "typical mining score conversion"),
                    ("999", 999, "high mining score"),
                    ("1", 1, "minimum positive mining score"),
                    ("123", 123, "multi-digit mining score")
                ]
                
                for input_val, expected, description in string_test_cases:
                    result = safely_call_function(self.module_obj, "convert_string_to_int", input_val)
                    if result is None:
                        errors.append(f"convert_string_to_int returned None for {description}")
                    elif result != expected:
                        errors.append(f"convert_string_to_int('{input_val}') should return {expected} per SRS, got {result}")
                    elif not isinstance(result, int):
                        errors.append(f"convert_string_to_int must return integer per SRS Section 3.2.1, got {type(result)}")
            
            # SRS Section 5.1.2: Test float conversion (Combat Score Conversion)
            if is_function_implemented(self.module_obj, "convert_float_to_int"):
                float_test_cases = [
                    (98.7, 98, "SRS example: combat score 98.7 should return 98 (truncated)"),
                    (0.0, 0, "SRS requirement: zero float should return 0"),
                    (99.9, 99, "high combat accuracy - decimal part truncated"),
                    (1.1, 1, "low combat score - decimal truncated"),
                    (50.5, 50, "medium combat score - SRS requires truncation"),
                    (100.0, 100, "perfect combat score"),
                    (1.0, 1, "SRS example: 1.0 should return 1")
                ]
                
                for input_val, expected, description in float_test_cases:
                    result = safely_call_function(self.module_obj, "convert_float_to_int", input_val)
                    if result is None:
                        errors.append(f"convert_float_to_int returned None for {description}")
                    elif result != expected:
                        errors.append(f"convert_float_to_int({input_val}) should return {expected} per SRS truncation rule, got {result}")
                    elif not isinstance(result, int):
                        errors.append(f"convert_float_to_int must return integer per SRS Section 3.2.2, got {type(result)}")
            
            # SRS Section 5.1.3: Test hex conversion (Achievement Bonus Conversion)
            if is_function_implemented(self.module_obj, "convert_hex_to_int"):
                hex_test_cases = [
                    ("1F", 31, "SRS example: achievement hex '1F' should return 31"),
                    ("A", 10, "SRS example: hex 'A' should return 10"),
                    ("ff", 255, "SRS example: lowercase 'ff' should return 255"),
                    ("0", 0, "SRS requirement: zero hex should return 0"),
                    ("F", 15, "single hex digit F"),
                    ("10", 16, "hex 10 equals decimal 16"),
                    ("ABC", 2748, "multi-character hex"),
                    ("DEAD", 57005, "complex hex value")
                ]
                
                for input_val, expected, description in hex_test_cases:
                    result = safely_call_function(self.module_obj, "convert_hex_to_int", input_val)
                    if result is None:
                        errors.append(f"convert_hex_to_int returned None for {description}")
                    elif result != expected:
                        errors.append(f"convert_hex_to_int('{input_val}') should return {expected} per SRS hex conversion, got {result}")
                    elif not isinstance(result, int):
                        errors.append(f"convert_hex_to_int must return integer per SRS Section 3.2.3, got {type(result)}")
            
            # SRS Section 5.2: Test additional formatting functions if they exist
            if check_function_exists(self.module_obj, "convert_score_to_string"):
                if is_function_implemented(self.module_obj, "convert_score_to_string"):
                    # SRS Section 5.2.1: Score to string conversion
                    score_test_cases = [
                        (150, "150", "SRS example: score 150 should return '150'"),
                        (0, "0", "SRS example: score 0 should return '0'"),
                        (42, "42", "typical score conversion"),
                        (999, "999", "high score conversion")
                    ]
                    
                    for input_val, expected, description in score_test_cases:
                        result = safely_call_function(self.module_obj, "convert_score_to_string", input_val)
                        if result is None:
                            errors.append(f"convert_score_to_string returned None for {description}")
                        elif result != expected:
                            errors.append(f"convert_score_to_string({input_val}) should return '{expected}' per SRS, got '{result}'")
                        elif not isinstance(result, str):
                            errors.append(f"convert_score_to_string must return string per SRS Section 5.2.1, got {type(result)}")
            
            if check_function_exists(self.module_obj, "create_player_list"):
                if is_function_implemented(self.module_obj, "create_player_list"):
                    # SRS Section 5.2.2: Player list creation
                    player_test_cases = [
                        ("Steve", 100, ["Steve", 100], "SRS example: create_player_list('Steve', 100) should return ['Steve', 100]"),
                        ("Alex", 250, ["Alex", 250], "SRS example: create_player_list('Alex', 250) should return ['Alex', 250]"),
                        ("Player1", 42, ["Player1", 42], "typical player list creation"),
                        ("Notch", 1337, ["Notch", 1337], "creator reference test")
                    ]
                    
                    for name, score, expected, description in player_test_cases:
                        result = safely_call_function(self.module_obj, "create_player_list", name, score)
                        if result is None:
                            errors.append(f"create_player_list returned None for {description}")
                        elif result != expected:
                            errors.append(f"create_player_list('{name}', {score}) should return {expected} per SRS, got {result}")
                        elif not isinstance(result, list):
                            errors.append(f"create_player_list must return list per SRS Section 5.2.2, got {type(result)}")
                        elif len(result) != 2:
                            errors.append(f"create_player_list must return list with exactly 2 elements per SRS, got {len(result)} elements")
            
            # Final assertion
            if errors:
                self.test_obj.yakshaAssert("TestConversionImplementations", False, "functional")
                print("TestConversionImplementations = Failed")
            else:
                self.test_obj.yakshaAssert("TestConversionImplementations", True, "functional")
                print("TestConversionImplementations = Passed")
                
        except Exception as e:
            self.test_obj.yakshaAssert("TestConversionImplementations", False, "functional")
            print("TestConversionImplementations = Failed")

    def test_function_existence(self):
        """Test that all required functions exist per SRS Section 4: Template Code Structure"""
        try:
            # Check if module exists
            if self.module_obj is None:
                self.test_obj.yakshaAssert("TestFunctionExistence", False, "functional")
                print("TestFunctionExistence = Failed")
                return
            
            # Collect errors
            errors = []
            
            # SRS Section 4.1: Required Type Conversion Functions
            required_functions = [
                "convert_string_to_int",    # SRS Section 5.1.1
                "convert_float_to_int",     # SRS Section 5.1.2
                "convert_hex_to_int",       # SRS Section 5.1.3
                "convert_score_to_string",  # SRS Section 5.2.1
                "create_player_list"        # SRS Section 5.2.2
            ]
            
            for func_name in required_functions:
                if not check_function_exists(self.module_obj, func_name):
                    errors.append(f"Required function {func_name} is missing - mandated by SRS Section 4.1")
                else:
                    # Check if function has proper docstring (SRS coding standards)
                    func_obj = getattr(self.module_obj, func_name)
                    if func_obj.__doc__ is None or len(func_obj.__doc__.strip()) < 10:
                        errors.append(f"Function {func_name} should have a meaningful docstring per SRS documentation requirements")
            
            # Check function signatures match SRS specifications
            signature_tests = [
                ("convert_string_to_int", 1, "must accept exactly 1 parameter (mining_score)"),
                ("convert_float_to_int", 1, "must accept exactly 1 parameter (combat_score)"),
                ("convert_hex_to_int", 1, "must accept exactly 1 parameter (achievement_hex)"),
                ("convert_score_to_string", 1, "must accept exactly 1 parameter (total_score)"),
                ("create_player_list", 2, "must accept exactly 2 parameters (player_name, total_score)")
            ]
            
            for func_name, expected_params, description in signature_tests:
                if check_function_exists(self.module_obj, func_name):
                    func_obj = getattr(self.module_obj, func_name)
                    try:
                        sig = inspect.signature(func_obj)
                        actual_params = len(sig.parameters)
                        if actual_params != expected_params:
                            errors.append(f"Function {func_name} {description}, got {actual_params} parameters")
                    except Exception as e:
                        errors.append(f"Could not inspect signature of {func_name}: {str(e)}")
            
            # Report results
            if errors:
                self.test_obj.yakshaAssert("TestFunctionExistence", False, "functional")
                print("TestFunctionExistence = Failed")
            else:
                self.test_obj.yakshaAssert("TestFunctionExistence", True, "functional")
                print("TestFunctionExistence = Passed")
                
        except Exception as e:
            self.test_obj.yakshaAssert("TestFunctionExistence", False, "functional")
            print("TestFunctionExistence = Failed")

    def test_implementation_quality(self):
        """Test implementation quality per SRS Section 3.2: Conversion Constraints"""
        try:
            # Check if module exists
            if self.module_obj is None:
                self.test_obj.yakshaAssert("TestImplementationQuality", False, "functional")
                print("TestImplementationQuality = Failed")
                return
            
            # Collect errors
            errors = []
            
            # Check required functions exist and are implemented
            required_functions = [
                "convert_string_to_int",
                "convert_float_to_int",
                "convert_hex_to_int"
            ]
            
            for func_name in required_functions:
                if not check_function_exists(self.module_obj, func_name):
                    errors.append(f"Required function {func_name} is missing - SRS requirement")
                elif not is_function_implemented(self.module_obj, func_name):
                    errors.append(f"Required function {func_name} is not implemented (contains only pass/return None) - SRS requirement")
            
            if errors:
                self.test_obj.yakshaAssert("TestImplementationQuality", False, "functional")
                print("TestImplementationQuality = Failed")
                return
            
            # SRS Section 3.2.1: Test string to integer conversion using int()
            if is_function_implemented(self.module_obj, "convert_string_to_int"):
                test_cases = [
                    ("42", 42, "SRS requirement: convert string to integer using int()"),
                    ("0", 0, "SRS edge case: zero conversion"),
                    ("999", 999, "SRS requirement: handle large numbers")
                ]
                
                for input_val, expected, description in test_cases:
                    result = safely_call_function(self.module_obj, "convert_string_to_int", input_val)
                    if result is None:
                        errors.append(f"convert_string_to_int returned None for {description}")
                    elif result != expected:
                        errors.append(f"convert_string_to_int({input_val}) failed {description}: expected {expected}, got {result}")
                    elif not isinstance(result, int):
                        errors.append(f"convert_string_to_int must return int per SRS Section 3.2.1, got {type(result)}")
            
            # SRS Section 3.2.2: Test float to integer conversion with truncation
            if is_function_implemented(self.module_obj, "convert_float_to_int"):
                test_cases = [
                    (3.14, 3, "SRS requirement: float to int conversion with truncation using int()"),
                    (98.7, 98, "SRS example: 98.7 should truncate to 98"),
                    (0.0, 0, "SRS edge case: zero float conversion"),
                    (99.99, 99, "SRS requirement: decimal part must be truncated")
                ]
                
                for input_val, expected, description in test_cases:
                    result = safely_call_function(self.module_obj, "convert_float_to_int", input_val)
                    if result is None:
                        errors.append(f"convert_float_to_int returned None for {description}")
                    elif result != expected:
                        errors.append(f"convert_float_to_int({input_val}) failed {description}: expected {expected}, got {result}")
                    elif not isinstance(result, int):
                        errors.append(f"convert_float_to_int must return int per SRS Section 3.2.2, got {type(result)}")
            
            # SRS Section 3.2.3: Test hex to integer conversion using int(x, 16)
            if is_function_implemented(self.module_obj, "convert_hex_to_int"):
                test_cases = [
                    ("A", 10, "SRS requirement: hex to int conversion using int(x, 16)"),
                    ("1F", 31, "SRS example: '1F' should convert to 31"),
                    ("0", 0, "SRS edge case: zero hex conversion"),
                    ("FF", 255, "SRS requirement: handle uppercase and lowercase")
                ]
                
                for input_val, expected, description in test_cases:
                    result = safely_call_function(self.module_obj, "convert_hex_to_int", input_val)
                    if result is None:
                        errors.append(f"convert_hex_to_int returned None for {description}")
                    elif result != expected:
                        errors.append(f"convert_hex_to_int('{input_val}') failed {description}: expected {expected}, got {result}")
                    elif not isinstance(result, int):
                        errors.append(f"convert_hex_to_int must return int per SRS Section 3.2.3, got {type(result)}")
            
            # Report results
            if errors:
                self.test_obj.yakshaAssert("TestImplementationQuality", False, "functional")
                print("TestImplementationQuality = Failed")
            else:
                self.test_obj.yakshaAssert("TestImplementationQuality", True, "functional")
                print("TestImplementationQuality = Passed")
                
        except Exception as e:
            self.test_obj.yakshaAssert("TestImplementationQuality", False, "functional")
            print("TestImplementationQuality = Failed")

    def test_score_calculation_workflow(self):
        """Test complete score calculation workflow per SRS Section 3.2.4 and Section 6"""
        try:
            # Check if module exists
            if self.module_obj is None:
                self.test_obj.yakshaAssert("TestScoreCalculationWorkflow", False, "functional")
                print("TestScoreCalculationWorkflow = Failed")
                return
            
            # Check all required functions per SRS Section 4
            required_functions = [
                "convert_string_to_int", "convert_float_to_int", 
                "convert_hex_to_int", "convert_score_to_string", "create_player_list"
            ]
            
            missing_functions = []
            for func_name in required_functions:
                if not check_function_exists(self.module_obj, func_name):
                    missing_functions.append(func_name)
            
            if missing_functions:
                self.test_obj.yakshaAssert("TestScoreCalculationWorkflow", False, "functional")
                print("TestScoreCalculationWorkflow = Failed")
                return
            
            # Create a list to collect errors
            errors = []
            
            # Check if all functions are implemented
            unimplemented_functions = []
            for func_name in required_functions:
                if not is_function_implemented(self.module_obj, func_name):
                    unimplemented_functions.append(func_name)
            
            if unimplemented_functions:
                errors.append(f"Functions not implemented: {', '.join(unimplemented_functions)}")
            
            # SRS Section 6: Complete workflow test scenarios
            if all(is_function_implemented(self.module_obj, func) for func in required_functions):
                workflow_test_cases = [
                    {
                        # SRS Example Scenario from Section 6
                        "mining": "100", "combat": 98.7, "hex": "1F", "name": "Steve",
                        "expected_mining": 100, "expected_combat": 98, "expected_hex": 31,
                        "expected_total": 229, "expected_display": "229", 
                        "expected_stats": ["Steve", 229], 
                        "description": "SRS Section 6 example: Steve with mining=100, combat=98.7, hex=1F"
                    },
                    {
                        # Minimum values scenario (SRS boundary testing)
                        "mining": "0", "combat": 0.0, "hex": "0", "name": "Beginner",
                        "expected_mining": 0, "expected_combat": 0, "expected_hex": 0,
                        "expected_total": 0, "expected_display": "0",
                        "expected_stats": ["Beginner", 0], 
                        "description": "SRS boundary test: minimum values across all score types"
                    },
                    {
                        # High values scenario
                        "mining": "500", "combat": 85.3, "hex": "FF", "name": "Expert",
                        "expected_mining": 500, "expected_combat": 85, "expected_hex": 255,
                        "expected_total": 840, "expected_display": "840",
                        "expected_stats": ["Expert", 840], 
                        "description": "SRS high values test: Expert player with max achievement bonus"
                    },
                    {
                        # Decimal truncation test (SRS Section 3.2.2)
                        "mining": "1", "combat": 1.9, "hex": "1", "name": "Rookie",
                        "expected_mining": 1, "expected_combat": 1, "expected_hex": 1,
                        "expected_total": 3, "expected_display": "3",
                        "expected_stats": ["Rookie", 3], 
                        "description": "SRS truncation test: 1.9 combat score should truncate to 1"
                    }
                ]
                
                for test_case in workflow_test_cases:
                    # SRS Section 3.2.1: Test mining points conversion
                    mining_result = safely_call_function(self.module_obj, "convert_string_to_int", test_case["mining"])
                    if mining_result != test_case["expected_mining"]:
                        errors.append(f"Mining conversion failed for {test_case['description']}: expected {test_case['expected_mining']}, got {mining_result}")
                    
                    # SRS Section 3.2.2: Test combat points conversion (with truncation)
                    combat_result = safely_call_function(self.module_obj, "convert_float_to_int", test_case["combat"])
                    if combat_result != test_case["expected_combat"]:
                        errors.append(f"Combat conversion failed for {test_case['description']}: expected {test_case['expected_combat']}, got {combat_result}")
                    
                    # SRS Section 3.2.3: Test achievement bonus conversion
                    hex_result = safely_call_function(self.module_obj, "convert_hex_to_int", test_case["hex"])
                    if hex_result != test_case["expected_hex"]:
                        errors.append(f"Hex conversion failed for {test_case['description']}: expected {test_case['expected_hex']}, got {hex_result}")
                    
                    # SRS Section 3.2.4: Test total score calculation
                    if mining_result is not None and combat_result is not None and hex_result is not None:
                        total_score = mining_result + combat_result + hex_result
                        if total_score != test_case["expected_total"]:
                            errors.append(f"Total score calculation failed for {test_case['description']}: expected {test_case['expected_total']}, got {total_score}")
                        
                        # SRS Section 5.2.1: Test score display conversion
                        display_result = safely_call_function(self.module_obj, "convert_score_to_string", total_score)
                        if display_result != test_case["expected_display"]:
                            errors.append(f"Score display conversion failed for {test_case['description']}: expected '{test_case['expected_display']}', got '{display_result}'")
                        
                        # SRS Section 3.1.5 & 5.2.2: Test player stats creation
                        stats_result = safely_call_function(self.module_obj, "create_player_list", test_case["name"], total_score)
                        if stats_result != test_case["expected_stats"]:
                            errors.append(f"Player stats creation failed for {test_case['description']}: expected {test_case['expected_stats']}, got {stats_result}")
            
            # Final assertion
            if errors:
                self.test_obj.yakshaAssert("TestScoreCalculationWorkflow", False, "functional")
                print("TestScoreCalculationWorkflow = Failed")
            else:
                self.test_obj.yakshaAssert("TestScoreCalculationWorkflow", True, "functional")
                print("TestScoreCalculationWorkflow = Passed")
                
        except Exception as e:
            self.test_obj.yakshaAssert("TestScoreCalculationWorkflow", False, "functional")
            print("TestScoreCalculationWorkflow = Failed")

    def test_data_type_handling(self):
        """Test proper data type handling per SRS Section 3: Constraints"""
        try:
            # Check if module exists
            if self.module_obj is None:
                self.test_obj.yakshaAssert("TestDataTypeHandling", False, "functional")
                print("TestDataTypeHandling = Failed")
                return
            
            # Check required functions
            required_functions = [
                "convert_string_to_int", "convert_float_to_int", 
                "convert_hex_to_int", "convert_score_to_string", "create_player_list"
            ]
            
            missing_functions = []
            for func_name in required_functions:
                if not check_function_exists(self.module_obj, func_name):
                    missing_functions.append(func_name)
            
            if missing_functions:
                self.test_obj.yakshaAssert("TestDataTypeHandling", False, "functional")
                print("TestDataTypeHandling = Failed")
                return
            
            # Create a list to collect errors
            errors = []
            
            # Check if functions are implemented
            unimplemented_functions = []
            for func_name in required_functions:
                if not is_function_implemented(self.module_obj, func_name):
                    unimplemented_functions.append(func_name)
            
            if unimplemented_functions:
                errors.append(f"Functions not implemented: {', '.join(unimplemented_functions)}")
            
            # SRS Section 3.1: Test return types match specifications
            if all(is_function_implemented(self.module_obj, func) for func in required_functions):
                
                # SRS Section 3.1.1: Mining score must return integer
                string_result = safely_call_function(self.module_obj, "convert_string_to_int", "123")
                if string_result is not None and not isinstance(string_result, int):
                    errors.append(f"convert_string_to_int must return int per SRS Section 3.1.1, got {type(string_result)}")
                
                # SRS Section 3.1.2: Combat score must return integer (truncated)
                float_result = safely_call_function(self.module_obj, "convert_float_to_int", 45.6)
                if float_result is not None and not isinstance(float_result, int):
                    errors.append(f"convert_float_to_int must return int per SRS Section 3.1.2, got {type(float_result)}")
                
                # SRS Section 3.1.3: Achievement hex must return integer
                hex_result = safely_call_function(self.module_obj, "convert_hex_to_int", "A5")
                if hex_result is not None and not isinstance(hex_result, int):
                    errors.append(f"convert_hex_to_int must return int per SRS Section 3.1.3, got {type(hex_result)}")
                
                # SRS Section 3.3.1: Score display must be string
                score_str_result = safely_call_function(self.module_obj, "convert_score_to_string", 200)
                if score_str_result is not None and not isinstance(score_str_result, str):
                    errors.append(f"convert_score_to_string must return str per SRS Section 3.3.1, got {type(score_str_result)}")
                
                # SRS Section 3.1.5: Player stats must be list with exactly 2 elements
                player_result = safely_call_function(self.module_obj, "create_player_list", "Alex", 150)
                if player_result is not None:
                    if not isinstance(player_result, list):
                        errors.append(f"create_player_list must return list per SRS Section 3.1.5, got {type(player_result)}")
                    elif len(player_result) != 2:
                        errors.append(f"create_player_list must return list with exactly 2 elements per SRS Section 3.1.5, got {len(player_result)}")
                    elif not isinstance(player_result[0], str):
                        errors.append(f"First element of player list must be string (player_name) per SRS Section 3.1.4, got {type(player_result[0])}")
                    elif not isinstance(player_result[1], int):
                        errors.append(f"Second element of player list must be int (total_score) per SRS Section 3.1.5, got {type(player_result[1])}")
                
                # SRS Section 3.2: Test numerical accuracy requirements
                accuracy_tests = [
                    ("convert_string_to_int", ["999"], 999, "SRS: large string number conversion accuracy"),
                    ("convert_float_to_int", [99.99], 99, "SRS: float truncation accuracy (not rounding)"),
                    ("convert_hex_to_int", ["DEAD"], 57005, "SRS: complex hex value conversion accuracy"),
                    ("convert_hex_to_int", ["ff"], 255, "SRS: lowercase hex handling"),
                    ("convert_hex_to_int", ["FF"], 255, "SRS: uppercase hex handling")
                ]
                
                for func_name, args, expected, description in accuracy_tests:
                    result = safely_call_function(self.module_obj, func_name, *args)
                    if result != expected:
                        errors.append(f"{func_name} accuracy test failed for {description}: expected {expected}, got {result}")
                
                # SRS Section 3.2.2: Specific truncation test (not rounding)
                truncation_tests = [
                    (1.1, 1, "1.1 should truncate to 1, not round to 1"),
                    (1.9, 1, "1.9 should truncate to 1, not round to 2"),
                    (98.7, 98, "SRS example: 98.7 should truncate to 98"),
                    (99.999, 99, "99.999 should truncate to 99, not round to 100")
                ]
                
                for input_val, expected, description in truncation_tests:
                    result = safely_call_function(self.module_obj, "convert_float_to_int", input_val)
                    if result != expected:
                        errors.append(f"Truncation test failed: {description}, got {result}")
            
            # Final assertion
            if errors:
                self.test_obj.yakshaAssert("TestDataTypeHandling", False, "functional")
                print("TestDataTypeHandling = Failed")
            else:
                self.test_obj.yakshaAssert("TestDataTypeHandling", True, "functional")
                print("TestDataTypeHandling = Passed")
                
        except Exception as e:
            self.test_obj.yakshaAssert("TestDataTypeHandling", False, "functional")
            print("TestDataTypeHandling = Failed")

    def test_main_program_structure(self):
        """Test main program structure per SRS Section 5.3: Main Program Implementation"""
        try:
            # Check if main file exists
            main_file = None
            for filename in ['skeleton.py']:
                if check_file_exists(filename):
                    main_file = filename
                    break
            
            if main_file is None:
                self.test_obj.yakshaAssert("TestMainProgramStructure", False, "functional")
                print("TestMainProgramStructure = Failed")
                return
            
            # Create a list to collect errors
            errors = []
            
            with open(main_file, 'r') as file:
                content = file.read()
            
            # SRS Section 5.3: Check main execution block structure
            if 'if __name__ == "__main__"' not in content:
                errors.append("Missing main execution block - required by SRS Section 5.3")
            else:
                main_block_start = content.find('if __name__ == "__main__"')
                main_block_content = content[main_block_start:]
                
                # SRS Section 5.3: Required function calls in main block
                required_function_calls = [
                    ('convert_string_to_int', 'SRS Section 5.3: must call convert_string_to_int for mining_points'),
                    ('convert_float_to_int', 'SRS Section 5.3: must call convert_float_to_int for combat_points'), 
                    ('convert_hex_to_int', 'SRS Section 5.3: must call convert_hex_to_int for achievement_bonus'),
                    ('convert_score_to_string', 'SRS Section 5.3: must call convert_score_to_string for score_display'),
                    ('create_player_list', 'SRS Section 5.3: must call create_player_list for player_stats')
                ]
                
                for func_call, requirement in required_function_calls:
                    if func_call not in main_block_content:
                        errors.append(f"Main block missing {func_call} call - {requirement}")
                
                # SRS Section 4.2: Check for required input sections
                input_requirements = [
                    (r'input\s*\(\s*["\'].*mining', 'SRS Section 4.2: must get mining score input'),
                    (r'input\s*\(\s*["\'].*combat', 'SRS Section 4.2: must get combat score input'),
                    (r'input\s*\(\s*["\'].*achievement', 'SRS Section 4.2: must get achievement hex input'),
                    (r'input\s*\(\s*["\'].*player.*name', 'SRS Section 4.2: must get player name input')
                ]
                
                for pattern, requirement in input_requirements:
                    if not re.search(pattern, main_block_content, re.IGNORECASE):
                        errors.append(f"Main block missing required input - {requirement}")
                
                # SRS Section 4.3: Check for conversion section requirements
                conversion_requirements = [
                    ('mining_points', 'SRS Section 4.3: must create mining_points variable'),
                    ('combat_points', 'SRS Section 4.3: must create combat_points variable'),
                    ('achievement_bonus', 'SRS Section 4.3: must create achievement_bonus variable'),
                    ('total_score', 'SRS Section 4.3: must calculate total_score'),
                    ('score_display', 'SRS Section 4.3: must create score_display'),
                    ('player_stats', 'SRS Section 4.3: must create player_stats')
                ]
                
                for var_name, requirement in conversion_requirements:
                    if var_name not in main_block_content:
                        errors.append(f"Main block missing variable {var_name} - {requirement}")
                
                # SRS Section 4.4: Check for output section requirements
                output_requirements = [
                    ('print', 'SRS Section 4.4: must have print statements for output'),
                    ('Mining Points:', 'SRS Section 3.3.2: must display "Mining Points: {value}"'),
                    ('Combat Points:', 'SRS Section 3.3.2: must display "Combat Points: {value}"'),
                    ('Achievement Bonus:', 'SRS Section 3.3.2: must display "Achievement Bonus: {value}"'),
                    ('Total Score:', 'SRS Section 3.3.2: must display "Total Score: {value}"')
                ]
                
                for requirement, description in output_requirements:
                    if requirement not in main_block_content:
                        errors.append(f"Main block missing output requirement - {description}")
                
                # SRS Section 6: Check for welcome header
                welcome_requirements = [
                    ('Minecraft', 'SRS Section 6: should display Minecraft-related header'),
                    ('Score', 'SRS Section 6: should mention scoring system')
                ]
                
                for requirement, description in welcome_requirements:
                    if requirement not in main_block_content:
                        errors.append(f"Main block missing welcome element - {description}")
                
                # SRS Section 3.2.4: Check for total score calculation
                total_calc_pattern = r'total_score\s*=.*\+.*\+'
                if not re.search(total_calc_pattern, main_block_content):
                    errors.append("Main block must calculate total_score as sum of all points - SRS Section 3.2.4")
                
                # SRS Section 3.1.2: Check for float conversion
                float_conv_pattern = r'float\s*\('
                if not re.search(float_conv_pattern, main_block_content):
                    errors.append("Main block must convert combat input to float - SRS Section 3.1.2")
            
            # Final assertion
            if errors:
                self.test_obj.yakshaAssert("TestMainProgramStructure", False, "functional")
                print("TestMainProgramStructure = Failed")
            else:
                self.test_obj.yakshaAssert("TestMainProgramStructure", True, "functional")
                print("TestMainProgramStructure = Passed")
                
        except Exception as e:
            self.test_obj.yakshaAssert("TestMainProgramStructure", False, "functional")
            print("TestMainProgramStructure = Failed")

    def test_srs_output_format_compliance(self):
        """Test output format compliance per SRS Section 3.3: Output Constraints"""
        try:
            # Check if main file exists
            main_file = None
            for filename in ['skeleton.py']:
                if check_file_exists(filename):
                    main_file = filename
                    break
            
            if main_file is None:
                self.test_obj.yakshaAssert("TestSRSOutputFormatCompliance", False, "functional")
                print("TestSRSOutputFormatCompliance = Failed")
                return
            
            # Create a list to collect errors
            errors = []
            
            with open(main_file, 'r') as file:
                content = file.read()
            
            # Check if main execution block exists
            if 'if __name__ == "__main__"' not in content:
                errors.append("Missing main execution block - required for output format testing")
            else:
                main_block_start = content.find('if __name__ == "__main__"')
                main_block_content = content[main_block_start:]
                
                # SRS Section 3.3.2: Required Output Format checks
                required_output_formats = [
                    (r'Mining Points:\s*\{.*\}', 'SRS Section 3.3.2: must show "Mining Points: {value}"'),
                    (r'Combat Points:\s*\{.*\}', 'SRS Section 3.3.2: must show "Combat Points: {value}"'),
                    (r'Achievement Bonus:\s*\{.*\}', 'SRS Section 3.3.2: must show "Achievement Bonus: {value}"'),
                    (r'Total Score:\s*\{.*\}', 'SRS Section 3.3.2: must show "Total Score: {value}"')
                ]
                
                for pattern, requirement in required_output_formats:
                    if not re.search(pattern, main_block_content, re.IGNORECASE):
                        errors.append(f"Output format missing - {requirement}")
                
                # SRS Section 3.3.1: Check for score_display variable usage
                if 'score_display' not in main_block_content:
                    errors.append("Must use score_display variable for total score display - SRS Section 3.3.1")
                
                # SRS Section 3.1.5: Check for player_stats variable usage
                if 'player_stats' not in main_block_content:
                    errors.append("Must create and use player_stats variable - SRS Section 3.1.5")
                
                # Check for proper variable formatting in print statements
                format_checks = [
                    ('mining_points', 'Mining Points'),
                    ('combat_points', 'Combat Points'),
                    ('achievement_bonus', 'Achievement Bonus'),
                    ('score_display', 'Total Score'),
                    ('player_stats', 'Player Stats')
                ]
                
                for var_name, display_name in format_checks:
                    if var_name in main_block_content and display_name not in main_block_content:
                        errors.append(f"Variable {var_name} used but {display_name} label missing from output - SRS Section 3.3.2")
            
            # Test function output compliance if functions exist
            if self.module_obj is not None:
                # SRS Section 5.2.1: convert_score_to_string must return exact string representation
                if check_function_exists(self.module_obj, "convert_score_to_string"):
                    if is_function_implemented(self.module_obj, "convert_score_to_string"):
                        test_score = 150
                        result = safely_call_function(self.module_obj, "convert_score_to_string", test_score)
                        if result != "150":
                            errors.append(f"convert_score_to_string must return exact string representation per SRS Section 5.2.1")
                
                # SRS Section 5.2.2: create_player_list must return exact format [name, score]
                if check_function_exists(self.module_obj, "create_player_list"):
                    if is_function_implemented(self.module_obj, "create_player_list"):
                        result = safely_call_function(self.module_obj, "create_player_list", "TestPlayer", 100)
                        if result != ["TestPlayer", 100]:
                            errors.append(f"create_player_list must return exact format [name, score] per SRS Section 5.2.2")
            
            # Final assertion
            if errors:
                self.test_obj.yakshaAssert("TestSRSOutputFormatCompliance", False, "functional")
                print("TestSRSOutputFormatCompliance = Failed")
            else:
                self.test_obj.yakshaAssert("TestSRSOutputFormatCompliance", True, "functional")
                print("TestSRSOutputFormatCompliance = Passed")
                
        except Exception as e:
            self.test_obj.yakshaAssert("TestSRSOutputFormatCompliance", False, "functional")
            print("TestSRSOutputFormatCompliance = Failed")

if __name__ == '__main__':
    unittest.main()