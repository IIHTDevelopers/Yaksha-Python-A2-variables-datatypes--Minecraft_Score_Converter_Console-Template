import pytest
from test.TestUtils import TestUtils
from game_score_converter import *

test_obj = TestUtils()

def test_string_float_conversion_boundary():
    """Test string and float conversion with boundary values"""
    try:
        # String conversion tests
        string_min = convert_string_to_int("0") == 0
        string_max = convert_string_to_int("999999") == 999999
        
        # Float conversion tests
        float_min = convert_float_to_int(0.1) == 0
        float_max = convert_float_to_int(999999.9) == 999999
        
        all_passed = string_min and string_max and float_min and float_max
        test_obj.yakshaAssert("TestStringFloatBoundary", all_passed, "boundary")
        
        if not all_passed:
            if not (string_min and string_max):
                pytest.fail("String conversion boundary test failed")
            else:
                pytest.fail("Float conversion boundary test failed")
    except Exception as e:
        test_obj.yakshaAssert("TestStringFloatBoundary", False, "boundary")

def test_hex_conversion_boundary():
    """Test hex conversion with boundary values"""
    try:
        result1 = convert_hex_to_int("0") == 0
        result2 = convert_hex_to_int("FF") == 255
        
        if result1 and result2:
            test_obj.yakshaAssert("TestHexConversionBoundary", True, "boundary")
        else:
            test_obj.yakshaAssert("TestHexConversionBoundary", False, "boundary")
            pytest.fail("Hex conversion boundary test failed")
    except Exception as e:
        test_obj.yakshaAssert("TestHexConversionBoundary", False, "boundary")