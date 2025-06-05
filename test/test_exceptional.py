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

def check_raises_exception(func, args, expected_exception=ValueError):
    """Check if a function raises the expected exception type."""
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            func(*args)
        return False  # No exception was raised
    except expected_exception:
        return True  # Expected exception was raised
    except Exception:
        return False  # Different exception was raised

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

class TestMinecraftException(unittest.TestCase):
    """Test class for comprehensive exception handling in the Minecraft Score Converter."""
    
    def setUp(self):
        """Setup test data before each test method."""
        self.test_obj = TestUtils()
        self.module_obj = load_module_dynamically()
        
        # Check basic requirements once
        if self.module_obj is None:
            self.skipTest("Module could not be imported")
        
        required_functions = [
            "convert_string_to_int", "convert_float_to_int", 
            "convert_hex_to_int", "convert_score_to_string", "create_player_list"
        ]
        
        missing_functions = []
        for func_name in required_functions:
            if not check_function_exists(self.module_obj, func_name):
                missing_functions.append(func_name)
        
        if missing_functions:
            self.skipTest(f"Missing functions: {missing_functions}")
    
    def test_comprehensive_exception_handling(self):
        """Test all exception scenarios across all functions with complete coverage"""
        try:
            required_functions = [
                "convert_string_to_int", "convert_float_to_int", 
                "convert_hex_to_int", "convert_score_to_string", "create_player_list"
            ]
            
            errors = []
            
            # Check if all functions are implemented
            unimplemented_functions = []
            for func_name in required_functions:
                if not is_function_implemented(self.module_obj, func_name):
                    unimplemented_functions.append(func_name)
            
            if unimplemented_functions:
                errors.append(f"Functions not implemented: {', '.join(unimplemented_functions)}")
            
            # === CONVERSION FUNCTION EXCEPTION TESTS ===
            
            # STRING CONVERSION EXCEPTION TESTS
            if is_function_implemented(self.module_obj, "convert_string_to_int"):
                string_cases = [
                    # Basic invalid cases
                    ("", "empty string"), (" ", "space string"), ("abc", "non-numeric string"),
                    ("12.5", "decimal string"), ("-100", "negative string"), ("+123", "positive sign"),
                    # Advanced cases
                    ("0x1F", "hex notation"), ("1e5", "scientific notation"), ("∞", "infinity symbol"),
                    ("①", "unicode number"), (" 123", "leading space"), ("123 ", "trailing space"),
                    # Non-string types
                    (123, "integer input"), (12.5, "float input"), (None, "None input"),
                    ([], "list input"), ({}, "dictionary input"), (True, "boolean True"),
                    (False, "boolean False"), (complex(1, 2), "complex number")
                ]
                
                func = getattr(self.module_obj, "convert_string_to_int")
                for input_val, description in string_cases:
                    if not check_raises_exception(func, [input_val], ValueError):
                        errors.append(f"convert_string_to_int should raise ValueError for {description}: {input_val}")
            
            # FLOAT CONVERSION EXCEPTION TESTS
            if is_function_implemented(self.module_obj, "convert_float_to_int"):
                float_cases = [
                    # Negative floats (SRS violation)
                    (-98.7, "negative float"), (-0.1, "small negative"), (-1.0, "negative one"),
                    (-100.0, "large negative"), (-999.9, "very large negative"),
                    # Wrong types
                    ("98.7", "string input"), ("12.5", "numeric string"), ("abc", "non-numeric string"),
                    (123, "integer input"), (None, "None input"), ([], "list input"),
                    ({}, "dictionary input"), (True, "boolean True"), (False, "boolean False"),
                    (complex(1, 2), "complex number"), ("", "empty string"), (" ", "space string"),
                    ("inf", "infinity string"), ("nan", "NaN string")
                ]
                
                func = getattr(self.module_obj, "convert_float_to_int")
                for input_val, description in float_cases:
                    if not check_raises_exception(func, [input_val], ValueError):
                        errors.append(f"convert_float_to_int should raise ValueError for {description}: {input_val}")
            
            # HEX CONVERSION EXCEPTION TESTS
            if is_function_implemented(self.module_obj, "convert_hex_to_int"):
                hex_cases = [
                    # Invalid hex cases
                    ("", "empty string"), (" ", "space string"), ("XYZ", "invalid characters"),
                    ("GG", "invalid G"), ("1G", "mixed valid/invalid"), ("-1F", "negative hex"),
                    # Spaces and special notation
                    ("FF ", "trailing space"), (" FF", "leading space"), ("F F", "internal space"),
                    ("0x1F", "hex prefix"), ("12.5", "decimal in hex"),
                    # Wrong types
                    (123, "integer input"), (12.5, "float input"), (None, "None input"),
                    ([], "list input"), ({}, "dictionary input"), (True, "boolean True"),
                    (False, "boolean False"), (complex(1, 2), "complex number")
                ]
                
                func = getattr(self.module_obj, "convert_hex_to_int")
                for input_val, description in hex_cases:
                    if not check_raises_exception(func, [input_val], ValueError):
                        errors.append(f"convert_hex_to_int should raise ValueError for {description}: {input_val}")
            
            # === OUTPUT FUNCTION EXCEPTION TESTS ===
            
            # SCORE DISPLAY CONVERSION EXCEPTION TESTS
            if is_function_implemented(self.module_obj, "convert_score_to_string"):
                score_cases = [
                    # String inputs (should be numeric)
                    ("150", "string input"), ("0", "zero string"), ("abc", "non-numeric string"),
                    ("12.5", "decimal string"), ("", "empty string"), (" ", "space string"),
                    # Non-numeric types
                    (None, "None input"), ([], "list input"), ({}, "dictionary input"),
                    (True, "boolean True"), (False, "boolean False"), (set(), "set input"),
                    (tuple(), "tuple input"), (complex(1, 2), "complex number"),
                ]
                
                func = getattr(self.module_obj, "convert_score_to_string")
                for input_val, description in score_cases:
                    if not check_raises_exception(func, [input_val], ValueError):
                        errors.append(f"convert_score_to_string should raise ValueError for {description}: {input_val}")
            
            # PLAYER LIST CREATION EXCEPTION TESTS
            if is_function_implemented(self.module_obj, "create_player_list"):
                player_cases = [
                    # Empty/whitespace names
                    ("", 100, "empty string name"), ("   ", 100, "whitespace name"),
                    ("\t", 100, "tab name"), ("\n", 100, "newline name"),
                    # Non-string name types
                    (None, 100, "None name"), (123, 100, "integer name"), (12.5, 100, "float name"),
                    ([], 100, "list name"), ({}, 100, "dictionary name"), (True, 100, "boolean True name"),
                    (False, 100, "boolean False name"), (set(), 100, "set name"), (tuple(), 100, "tuple name"),
                    (complex(1, 2), 100, "complex number name"),
                ]
                
                func = getattr(self.module_obj, "create_player_list")
                for name_val, score_val, description in player_cases:
                    if not check_raises_exception(func, [name_val, score_val], ValueError):
                        errors.append(f"create_player_list should raise ValueError for {description}: name={name_val}")
            
            # === CROSS-FUNCTION TYPE VALIDATION AND ADVANCED EDGE CASES ===
            
            # Advanced invalid input types that should fail across multiple functions
            advanced_invalid_types = [
                (lambda x: x, "lambda function"),
                (object(), "generic object"),
                (set(), "empty set"),
                ({1, 2, 3}, "non-empty set"),
                (tuple(), "empty tuple"),
                ((1, 2, 3), "non-empty tuple"),
            ]
            
            # Test string and hex functions with advanced types
            for func_name in ["convert_string_to_int", "convert_hex_to_int"]:
                if is_function_implemented(self.module_obj, func_name):
                    func = getattr(self.module_obj, func_name)
                    for invalid_input, type_description in advanced_invalid_types:
                        if not check_raises_exception(func, [invalid_input], ValueError):
                            errors.append(f"{func_name} should raise ValueError for {type_description}")
            
            # Test float function with advanced types
            if is_function_implemented(self.module_obj, "convert_float_to_int"):
                func = getattr(self.module_obj, "convert_float_to_int")
                for invalid_input, type_description in advanced_invalid_types:
                    if not check_raises_exception(func, [invalid_input], ValueError):
                        errors.append(f"convert_float_to_int should raise ValueError for {type_description}")
            
            # Test score function with advanced types (excluding valid int and float)
            if is_function_implemented(self.module_obj, "convert_score_to_string"):
                func = getattr(self.module_obj, "convert_score_to_string")
                score_invalid_types = [
                    (None, "None input"), ([], "list input"), ({}, "dictionary input"),
                    (True, "boolean input"), (complex(1, 2), "complex number input"),
                    (set(), "set input"), (tuple(), "tuple input"), ("string", "string input")
                ]
                
                for invalid_input, type_description in score_invalid_types:
                    if not check_raises_exception(func, [invalid_input], ValueError):
                        errors.append(f"convert_score_to_string should raise ValueError for {type_description}")
            
            # Test player list function with advanced name types
            if is_function_implemented(self.module_obj, "create_player_list"):
                func = getattr(self.module_obj, "create_player_list")
                for invalid_input, type_description in advanced_invalid_types:
                    if not check_raises_exception(func, [invalid_input, 100], ValueError):
                        errors.append(f"create_player_list should raise ValueError for {type_description} as name parameter")
            
            # SRS-specific validation: negative float validation
            if is_function_implemented(self.module_obj, "convert_float_to_int"):
                func = getattr(self.module_obj, "convert_float_to_int")
                srs_negative_cases = [
                    (-0.1, "small negative per SRS"), (-1.0, "negative one per SRS"),
                    (-98.7, "SRS example negative"), (-999.9, "large negative per SRS")
                ]
                
                for negative_val, description in srs_negative_cases:
                    if not check_raises_exception(func, [negative_val], ValueError):
                        errors.append(f"convert_float_to_int should raise ValueError for {description}: {negative_val}")
            
            # Final assertion
            if errors:
                self.test_obj.yakshaAssert("TestComprehensiveExceptionHandling", False, "exception")
                print("TestComprehensiveExceptionHandling = Failed")
            else:
                self.test_obj.yakshaAssert("TestComprehensiveExceptionHandling", True, "exception")
                print("TestComprehensiveExceptionHandling = Passed")
                
        except Exception as e:
            self.test_obj.yakshaAssert("TestComprehensiveExceptionHandling", False, "exception")
            print("TestComprehensiveExceptionHandling = Failed")

if __name__ == '__main__':
    unittest.main()