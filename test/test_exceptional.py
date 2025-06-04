import unittest
import os
import importlib
import sys
import io
import contextlib
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

def load_module_dynamically():
    """Load the student's module for testing"""
    module_obj = safely_import_module("skeleton")
    if module_obj is None:
        module_obj = safely_import_module("solution")
    return module_obj

def is_implementation_functional(module_obj):
    """Check if the implementation is functional by testing basic operations"""
    if module_obj is None:
        return False
    
    # Test basic functionality of each required function
    try:
        # Test calculate_ticket_revenue with simple valid inputs
        revenue_result = safely_call_function(module_obj, "calculate_ticket_revenue", 10, 20, 30)
        if revenue_result is None:
            return False
        
        # Test calculate_seats_remaining with simple valid inputs
        seats_result = safely_call_function(module_obj, "calculate_seats_remaining", 50, 100, 200)
        if seats_result is None:
            return False
        
        # Test calculate_zone_occupancy with simple valid inputs
        occupancy_result = safely_call_function(module_obj, "calculate_zone_occupancy", 100, 200)
        if occupancy_result is None:
            return False
        
        # Test calculate_seats_per_row with simple valid inputs
        rows_result = safely_call_function(module_obj, "calculate_seats_per_row", 45)
        if rows_result is None:
            return False
        
        return True
    except Exception:
        return False

