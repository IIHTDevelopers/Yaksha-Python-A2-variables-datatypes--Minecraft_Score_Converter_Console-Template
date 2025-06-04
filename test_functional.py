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

def has_correct_logic_implementation(module_obj):
    """Check if the implementation has correct calculation logic"""
    if not is_implementation_functional(module_obj):
        return False
    
    try:
        # Test calculate_ticket_revenue with known values
        revenue = safely_call_function(module_obj, "calculate_ticket_revenue", 10, 15, 20)
        expected_revenue = 10*5000 + 15*3000 + 20*1500  # 50000 + 45000 + 30000 = 125000
        if revenue != expected_revenue:
            return False
        
        # Test calculate_seats_remaining with known values
        seats = safely_call_function(module_obj, "calculate_seats_remaining", 50, 100, 200)
        expected_seats = (150, 200, 300)  # (200-50, 300-100, 500-200)
        if seats != expected_seats:
            return False
        
        # Test calculate_zone_occupancy with known values
        occupancy = safely_call_function(module_obj, "calculate_zone_occupancy", 75, 200)
        expected_occupancy = 37.5  # (75 * 100) / 200
        if occupancy != expected_occupancy:
            return False
        
        # Test calculate_seats_per_row with known values
        rows = safely_call_function(module_obj, "calculate_seats_per_row", 45)
        expected_rows = (2, 5)  # 45 // 20 = 2, 45 % 20 = 5
        if rows != expected_rows:
            return False
        
        return True
    except Exception:
        return False

