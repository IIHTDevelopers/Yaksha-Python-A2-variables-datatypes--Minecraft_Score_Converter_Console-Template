import pytest
from test.TestUtils import TestUtils
import re
import inspect
from game_score_converter import *

@pytest.fixture
def test_obj():
    return TestUtils()

def test_required_variables(test_obj):
    """Test if all required variables are defined with exact naming"""
    try:
        with open('game_score_converter.py', 'r') as file:
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
        
        all_vars_found = True
        for var_name, pattern in required_vars.items():
            if not re.search(pattern, content):
                all_vars_found = False
                test_obj.yakshaAssert("TestRequiredVariables", False, "functional")
                pytest.fail(f"Required variable '{var_name}' not found or incorrectly named")
        
        test_obj.yakshaAssert("TestRequiredVariables", all_vars_found, "functional")
    except Exception as e:
        test_obj.yakshaAssert("TestRequiredVariables", False, "functional")
        pytest.fail(f"Variable check failed: {str(e)}")

def test_conversion_implementations(test_obj):
    """Test all conversion functions together"""
    try:
        # Test string conversion
        string_result = convert_string_to_int("100")
        
        # Test float conversion
        float_result = convert_float_to_int(98.7)
        
        # Test hex conversion
        hex_result = convert_hex_to_int("1F")
        
        # Check correct implementations
        string_correct = string_result == 100
        float_correct = float_result == 98
        hex_correct = hex_result == 31
        
        all_correct = string_correct and float_correct and hex_correct
        test_obj.yakshaAssert("TestConversionImplementations", all_correct, "functional")
        
        if not all_correct:
            if not string_correct:
                pytest.fail("String conversion implementation incorrect")
            elif not float_correct:
                pytest.fail("Float conversion implementation incorrect")
            elif not hex_correct:
                pytest.fail("Hex conversion implementation incorrect")
    except Exception as e:
        test_obj.yakshaAssert("TestConversionImplementations", False, "functional")
        pytest.fail(f"Conversion test failed: {str(e)}")

if __name__ == '__main__':
    pytest.main(['-v'])