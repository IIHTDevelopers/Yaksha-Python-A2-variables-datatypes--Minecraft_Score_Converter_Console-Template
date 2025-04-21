import pytest
from test.TestUtils import TestUtils

# Try to import, but if it fails, create dummy functions
try:
    from game_score_converter import (
        convert_string_to_int,
        convert_float_to_int,
        convert_hex_to_int
    )
except Exception as e:
    # Define dummy functions that will cause tests to fail gracefully
    def convert_string_to_int(mining_score):
        raise Exception("Function not properly implemented")
    
    def convert_float_to_int(combat_score):
        raise Exception("Function not properly implemented")
        
    def convert_hex_to_int(achievement_hex):
        raise Exception("Function not properly implemented")

test_obj = TestUtils()

def test_string_float_exception():
    """Test string and float conversion with invalid inputs"""
    try:
        # String conversion exception tests
        with pytest.raises(ValueError):
            convert_string_to_int("abc")
        with pytest.raises(ValueError):
            convert_string_to_int("-100")
            
        # Float conversion exception tests
        with pytest.raises(ValueError):
            convert_float_to_int("98.7")
        with pytest.raises(ValueError):
            convert_float_to_int(-98.7)
            
        test_obj.yakshaAssert("TestStringFloatException", True, "exception")
    except Exception as e:
        test_obj.yakshaAssert("TestStringFloatException", False, "exception")
        print("TestStringFloatException = Failed")

def test_hex_conversion_exception():
    """Test hex conversion with invalid inputs"""
    try:
        with pytest.raises(ValueError):
            convert_hex_to_int("XYZ")
        with pytest.raises(ValueError):
            convert_hex_to_int("-1F")
            
        test_obj.yakshaAssert("TestHexConversionException", True, "exception")
    except Exception as e:
        test_obj.yakshaAssert("TestHexConversionException", False, "exception")
        print("TestHexConversionException = Failed")