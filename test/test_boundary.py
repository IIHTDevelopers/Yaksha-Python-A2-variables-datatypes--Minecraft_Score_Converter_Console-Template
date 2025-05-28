"""
Boundary tests for Variables and Data Types assignment.
Tests edge cases and limits of the implementation.
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

class TestBoundary:
    """Test class for boundary tests of the Variables and Data Types assignment."""
    
    def setup_method(self):
        """Setup test data before each test method."""
        # Import the module under test
        self.module_obj = safely_import_module("skeleton")
        if self.module_obj is None:
            self.module_obj = safely_import_module("game_score_converter")
        
        # Test object for assertions
        self.test_obj = TestUtils()

    def test_string_float_conversion_boundary(self):
        """Test string and float conversion with boundary values"""
        # Check if module exists
        if self.module_obj is None:
            self.test_obj.yakshaAssert("TestStringFloatBoundary", False, "boundary")
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
            self.test_obj.yakshaAssert("TestStringFloatBoundary", False, "boundary")
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
            
            # Test string conversion with boundary values
            if is_function_implemented(self.module_obj, "convert_string_to_int"):
                string_test_cases = [
                    ("0", 0, "zero string"),
                    ("999999", 999999, "large string"),
                    ("1", 1, "single digit")
                ]
                
                for input_val, expected, description in string_test_cases:
                    result = safely_call_function(self.module_obj, "convert_string_to_int", input_val)
                    if result is None:
                        errors.append(f"convert_string_to_int returned None for {description}")
                    elif result != expected:
                        errors.append(f"convert_string_to_int('{input_val}') should be {expected} for {description}, got {result}")
            
            # Test float conversion with boundary values
            if is_function_implemented(self.module_obj, "convert_float_to_int"):
                float_test_cases = [
                    (0.1, 0, "small positive float"),
                    (999999.9, 999999, "large float"),
                    (0.0, 0, "zero float"),
                    (1.0, 1, "whole number float")
                ]
                
                for input_val, expected, description in float_test_cases:
                    result = safely_call_function(self.module_obj, "convert_float_to_int", input_val)
                    if result is None:
                        errors.append(f"convert_float_to_int returned None for {description}")
                    elif result != expected:
                        errors.append(f"convert_float_to_int({input_val}) should be {expected} for {description}, got {result}")
            
            # Final assertion
            if errors:
                self.test_obj.yakshaAssert("TestStringFloatBoundary", False, "boundary")
                pytest.fail("\n".join(errors))
            else:
                self.test_obj.yakshaAssert("TestStringFloatBoundary", True, "boundary")
                
        except Exception as e:
            self.test_obj.yakshaAssert("TestStringFloatBoundary", False, "boundary")
            pytest.fail(f"String/Float conversion boundary test failed: {str(e)}")

    def test_hex_conversion_boundary(self):
        """Test hex conversion with boundary values"""
        # Check if module exists
        if self.module_obj is None:
            self.test_obj.yakshaAssert("TestHexConversionBoundary", False, "boundary")
            pytest.fail("Could not import skeleton or game_score_converter module")
            return
        
        # Check required function
        if not check_function_exists(self.module_obj, "convert_hex_to_int"):
            self.test_obj.yakshaAssert("TestHexConversionBoundary", False, "boundary")
            pytest.fail("Missing required function: convert_hex_to_int")
            return
        
        # Create a list to collect errors
        errors = []
        
        try:
            # Check if function is implemented
            if not is_function_implemented(self.module_obj, "convert_hex_to_int"):
                errors.append("convert_hex_to_int is not implemented (contains only pass/return None)")
            
            # Test hex conversion with boundary values
            if is_function_implemented(self.module_obj, "convert_hex_to_int"):
                hex_test_cases = [
                    ("0", 0, "zero hex"),
                    ("FF", 255, "max single byte hex"),
                    ("1F", 31, "medium hex value"),
                    ("A", 10, "single hex digit"),
                    ("ff", 255, "lowercase hex")
                ]
                
                for input_val, expected, description in hex_test_cases:
                    result = safely_call_function(self.module_obj, "convert_hex_to_int", input_val)
                    if result is None:
                        errors.append(f"convert_hex_to_int returned None for {description}")
                    elif result != expected:
                        errors.append(f"convert_hex_to_int('{input_val}') should be {expected} for {description}, got {result}")
            
            # Final assertion
            if errors:
                self.test_obj.yakshaAssert("TestHexConversionBoundary", False, "boundary")
                pytest.fail("\n".join(errors))
            else:
                self.test_obj.yakshaAssert("TestHexConversionBoundary", True, "boundary")
                
        except Exception as e:
            self.test_obj.yakshaAssert("TestHexConversionBoundary", False, "boundary")
            pytest.fail(f"Hex conversion boundary test failed: {str(e)}")

if __name__ == '__main__':
    pytest.main(['-v'])