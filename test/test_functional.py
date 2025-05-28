"""
Functional tests for Variables and Data Types assignment.
Tests the correctness of the implementation logic.
"""
import pytest
import os
import re
import importlib
import inspect
from test.TestUtils import TestUtils

# Utility functions for resilient testing
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

class TestFunctional:
    """Test class for functional tests of the Variables and Data Types assignment."""
    
    def setup_method(self):
        """Setup test data before each test method."""
        # Import the module under test
        self.module_obj = safely_import_module("skeleton")
        if self.module_obj is None:
            self.module_obj = safely_import_module("game_score_converter")
        
        # Test object for assertions
        self.test_obj = TestUtils()

    def test_required_variables(self):
        """Test if all required variables are defined with exact naming"""
        # Check if main file exists
        main_file = None
        for filename in ['game_score_converter.py', 'skeleton.py']:
            if check_file_exists(filename):
                main_file = filename
                break
        
        if main_file is None:
            self.test_obj.yakshaAssert("TestRequiredVariables", False, "functional")
            pytest.fail("Could not find game_score_converter.py or skeleton.py file")
            return
        
        # Create a list to collect errors
        errors = []
        
        try:
            with open(main_file, 'r') as file:
                content = file.read()
            
            required_vars = {
                'mining_score': r'mining_score\s*=',
                'mining_points': r'mining_points\s*=',
                'combat_score': r'combat_score\s*=',
                'combat_points': r'combat_points\s*=',
                'achievement_hex': r'achievement_hex\s*=',
                'achievement_bonus': r'achievement_bonus\s*=',
                'total_score': r'total_score\s*=',
                'score_display': r'score_display\s*=',
                'player_stats': r'player_stats\s*='
            }
            
            # Check if main execution block exists
            if 'if __name__ == "__main__"' not in content:
                errors.append("Missing main execution block (if __name__ == '__main__')")
            
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
                    errors.append("Main execution block is not implemented (contains only pass or comments)")
                else:
                    # Check for required variables only if main block is implemented
                    for var_name, pattern in required_vars.items():
                        if not re.search(pattern, main_block_content):
                            errors.append(f"Required variable '{var_name}' not found in main block or incorrectly named")
            
            # Final assertion
            if errors:
                self.test_obj.yakshaAssert("TestRequiredVariables", False, "functional")
                pytest.fail("\n".join(errors))
            else:
                self.test_obj.yakshaAssert("TestRequiredVariables", True, "functional")
                
        except Exception as e:
            self.test_obj.yakshaAssert("TestRequiredVariables", False, "functional")
            pytest.fail(f"Required variables test failed: {str(e)}")

    def test_conversion_implementations(self):
        """Test all conversion functions together"""
        # Check if module exists
        if self.module_obj is None:
            self.test_obj.yakshaAssert("TestConversionImplementations", False, "functional")
            pytest.fail("Could not import skeleton or game_score_converter module")
            return
        
        # Check required functions
        required_functions = ["convert_string_to_int", "convert_float_to_int", "convert_hex_to_int"]
        
        missing_functions = []
        for func_name in required_functions:
            if not check_function_exists(self.module_obj, func_name):
                missing_functions.append(func_name)
        
        if missing_functions:
            error_msg = f"Missing required functions: {', '.join(missing_functions)}"
            self.test_obj.yakshaAssert("TestConversionImplementations", False, "functional")
            pytest.fail(error_msg)
            return
        
        # Create a list to collect errors
        errors = []
        
        try:
            # Check if functions are implemented
            unimplemented_functions = []
            for func_name in required_functions:
                if not is_function_implemented(self.module_obj, func_name):
                    unimplemented_functions.append(func_name)
            
            if unimplemented_functions:
                errors.append(f"Functions not implemented (contain only pass/return None): {', '.join(unimplemented_functions)}")
            
            # Test string conversion
            if is_function_implemented(self.module_obj, "convert_string_to_int"):
                string_result = safely_call_function(self.module_obj, "convert_string_to_int", "100")
                if string_result is None:
                    errors.append("convert_string_to_int returned None for valid input")
                elif string_result != 100:
                    errors.append(f"convert_string_to_int('100') should return 100, got {string_result}")
            
            # Test float conversion
            if is_function_implemented(self.module_obj, "convert_float_to_int"):
                float_result = safely_call_function(self.module_obj, "convert_float_to_int", 98.7)
                if float_result is None:
                    errors.append("convert_float_to_int returned None for valid input")
                elif float_result != 98:
                    errors.append(f"convert_float_to_int(98.7) should return 98, got {float_result}")
            
            # Test hex conversion
            if is_function_implemented(self.module_obj, "convert_hex_to_int"):
                hex_result = safely_call_function(self.module_obj, "convert_hex_to_int", "1F")
                if hex_result is None:
                    errors.append("convert_hex_to_int returned None for valid input")
                elif hex_result != 31:
                    errors.append(f"convert_hex_to_int('1F') should return 31, got {hex_result}")
            
            # Test additional functions if they exist
            if check_function_exists(self.module_obj, "convert_score_to_string"):
                if is_function_implemented(self.module_obj, "convert_score_to_string"):
                    score_str_result = safely_call_function(self.module_obj, "convert_score_to_string", 150)
                    if score_str_result is None:
                        errors.append("convert_score_to_string returned None for valid input")
                    elif score_str_result != "150":
                        errors.append(f"convert_score_to_string(150) should return '150', got {score_str_result}")
            
            if check_function_exists(self.module_obj, "create_player_list"):
                if is_function_implemented(self.module_obj, "create_player_list"):
                    player_list_result = safely_call_function(self.module_obj, "create_player_list", "Steve", 100)
                    if player_list_result is None:
                        errors.append("create_player_list returned None for valid input")
                    elif player_list_result != ["Steve", 100]:
                        errors.append(f"create_player_list('Steve', 100) should return ['Steve', 100], got {player_list_result}")
            
            # Final assertion
            if errors:
                self.test_obj.yakshaAssert("TestConversionImplementations", False, "functional")
                pytest.fail("\n".join(errors))
            else:
                self.test_obj.yakshaAssert("TestConversionImplementations", True, "functional")
                
        except Exception as e:
            self.test_obj.yakshaAssert("TestConversionImplementations", False, "functional")
            pytest.fail(f"Conversion implementations test failed: {str(e)}")

    def test_function_existence(self):
        """Test that all required functions exist and are callable"""
        # Check if module exists
        if self.module_obj is None:
            self.test_obj.yakshaAssert("TestFunctionExistence", False, "functional")
            pytest.fail("Could not import skeleton or game_score_converter module")
            return
        
        # Collect errors
        errors = []
        
        # Check required functions
        required_functions = [
            "convert_string_to_int",
            "convert_float_to_int", 
            "convert_hex_to_int",
            "convert_score_to_string",
            "create_player_list"
        ]
        
        for func_name in required_functions:
            if not check_function_exists(self.module_obj, func_name):
                errors.append(f"Required function {func_name} is missing")
            else:
                # Check if function has proper docstring
                func_obj = getattr(self.module_obj, func_name)
                if func_obj.__doc__ is None or len(func_obj.__doc__.strip()) < 10:
                    errors.append(f"Function {func_name} should have a meaningful docstring")
        
        # Report results
        if errors:
            self.test_obj.yakshaAssert("TestFunctionExistence", False, "functional")
            pytest.fail("\n".join(errors))
        else:
            self.test_obj.yakshaAssert("TestFunctionExistence", True, "functional")

    def test_implementation_quality(self):
        """Test implementation quality and best practices"""
        # Check if module exists
        if self.module_obj is None:
            self.test_obj.yakshaAssert("TestImplementationQuality", False, "functional")
            pytest.fail("Could not import skeleton or game_score_converter module")
            return
        
        # Collect errors
        errors = []
        
        # Check required functions exist
        required_functions = [
            "convert_string_to_int",
            "convert_float_to_int",
            "convert_hex_to_int"
        ]
        
        for func_name in required_functions:
            if not check_function_exists(self.module_obj, func_name):
                errors.append(f"Required function {func_name} is missing")
            elif not is_function_implemented(self.module_obj, func_name):
                errors.append(f"Required function {func_name} is not implemented (contains only pass/return None)")
        
        if errors:
            self.test_obj.yakshaAssert("TestImplementationQuality", False, "functional")
            pytest.fail("\n".join(errors))
            return
        
        try:
            # Test that functions handle correct data types
            test_cases = [
                ("convert_string_to_int", ["42"], 42, "string to int conversion"),
                ("convert_float_to_int", [3.14], 3, "float to int conversion"),
                ("convert_hex_to_int", ["A"], 10, "hex to int conversion")
            ]
            
            for func_name, args, expected, description in test_cases:
                if is_function_implemented(self.module_obj, func_name):
                    result = safely_call_function(self.module_obj, func_name, *args)
                    if result is None:
                        errors.append(f"{func_name} returned None for {description}")
                    elif result != expected:
                        errors.append(f"{func_name} failed {description}: expected {expected}, got {result}")
            
            # Test edge cases
            edge_cases = [
                ("convert_string_to_int", ["0"], 0, "zero string conversion"),
                ("convert_float_to_int", [0.0], 0, "zero float conversion"),
                ("convert_hex_to_int", ["0"], 0, "zero hex conversion")
            ]
            
            for func_name, args, expected, description in edge_cases:
                if is_function_implemented(self.module_obj, func_name):
                    result = safely_call_function(self.module_obj, func_name, *args)
                    if result is None:
                        errors.append(f"{func_name} returned None for {description}")
                    elif result != expected:
                        errors.append(f"{func_name} failed {description}: expected {expected}, got {result}")
            
            # Report results
            if errors:
                self.test_obj.yakshaAssert("TestImplementationQuality", False, "functional")
                pytest.fail("\n".join(errors))
            else:
                self.test_obj.yakshaAssert("TestImplementationQuality", True, "functional")
                
        except Exception as e:
            self.test_obj.yakshaAssert("TestImplementationQuality", False, "functional")
            pytest.fail(f"Implementation quality test failed: {str(e)}")

if __name__ == '__main__':
    pytest.main(['-v'])