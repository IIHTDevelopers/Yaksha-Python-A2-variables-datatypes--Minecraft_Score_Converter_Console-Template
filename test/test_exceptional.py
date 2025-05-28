"""
Exception handling tests for Variables and Data Types assignment.
Tests error handling and exception cases.
"""
import pytest
import os
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

def check_raises(func, args, expected_exception=Exception):
    """Check if a function raises an expected exception."""
    try:
        func(*args)
        return False
    except expected_exception:
        return True
    except Exception:
        return False

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

class TestExceptional:
    """Test class for exception handling tests of the Variables and Data Types assignment."""
    
    def setup_method(self):
        """Setup test data before each test method."""
        # Import the module under test
        self.module_obj = safely_import_module("skeleton")
        if self.module_obj is None:
            self.module_obj = safely_import_module("game_score_converter")
        
        # Test object for assertions
        self.test_obj = TestUtils()

    def test_string_float_exception(self):
        """Test string and float conversion with invalid inputs"""
        # Check if module exists
        if self.module_obj is None:
            self.test_obj.yakshaAssert("TestStringFloatException", False, "exception")
            pytest.fail("Could not import skeleton or game_score_converter module")
            return
        
        # Check required functions
        required_functions = ["convert_string_to_int", "convert_float_to_int"]
        
        missing_functions = []
        for func_name in required_functions:
            if not check_function_exists(self.module_obj, func_name):
                missing_functions.append(func_name)
        
        if missing_functions:
            error_msg = f"Missing required functions: {', '.join(missing_functions)}"
            self.test_obj.yakshaAssert("TestStringFloatException", False, "exception")
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
            
            # Test string conversion exception handling
            if is_function_implemented(self.module_obj, "convert_string_to_int"):
                string_invalid_cases = [
                    ("abc", "non-numeric string"),
                    ("-100", "negative string"),
                    ("12.5", "decimal string"),
                    ("", "empty string"),
                    ("12a", "mixed alphanumeric")
                ]
                
                for input_val, description in string_invalid_cases:
                    func = getattr(self.module_obj, "convert_string_to_int")
                    if not check_raises(func, [input_val], ValueError):
                        errors.append(f"convert_string_to_int should raise ValueError for {description}: '{input_val}'")
            
            # Test float conversion exception handling
            if is_function_implemented(self.module_obj, "convert_float_to_int"):
                float_invalid_cases = [
                    ("98.7", "string input instead of float"),
                    (-98.7, "negative float"),
                    (None, "None input"),
                    ("invalid", "non-numeric string")
                ]
                
                for input_val, description in float_invalid_cases:
                    func = getattr(self.module_obj, "convert_float_to_int")
                    if not check_raises(func, [input_val], ValueError):
                        errors.append(f"convert_float_to_int should raise ValueError for {description}: {input_val}")
            
            # Final assertion
            if errors:
                self.test_obj.yakshaAssert("TestStringFloatException", False, "exception")
                pytest.fail("\n".join(errors))
            else:
                self.test_obj.yakshaAssert("TestStringFloatException", True, "exception")
                
        except Exception as e:
            self.test_obj.yakshaAssert("TestStringFloatException", False, "exception")
            pytest.fail(f"String/Float exception test failed: {str(e)}")

    def test_hex_conversion_exception(self):
        """Test hex conversion with invalid inputs"""
        # Check if module exists
        if self.module_obj is None:
            self.test_obj.yakshaAssert("TestHexConversionException", False, "exception")
            pytest.fail("Could not import skeleton or game_score_converter module")
            return
        
        # Check required function
        if not check_function_exists(self.module_obj, "convert_hex_to_int"):
            self.test_obj.yakshaAssert("TestHexConversionException", False, "exception")
            pytest.fail("Missing required function: convert_hex_to_int")
            return
        
        # Create a list to collect errors
        errors = []
        
        try:
            # Check if function is implemented
            if not is_function_implemented(self.module_obj, "convert_hex_to_int"):
                errors.append("convert_hex_to_int is not implemented (contains only pass/return None)")
            
            # Test hex conversion exception handling
            if is_function_implemented(self.module_obj, "convert_hex_to_int"):
                hex_invalid_cases = [
                    ("XYZ", "invalid hex characters"),
                    ("-1F", "negative hex"),
                    ("", "empty string"),
                    ("GG", "invalid hex digits"),
                    ("12.5", "decimal in hex"),
                    (None, "None input"),
                    (123, "integer input instead of string")
                ]
                
                for input_val, description in hex_invalid_cases:
                    func = getattr(self.module_obj, "convert_hex_to_int")
                    if not check_raises(func, [input_val], ValueError):
                        errors.append(f"convert_hex_to_int should raise ValueError for {description}: {input_val}")
            
            # Final assertion
            if errors:
                self.test_obj.yakshaAssert("TestHexConversionException", False, "exception")
                pytest.fail("\n".join(errors))
            else:
                self.test_obj.yakshaAssert("TestHexConversionException", True, "exception")
                
        except Exception as e:
            self.test_obj.yakshaAssert("TestHexConversionException", False, "exception")
            pytest.fail(f"Hex conversion exception test failed: {str(e)}")

if __name__ == '__main__':
    pytest.main(['-v'])