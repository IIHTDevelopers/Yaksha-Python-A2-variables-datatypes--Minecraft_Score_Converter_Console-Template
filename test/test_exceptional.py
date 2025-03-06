import pytest
from test.TestUtils import TestUtils
from game_score_converter import *

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