class TestMusicFestivalFunctional(unittest.TestCase):
    """Test class for functional testing of the Music Festival Console System."""
    
    def setUp(self):
        """Setup test data before each test method."""
        self.test_obj = TestUtils()
        self.module_obj = load_module_dynamically()
    
    def test_required_variables(self):
        """Test if all required variables are defined with exact naming"""
        try:
            # Check if file exists
            if not check_file_exists('skeleton.py'):
                self.test_obj.yakshaAssert("TestRequiredVariables", False, "functional")
                print("TestRequiredVariables = Failed")
                return
            
            # Check if implementation is functional
            if not is_implementation_functional(self.module_obj):
                self.test_obj.yakshaAssert("TestRequiredVariables", False, "functional")
                print("TestRequiredVariables = Failed")
                return
            
            errors = []
            
            try:
                with open('music_festival_console.py', 'r') as file:
                    content = file.read()
                
                required_vars = {
                    'zone_a_revenue': r'zone_a_revenue\s*=',
                    'zone_b_revenue': r'zone_b_revenue\s*=',
                    'zone_c_revenue': r'zone_c_revenue\s*=',
                    'total_revenue': r'total_revenue\s*=',
                    'zone_a_left': r'zone_a_left\s*=',
                    'zone_b_left': r'zone_b_left\s*=',
                    'zone_c_left': r'zone_c_left\s*=',
                    'complete_rows': r'complete_rows\s*=',
                    'remaining_seats': r'remaining_seats\s*='
                }
                
                # For functional solutions, check if all required variables are used in the main section
                missing_vars = []
                for var_name, pattern in required_vars.items():
                    if not re.search(pattern, content):
                        missing_vars.append(var_name)
                
                # If some variables are missing, check if the functions exist and work correctly
                if missing_vars:
                    # Check if at least the main functions are implemented correctly
                    if not has_correct_logic_implementation(self.module_obj):
                        errors.append(f"Required variables not found and functions don't work correctly: {', '.join(missing_vars)}")
                    # If functions work correctly, we can be more lenient about variable names
                
                # Check if main program structure exists
                if "__name__" not in content or "__main__" not in content:
                    errors.append("Main program structure (__name__ == '__main__') not found")
                
                # Check for input statements
                if "input(" not in content:
                    errors.append("User input functionality not found")
                
                # Check for print statements (output functionality)
                if "print(" not in content:
                    errors.append("Output functionality (print statements) not found")
            
            except Exception as e:
                errors.append(f"Error reading file: {str(e)}")
            
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
    
    def test_calculation_operators(self):
        """Test if correct operators are used in calculations"""
        try:
            # Check if module can be imported
            if self.module_obj is None:
                self.test_obj.yakshaAssert("TestCalculationOperators", False, "functional")
                print("TestCalculationOperators = Failed")
                return
            
            # Check if implementation is functional
            if not is_implementation_functional(self.module_obj):
                self.test_obj.yakshaAssert("TestCalculationOperators", False, "functional")
                print("TestCalculationOperators = Failed")
                return
            
            # Check if implementation has correct logic
            if not has_correct_logic_implementation(self.module_obj):
                self.test_obj.yakshaAssert("TestCalculationOperators", False, "functional")
                print("TestCalculationOperators = Failed")
                return
            
            errors = []
            
            # Check calculate_ticket_revenue function
            if check_function_exists(self.module_obj, "calculate_ticket_revenue"):
                try:
                    revenue_code = inspect.getsource(getattr(self.module_obj, "calculate_ticket_revenue"))
                    if "*" not in revenue_code:
                        errors.append("Multiplication (*) operator not found in calculate_ticket_revenue")
                    if "+" not in revenue_code:
                        errors.append("Addition (+) operator not found in calculate_ticket_revenue")
                    
                    # Check for proper calculation pattern
                    if "5000" not in revenue_code and "ZONE_A_PRICE" not in revenue_code:
                        errors.append("Zone A price (5000) or constant not found in calculate_ticket_revenue")
                    if "3000" not in revenue_code and "ZONE_B_PRICE" not in revenue_code:
                        errors.append("Zone B price (3000) or constant not found in calculate_ticket_revenue")
                    if "1500" not in revenue_code and "ZONE_C_PRICE" not in revenue_code:
                        errors.append("Zone C price (1500) or constant not found in calculate_ticket_revenue")
                except Exception as e:
                    errors.append(f"Error checking calculate_ticket_revenue source: {str(e)}")
            else:
                errors.append("Function calculate_ticket_revenue not found")
            
            # Check calculate_seats_remaining function
            if check_function_exists(self.module_obj, "calculate_seats_remaining"):
                try:
                    seats_code = inspect.getsource(getattr(self.module_obj, "calculate_seats_remaining"))
                    if "-" not in seats_code:
                        errors.append("Subtraction (-) operator not found in calculate_seats_remaining")
                    
                    # Check for proper capacity constants
                    if "200" not in seats_code and "ZONE_A_CAPACITY" not in seats_code:
                        errors.append("Zone A capacity (200) or constant not found in calculate_seats_remaining")
                    if "300" not in seats_code and "ZONE_B_CAPACITY" not in seats_code:
                        errors.append("Zone B capacity (300) or constant not found in calculate_seats_remaining")
                    if "500" not in seats_code and "ZONE_C_CAPACITY" not in seats_code:
                        errors.append("Zone C capacity (500) or constant not found in calculate_seats_remaining")
                except Exception as e:
                    errors.append(f"Error checking calculate_seats_remaining source: {str(e)}")
            else:
                errors.append("Function calculate_seats_remaining not found")
            
            # Check calculate_zone_occupancy function
            if check_function_exists(self.module_obj, "calculate_zone_occupancy"):
                try:
                    occupancy_code = inspect.getsource(getattr(self.module_obj, "calculate_zone_occupancy"))
                    if "*" not in occupancy_code:
                        errors.append("Multiplication (*) operator not found in calculate_zone_occupancy")
                    if "/" not in occupancy_code:
                        errors.append("Division (/) operator not found in calculate_zone_occupancy")
                    
                    # Check for percentage calculation (multiplication by 100)
                    if "100" not in occupancy_code:
                        errors.append("Percentage calculation (100) not found in calculate_zone_occupancy")
                except Exception as e:
                    errors.append(f"Error checking calculate_zone_occupancy source: {str(e)}")
            else:
                errors.append("Function calculate_zone_occupancy not found")
            
            # Check calculate_seats_per_row function
            if check_function_exists(self.module_obj, "calculate_seats_per_row"):
                try:
                    rows_code = inspect.getsource(getattr(self.module_obj, "calculate_seats_per_row"))
                    if "//" not in rows_code:
                        errors.append("Floor division (//) operator not found in calculate_seats_per_row")
                    if "%" not in rows_code:
                        errors.append("Modulus (%) operator not found in calculate_seats_per_row")
                    
                    # Check for seats per row constant
                    if "20" not in rows_code and "SEATS_PER_ROW" not in rows_code:
                        errors.append("Seats per row (20) or constant not found in calculate_seats_per_row")
                except Exception as e:
                    errors.append(f"Error checking calculate_seats_per_row source: {str(e)}")
            else:
                errors.append("Function calculate_seats_per_row not found")
            
            # Final assertion
            if errors:
                self.test_obj.yakshaAssert("TestCalculationOperators", False, "functional")
                print("TestCalculationOperators = Failed")
            else:
                self.test_obj.yakshaAssert("TestCalculationOperators", True, "functional")
                print("TestCalculationOperators = Passed")
                
        except Exception as e:
            self.test_obj.yakshaAssert("TestCalculationOperators", False, "functional")
            print("TestCalculationOperators = Failed")
    
    def test_calculation_logic(self):
        """Test if calculation functions produce correct results"""
        try:
            # Check if module can be imported
            if self.module_obj is None:
                self.test_obj.yakshaAssert("TestCalculationLogic", False, "functional")
                print("TestCalculationLogic = Failed")
                return
            
            # Check if implementation is functional
            if not is_implementation_functional(self.module_obj):
                self.test_obj.yakshaAssert("TestCalculationLogic", False, "functional")
                print("TestCalculationLogic = Failed")
                return
            
            errors = []
            
            # Test revenue calculation with multiple test cases
            if check_function_exists(self.module_obj, "calculate_ticket_revenue"):
                # Test case 1: Basic calculation
                expected_revenue = 10*5000 + 15*3000 + 20*1500  # 50000 + 45000 + 30000 = 125000
                actual_revenue = safely_call_function(self.module_obj, "calculate_ticket_revenue", 10, 15, 20)
                if actual_revenue is None:
                    errors.append("calculate_ticket_revenue returned None")
                elif actual_revenue != expected_revenue:
                    errors.append(f"Revenue calculation failed: Expected {expected_revenue}, got {actual_revenue}")
                
                # Test case 2: Zero tickets
                zero_revenue = safely_call_function(self.module_obj, "calculate_ticket_revenue", 0, 0, 0)
                if zero_revenue is None:
                    errors.append("calculate_ticket_revenue returned None for zero tickets")
                elif zero_revenue != 0:
                    errors.append(f"Zero tickets revenue should be 0, got {zero_revenue}")
                
                # Test case 3: Maximum capacity
                max_revenue = safely_call_function(self.module_obj, "calculate_ticket_revenue", 200, 300, 500)
                expected_max = 200*5000 + 300*3000 + 500*1500  # 1000000 + 900000 + 750000 = 2650000
                if max_revenue is None:
                    errors.append("calculate_ticket_revenue returned None for max capacity")
                elif max_revenue != expected_max:
                    errors.append(f"Max capacity revenue failed: Expected {expected_max}, got {max_revenue}")
                
                # Test case 4: Single zone
                single_revenue = safely_call_function(self.module_obj, "calculate_ticket_revenue", 100, 0, 0)
                expected_single = 100 * 5000
                if single_revenue is None:
                    errors.append("calculate_ticket_revenue returned None for single zone")
                elif single_revenue != expected_single:
                    errors.append(f"Single zone revenue failed: Expected {expected_single}, got {single_revenue}")
            else:
                errors.append("Function calculate_ticket_revenue not found")
            
            # Test seats remaining calculation with multiple test cases
            if check_function_exists(self.module_obj, "calculate_seats_remaining"):
                # Test case 1: Basic calculation
                expected_seats = (150, 200, 300)  # (200-50, 300-100, 500-200)
                actual_seats = safely_call_function(self.module_obj, "calculate_seats_remaining", 50, 100, 200)
                if actual_seats is None:
                    errors.append("calculate_seats_remaining returned None")
                elif actual_seats != expected_seats:
                    errors.append(f"Seats remaining calculation failed: Expected {expected_seats}, got {actual_seats}")
                
                # Test case 2: Empty venue
                empty_seats = safely_call_function(self.module_obj, "calculate_seats_remaining", 0, 0, 0)
                expected_empty = (200, 300, 500)
                if empty_seats is None:
                    errors.append("calculate_seats_remaining returned None for empty venue")
                elif empty_seats != expected_empty:
                    errors.append(f"Empty venue seats failed: Expected {expected_empty}, got {empty_seats}")
                
                # Test case 3: Full venue
                full_seats = safely_call_function(self.module_obj, "calculate_seats_remaining", 200, 300, 500)
                expected_full = (0, 0, 0)
                if full_seats is None:
                    errors.append("calculate_seats_remaining returned None for full venue")
                elif full_seats != expected_full:
                    errors.append(f"Full venue seats failed: Expected {expected_full}, got {full_seats}")
                
                # Test case 4: Partial occupancy
                partial_seats = safely_call_function(self.module_obj, "calculate_seats_remaining", 150, 200, 350)
                expected_partial = (50, 100, 150)
                if partial_seats is None:
                    errors.append("calculate_seats_remaining returned None for partial occupancy")
                elif partial_seats != expected_partial:
                    errors.append(f"Partial occupancy seats failed: Expected {expected_partial}, got {partial_seats}")
            else:
                errors.append("Function calculate_seats_remaining not found")
            
            # Test occupancy calculation with multiple test cases
            if check_function_exists(self.module_obj, "calculate_zone_occupancy"):
                # Test case 1: Basic calculation (37.5%)
                expected_occupancy = 37.5
                actual_occupancy = safely_call_function(self.module_obj, "calculate_zone_occupancy", 75, 200)
                if actual_occupancy is None:
                    errors.append("calculate_zone_occupancy returned None")
                elif actual_occupancy != expected_occupancy:
                    errors.append(f"Occupancy calculation failed: Expected {expected_occupancy}, got {actual_occupancy}")
                
                # Test case 2: Empty zone (0%)
                empty_occupancy = safely_call_function(self.module_obj, "calculate_zone_occupancy", 0, 200)
                if empty_occupancy is None:
                    errors.append("calculate_zone_occupancy returned None for empty zone")
                elif empty_occupancy != 0.0:
                    errors.append(f"Empty zone occupancy should be 0.0, got {empty_occupancy}")
                
                # Test case 3: Full zone (100%)
                full_occupancy = safely_call_function(self.module_obj, "calculate_zone_occupancy", 200, 200)
                if full_occupancy is None:
                    errors.append("calculate_zone_occupancy returned None for full zone")
                elif full_occupancy != 100.0:
                    errors.append(f"Full zone occupancy should be 100.0, got {full_occupancy}")
                
                # Test case 4: Half capacity (50%)
                half_occupancy = safely_call_function(self.module_obj, "calculate_zone_occupancy", 150, 300)
                if half_occupancy is None:
                    errors.append("calculate_zone_occupancy returned None for half capacity")
                elif half_occupancy != 50.0:
                    errors.append(f"Half capacity occupancy should be 50.0, got {half_occupancy}")
                
                # Test case 5: Different zone capacities
                zone_a_occupancy = safely_call_function(self.module_obj, "calculate_zone_occupancy", 150, 200)
                if zone_a_occupancy is None:
                    errors.append("calculate_zone_occupancy returned None for Zone A test")
                elif zone_a_occupancy != 75.0:
                    errors.append(f"Zone A occupancy should be 75.0, got {zone_a_occupancy}")
            else:
                errors.append("Function calculate_zone_occupancy not found")
            
            # Test seats per row calculation with multiple test cases
            if check_function_exists(self.module_obj, "calculate_seats_per_row"):
                # Test case 1: Basic calculation (2 rows, 5 extra)
                expected_rows = (2, 5)
                actual_rows = safely_call_function(self.module_obj, "calculate_seats_per_row", 45)
                if actual_rows is None:
                    errors.append("calculate_seats_per_row returned None")
                elif actual_rows != expected_rows:
                    errors.append(f"Seats per row calculation failed: Expected {expected_rows}, got {actual_rows}")
                
                # Test case 2: Exact rows (no remainder)
                exact_rows = safely_call_function(self.module_obj, "calculate_seats_per_row", 40)
                expected_exact = (2, 0)
                if exact_rows is None:
                    errors.append("calculate_seats_per_row returned None for exact rows")
                elif exact_rows != expected_exact:
                    errors.append(f"Exact rows calculation failed: Expected {expected_exact}, got {exact_rows}")
                
                # Test case 3: Single row
                single_row = safely_call_function(self.module_obj, "calculate_seats_per_row", 20)
                expected_single = (1, 0)
                if single_row is None:
                    errors.append("calculate_seats_per_row returned None for single row")
                elif single_row != expected_single:
                    errors.append(f"Single row calculation failed: Expected {expected_single}, got {single_row}")
                
                # Test case 4: Less than one row
                partial_row = safely_call_function(self.module_obj, "calculate_seats_per_row", 15)
                expected_partial = (0, 15)
                if partial_row is None:
                    errors.append("calculate_seats_per_row returned None for partial row")
                elif partial_row != expected_partial:
                    errors.append(f"Partial row calculation failed: Expected {expected_partial}, got {partial_row}")
                
                # Test case 5: Zero seats
                zero_rows = safely_call_function(self.module_obj, "calculate_seats_per_row", 0)
                expected_zero = (0, 0)
                if zero_rows is None:
                    errors.append("calculate_seats_per_row returned None for zero seats")
                elif zero_rows != expected_zero:
                    errors.append(f"Zero seats calculation failed: Expected {expected_zero}, got {zero_rows}")
                
                # Test case 6: Large numbers
                large_rows = safely_call_function(self.module_obj, "calculate_seats_per_row", 150)
                expected_large = (7, 10)  # 150 // 20 = 7, 150 % 20 = 10
                if large_rows is None:
                    errors.append("calculate_seats_per_row returned None for large numbers")
                elif large_rows != expected_large:
                    errors.append(f"Large numbers calculation failed: Expected {expected_large}, got {large_rows}")
            else:
                errors.append("Function calculate_seats_per_row not found")
            
            # Final assertion
            if errors:
                self.test_obj.yakshaAssert("TestCalculationLogic", False, "functional")
                print("TestCalculationLogic = Failed")
            else:
                self.test_obj.yakshaAssert("TestCalculationLogic", True, "functional")
                print("TestCalculationLogic = Passed")
                
        except Exception as e:
            self.test_obj.yakshaAssert("TestCalculationLogic", False, "functional")
            print("TestCalculationLogic = Failed")

if __name__ == '__main__':
    unittest.main()