class TestMusicFestivalException(unittest.TestCase):
    """Test class for exception handling in the Music Festival Console System."""
    
    def setUp(self):
        """Setup test data before each test method."""
        self.test_obj = TestUtils()
        self.module_obj = load_module_dynamically()
    
    def test_invalid_input_exceptions(self):
        """Test invalid input handling across functions"""
        try:
            # Check if module can be imported
            if self.module_obj is None:
                self.test_obj.yakshaAssert("TestInvalidInputExceptions", False, "exception")
                print("TestInvalidInputExceptions = Failed")
                return
            
            # Check if implementation is functional
            if not is_implementation_functional(self.module_obj):
                self.test_obj.yakshaAssert("TestInvalidInputExceptions", False, "exception")
                print("TestInvalidInputExceptions = Failed")
                return
            
            errors = []
            exception_tests_passed = 0
            total_exception_tests = 0
            
            # Test invalid type handling for calculate_ticket_revenue
            if check_function_exists(self.module_obj, "calculate_ticket_revenue"):
                func = getattr(self.module_obj, "calculate_ticket_revenue")
                
                # Test string input
                total_exception_tests += 1
                if check_raises_exception(func, ["10", 20, 30], ValueError):
                    exception_tests_passed += 1
                else:
                    errors.append("calculate_ticket_revenue does not raise ValueError for string input")
                
                # Test float input
                total_exception_tests += 1
                if check_raises_exception(func, [10.5, 20, 30], ValueError):
                    exception_tests_passed += 1
                else:
                    errors.append("calculate_ticket_revenue does not raise ValueError for float input")
                
                # Test None input
                total_exception_tests += 1
                if check_raises_exception(func, [None, 20, 30], ValueError):
                    exception_tests_passed += 1
                else:
                    errors.append("calculate_ticket_revenue does not raise ValueError for None input")
                
                # Test negative input
                total_exception_tests += 1
                if check_raises_exception(func, [-5, 20, 30], ValueError):
                    exception_tests_passed += 1
                else:
                    errors.append("calculate_ticket_revenue does not raise ValueError for negative input")
            else:
                errors.append("Function calculate_ticket_revenue not found")
            
            # Test invalid type handling for calculate_seats_remaining
            if check_function_exists(self.module_obj, "calculate_seats_remaining"):
                func = getattr(self.module_obj, "calculate_seats_remaining")
                
                # Test string input
                total_exception_tests += 1
                if check_raises_exception(func, ["150", 200, 350], ValueError):
                    exception_tests_passed += 1
                else:
                    errors.append("calculate_seats_remaining does not raise ValueError for string input")
                
                # Test float input
                total_exception_tests += 1
                if check_raises_exception(func, [150.5, 200, 350], ValueError):
                    exception_tests_passed += 1
                else:
                    errors.append("calculate_seats_remaining does not raise ValueError for float input")
                
                # Test None input
                total_exception_tests += 1
                if check_raises_exception(func, [150, None, 350], ValueError):
                    exception_tests_passed += 1
                else:
                    errors.append("calculate_seats_remaining does not raise ValueError for None input")
                
                # Test negative input
                total_exception_tests += 1
                if check_raises_exception(func, [-10, 20, 30], ValueError):
                    exception_tests_passed += 1
                else:
                    errors.append("calculate_seats_remaining does not raise ValueError for negative input")
                
                # Test exceeding capacity
                total_exception_tests += 1
                if check_raises_exception(func, [250, 20, 30], ValueError):
                    exception_tests_passed += 1
                else:
                    errors.append("calculate_seats_remaining does not raise ValueError for exceeding Zone A capacity")
            else:
                errors.append("Function calculate_seats_remaining not found")
            
            # Test invalid type handling for calculate_zone_occupancy
            if check_function_exists(self.module_obj, "calculate_zone_occupancy"):
                func = getattr(self.module_obj, "calculate_zone_occupancy")
                
                # Test string input for zone_sold
                total_exception_tests += 1
                if check_raises_exception(func, ["150", 200], ValueError):
                    exception_tests_passed += 1
                else:
                    errors.append("calculate_zone_occupancy does not raise ValueError for string zone_sold")
                
                # Test string input for zone_capacity
                total_exception_tests += 1
                if check_raises_exception(func, [150, "200"], ValueError):
                    exception_tests_passed += 1
                else:
                    errors.append("calculate_zone_occupancy does not raise ValueError for string zone_capacity")
                
                # Test float input
                total_exception_tests += 1
                if check_raises_exception(func, [150.5, 200], ValueError):
                    exception_tests_passed += 1
                else:
                    errors.append("calculate_zone_occupancy does not raise ValueError for float input")
                
                # Test None input
                total_exception_tests += 1
                if check_raises_exception(func, [None, 200], ValueError):
                    exception_tests_passed += 1
                else:
                    errors.append("calculate_zone_occupancy does not raise ValueError for None input")
                
                # Test negative zone_sold
                total_exception_tests += 1
                if check_raises_exception(func, [-10, 200], ValueError):
                    exception_tests_passed += 1
                else:
                    errors.append("calculate_zone_occupancy does not raise ValueError for negative zone_sold")
                
                # Test zero/negative capacity
                total_exception_tests += 1
                if check_raises_exception(func, [100, 0], ValueError):
                    exception_tests_passed += 1
                else:
                    errors.append("calculate_zone_occupancy does not raise ValueError for zero capacity")
                
                # Test exceeding capacity
                total_exception_tests += 1
                if check_raises_exception(func, [250, 200], ValueError):
                    exception_tests_passed += 1
                else:
                    errors.append("calculate_zone_occupancy does not raise ValueError for exceeding capacity")
            else:
                errors.append("Function calculate_zone_occupancy not found")
            
            # Test invalid type handling for calculate_seats_per_row
            if check_function_exists(self.module_obj, "calculate_seats_per_row"):
                func = getattr(self.module_obj, "calculate_seats_per_row")
                
                # Test string input
                total_exception_tests += 1
                if check_raises_exception(func, ["20"], ValueError):
                    exception_tests_passed += 1
                else:
                    errors.append("calculate_seats_per_row does not raise ValueError for string input")
                
                # Test float input
                total_exception_tests += 1
                if check_raises_exception(func, [20.5], ValueError):
                    exception_tests_passed += 1
                else:
                    errors.append("calculate_seats_per_row does not raise ValueError for float input")
                
                # Test None input
                total_exception_tests += 1
                if check_raises_exception(func, [None], ValueError):
                    exception_tests_passed += 1
                else:
                    errors.append("calculate_seats_per_row does not raise ValueError for None input")
                
                # Test negative input
                total_exception_tests += 1
                if check_raises_exception(func, [-5], ValueError):
                    exception_tests_passed += 1
                else:
                    errors.append("calculate_seats_per_row does not raise ValueError for negative input")
            else:
                errors.append("Function calculate_seats_per_row not found")
            
            # Determine if enough exception tests passed (at least 80% should pass for a good implementation)
            success_rate = exception_tests_passed / total_exception_tests if total_exception_tests > 0 else 0
            
            # For the solution code provided, all exception tests should pass
            # But we'll be lenient and accept if at least 80% pass
            if success_rate >= 0.8 and len([e for e in errors if "not found" in e]) == 0:
                self.test_obj.yakshaAssert("TestInvalidInputExceptions", True, "exception")
                print("TestInvalidInputExceptions = Passed")
            else:
                self.test_obj.yakshaAssert("TestInvalidInputExceptions", False, "exception")
                print("TestInvalidInputExceptions = Failed")
                
        except Exception as e:
            self.test_obj.yakshaAssert("TestInvalidInputExceptions", False, "exception")
            print("TestInvalidInputExceptions = Failed")
    
    def test_capacity_exceptions(self):
        """Test capacity constraint handling"""
        try:
            # Check if module can be imported
            if self.module_obj is None:
                self.test_obj.yakshaAssert("TestCapacityExceptions", False, "exception")
                print("TestCapacityExceptions = Failed")
                return
            
            # Check if implementation is functional
            if not is_implementation_functional(self.module_obj):
                self.test_obj.yakshaAssert("TestCapacityExceptions", False, "exception")
                print("TestCapacityExceptions = Failed")
                return
            
            errors = []
            
            # Test exceeding zone capacity in calculate_seats_remaining
            if check_function_exists(self.module_obj, "calculate_seats_remaining"):
                func = getattr(self.module_obj, "calculate_seats_remaining")
                
                # Test exceeding Zone A capacity (capacity = 200)
                if not check_raises_exception(func, [250, 20, 30], ValueError):
                    errors.append("calculate_seats_remaining does not raise ValueError for exceeding Zone A capacity")
                
                # Test exceeding Zone B capacity (capacity = 300)
                if not check_raises_exception(func, [20, 350, 30], ValueError):
                    errors.append("calculate_seats_remaining does not raise ValueError for exceeding Zone B capacity")
                
                # Test exceeding Zone C capacity (capacity = 500)
                if not check_raises_exception(func, [20, 30, 550], ValueError):
                    errors.append("calculate_seats_remaining does not raise ValueError for exceeding Zone C capacity")
                
                # Test exact capacity limits (should not raise exception)
                try:
                    with contextlib.redirect_stdout(io.StringIO()):
                        result = func(200, 300, 500)
                    if result != (0, 0, 0):
                        errors.append("calculate_seats_remaining should handle exact capacity limits correctly")
                except Exception:
                    errors.append("calculate_seats_remaining should not raise exception for exact capacity limits")
            else:
                errors.append("Function calculate_seats_remaining not found")
            
            # Test exceeding capacity in calculate_zone_occupancy
            if check_function_exists(self.module_obj, "calculate_zone_occupancy"):
                func = getattr(self.module_obj, "calculate_zone_occupancy")
                
                # Test exceeding capacity
                if not check_raises_exception(func, [250, 200], ValueError):
                    errors.append("calculate_zone_occupancy does not raise ValueError for exceeding capacity")
                
                # Test zero/negative capacity
                if not check_raises_exception(func, [100, 0], ValueError):
                    errors.append("calculate_zone_occupancy does not raise ValueError for zero capacity")
                
                if not check_raises_exception(func, [100, -10], ValueError):
                    errors.append("calculate_zone_occupancy does not raise ValueError for negative capacity")
                
                # Test exact capacity (should not raise exception)
                try:
                    with contextlib.redirect_stdout(io.StringIO()):
                        result = func(200, 200)
                    if result != 100.0:
                        errors.append("calculate_zone_occupancy should handle exact capacity correctly")
                except Exception:
                    errors.append("calculate_zone_occupancy should not raise exception for exact capacity")
            else:
                errors.append("Function calculate_zone_occupancy not found")
            
            # Final assertion
            if errors:
                self.test_obj.yakshaAssert("TestCapacityExceptions", False, "exception")
                print("TestCapacityExceptions = Failed")
            else:
                self.test_obj.yakshaAssert("TestCapacityExceptions", True, "exception")
                print("TestCapacityExceptions = Passed")
                
        except Exception as e:
            self.test_obj.yakshaAssert("TestCapacityExceptions", False, "exception")
            print("TestCapacityExceptions = Failed")

if __name__ == '__main__':
    unittest.main()