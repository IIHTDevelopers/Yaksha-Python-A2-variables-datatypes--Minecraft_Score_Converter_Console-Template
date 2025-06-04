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

def load_module_dynamically():
    """Load the student's module for testing"""
    module_obj = safely_import_module("skeleton")
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

class TestMusicFestivalBoundary(unittest.TestCase):
    """Test class for boundary value testing of the Music Festival Console System."""
    
    def setUp(self):
        """Setup test data before each test method."""
        self.test_obj = TestUtils()
        self.module_obj = load_module_dynamically()
    
    def test_revenue_and_seats_boundary(self):
        """Test revenue and remaining seats with boundary values"""
        try:
            # Check if module can be imported
            if self.module_obj is None:
                self.test_obj.yakshaAssert("TestRevenueAndSeatsBoundary", False, "boundary")
                print("TestRevenueAndSeatsBoundary = Failed")
                return
            
            # Check if implementation is functional
            if not is_implementation_functional(self.module_obj):
                self.test_obj.yakshaAssert("TestRevenueAndSeatsBoundary", False, "boundary")
                print("TestRevenueAndSeatsBoundary = Failed")
                return
            
            errors = []
            
            # Test revenue calculations with boundary values
            if check_function_exists(self.module_obj, "calculate_ticket_revenue"):
                # Empty venue test
                revenue_empty = safely_call_function(self.module_obj, "calculate_ticket_revenue", 0, 0, 0)
                if revenue_empty is None:
                    errors.append("calculate_ticket_revenue returned None for empty venue")
                elif revenue_empty != 0:
                    errors.append(f"Empty venue revenue should be 0, got {revenue_empty}")
                
                # Full venue test - Based on SRS: Zone A=200*5000, Zone B=300*3000, Zone C=500*1500
                expected_full_revenue = 200*5000 + 300*3000 + 500*1500
                revenue_full = safely_call_function(self.module_obj, "calculate_ticket_revenue", 200, 300, 500)
                if revenue_full is None:
                    errors.append("calculate_ticket_revenue returned None for full venue")
                elif revenue_full != expected_full_revenue:
                    errors.append(f"Full venue revenue should be {expected_full_revenue}, got {revenue_full}")
                
                # Boundary test with maximum capacity per zone
                revenue_max_a = safely_call_function(self.module_obj, "calculate_ticket_revenue", 200, 0, 0)
                if revenue_max_a is None:
                    errors.append("calculate_ticket_revenue failed for max Zone A capacity")
                elif revenue_max_a != 200 * 5000:
                    errors.append(f"Zone A max revenue should be {200 * 5000}, got {revenue_max_a}")
                
                revenue_max_b = safely_call_function(self.module_obj, "calculate_ticket_revenue", 0, 300, 0)
                if revenue_max_b is None:
                    errors.append("calculate_ticket_revenue failed for max Zone B capacity")
                elif revenue_max_b != 300 * 3000:
                    errors.append(f"Zone B max revenue should be {300 * 3000}, got {revenue_max_b}")
                
                revenue_max_c = safely_call_function(self.module_obj, "calculate_ticket_revenue", 0, 0, 500)
                if revenue_max_c is None:
                    errors.append("calculate_ticket_revenue failed for max Zone C capacity")
                elif revenue_max_c != 500 * 1500:
                    errors.append(f"Zone C max revenue should be {500 * 1500}, got {revenue_max_c}")
                
                # Test with minimum non-zero values
                revenue_min = safely_call_function(self.module_obj, "calculate_ticket_revenue", 1, 1, 1)
                expected_min_revenue = 1*5000 + 1*3000 + 1*1500
                if revenue_min is None:
                    errors.append("calculate_ticket_revenue failed for minimum values")
                elif revenue_min != expected_min_revenue:
                    errors.append(f"Minimum revenue should be {expected_min_revenue}, got {revenue_min}")
            else:
                errors.append("Function calculate_ticket_revenue not found")
            
            # Test seats remaining calculations
            if check_function_exists(self.module_obj, "calculate_seats_remaining"):
                # Empty venue test - should return full capacity
                seats_empty = safely_call_function(self.module_obj, "calculate_seats_remaining", 0, 0, 0)
                if seats_empty is None:
                    errors.append("calculate_seats_remaining returned None for empty venue")
                elif seats_empty != (200, 300, 500):
                    errors.append(f"Empty venue seats remaining should be (200, 300, 500), got {seats_empty}")
                
                # Full venue test - should return (0, 0, 0)
                seats_full = safely_call_function(self.module_obj, "calculate_seats_remaining", 200, 300, 500)
                if seats_full is None:
                    errors.append("calculate_seats_remaining returned None for full venue")
                elif seats_full != (0, 0, 0):
                    errors.append(f"Full venue seats remaining should be (0, 0, 0), got {seats_full}")
                
                # Partial occupancy test
                seats_partial = safely_call_function(self.module_obj, "calculate_seats_remaining", 150, 200, 350)
                if seats_partial is None:
                    errors.append("calculate_seats_remaining returned None for partial occupancy")
                elif seats_partial != (50, 100, 150):
                    errors.append(f"Partial occupancy seats remaining should be (50, 100, 150), got {seats_partial}")
                
                # Single seat boundary test
                seats_single = safely_call_function(self.module_obj, "calculate_seats_remaining", 1, 1, 1)
                if seats_single is None:
                    errors.append("calculate_seats_remaining returned None for single seat test")
                elif seats_single != (199, 299, 499):
                    errors.append(f"Single seat test should be (199, 299, 499), got {seats_single}")
                
                # Test boundary - one seat before full capacity
                seats_almost_full = safely_call_function(self.module_obj, "calculate_seats_remaining", 199, 299, 499)
                if seats_almost_full is None:
                    errors.append("calculate_seats_remaining returned None for almost full test")
                elif seats_almost_full != (1, 1, 1):
                    errors.append(f"Almost full test should be (1, 1, 1), got {seats_almost_full}")
            else:
                errors.append("Function calculate_seats_remaining not found")
            
            # Final assertion
            if errors:
                self.test_obj.yakshaAssert("TestRevenueAndSeatsBoundary", False, "boundary")
                print("TestRevenueAndSeatsBoundary = Failed")
            else:
                self.test_obj.yakshaAssert("TestRevenueAndSeatsBoundary", True, "boundary")
                print("TestRevenueAndSeatsBoundary = Passed")
                
        except Exception as e:
            self.test_obj.yakshaAssert("TestRevenueAndSeatsBoundary", False, "boundary")
            print("TestRevenueAndSeatsBoundary = Failed")
    
    def test_occupancy_and_rows_boundary(self):
        """Test occupancy and row calculations with boundary values"""
        try:
            # Check if module can be imported
            if self.module_obj is None:
                self.test_obj.yakshaAssert("TestOccupancyAndRowsBoundary", False, "boundary")
                print("TestOccupancyAndRowsBoundary = Failed")
                return
            
            # Check if implementation is functional
            if not is_implementation_functional(self.module_obj):
                self.test_obj.yakshaAssert("TestOccupancyAndRowsBoundary", False, "boundary")
                print("TestOccupancyAndRowsBoundary = Failed")
                return
            
            errors = []
            
            # Test occupancy calculations
            if check_function_exists(self.module_obj, "calculate_zone_occupancy"):
                # Empty zone test (0% occupancy)
                occupancy_empty = safely_call_function(self.module_obj, "calculate_zone_occupancy", 0, 200)
                if occupancy_empty is None:
                    errors.append("calculate_zone_occupancy returned None for empty zone")
                elif occupancy_empty != 0.0:
                    errors.append(f"Empty zone occupancy should be 0.0, got {occupancy_empty}")
                
                # Full zone test (100% occupancy)
                occupancy_full = safely_call_function(self.module_obj, "calculate_zone_occupancy", 200, 200)
                if occupancy_full is None:
                    errors.append("calculate_zone_occupancy returned None for full zone")
                elif occupancy_full != 100.0:
                    errors.append(f"Full zone occupancy should be 100.0, got {occupancy_full}")
                
                # 50% occupancy test
                occupancy_half = safely_call_function(self.module_obj, "calculate_zone_occupancy", 100, 200)
                if occupancy_half is None:
                    errors.append("calculate_zone_occupancy returned None for half zone")
                elif occupancy_half != 50.0:
                    errors.append(f"Half zone occupancy should be 50.0, got {occupancy_half}")
                
                # Zone A specific test (75% occupancy: 150/200)
                occupancy_zone_a = safely_call_function(self.module_obj, "calculate_zone_occupancy", 150, 200)
                if occupancy_zone_a is None:
                    errors.append("calculate_zone_occupancy returned None for Zone A test")
                elif occupancy_zone_a != 75.0:
                    errors.append(f"Zone A occupancy should be 75.0, got {occupancy_zone_a}")
                
                # Zone B specific test (66.67% occupancy: 200/300)
                occupancy_zone_b = safely_call_function(self.module_obj, "calculate_zone_occupancy", 200, 300)
                if occupancy_zone_b is None:
                    errors.append("calculate_zone_occupancy returned None for Zone B test")
                elif abs(occupancy_zone_b - 66.66666666666667) > 0.01:
                    errors.append(f"Zone B occupancy should be ~66.67, got {occupancy_zone_b}")
                
                # Zone C specific test (70% occupancy: 350/500)
                occupancy_zone_c = safely_call_function(self.module_obj, "calculate_zone_occupancy", 350, 500)
                if occupancy_zone_c is None:
                    errors.append("calculate_zone_occupancy returned None for Zone C test")
                elif occupancy_zone_c != 70.0:
                    errors.append(f"Zone C occupancy should be 70.0, got {occupancy_zone_c}")
                
                # Boundary: 1 seat in capacity
                occupancy_one = safely_call_function(self.module_obj, "calculate_zone_occupancy", 1, 200)
                if occupancy_one is None:
                    errors.append("calculate_zone_occupancy returned None for single seat")
                elif occupancy_one != 0.5:
                    errors.append(f"Single seat occupancy should be 0.5, got {occupancy_one}")
                
                # Boundary: capacity - 1
                occupancy_almost_full = safely_call_function(self.module_obj, "calculate_zone_occupancy", 199, 200)
                if occupancy_almost_full is None:
                    errors.append("calculate_zone_occupancy returned None for almost full")
                elif occupancy_almost_full != 99.5:
                    errors.append(f"Almost full occupancy should be 99.5, got {occupancy_almost_full}")
            else:
                errors.append("Function calculate_zone_occupancy not found")
            
            # Test row calculations (SEATS_PER_ROW = 20 based on SRS)
            if check_function_exists(self.module_obj, "calculate_seats_per_row"):
                # Empty rows test (0 seats)
                rows_empty = safely_call_function(self.module_obj, "calculate_seats_per_row", 0)
                if rows_empty is None:
                    errors.append("calculate_seats_per_row returned None for 0 seats")
                elif rows_empty != (0, 0):
                    errors.append(f"0 seats should give (0, 0) rows, got {rows_empty}")
                
                # Exact one row test (20 seats)
                rows_exact = safely_call_function(self.module_obj, "calculate_seats_per_row", 20)
                if rows_exact is None:
                    errors.append("calculate_seats_per_row returned None for 20 seats")
                elif rows_exact != (1, 0):
                    errors.append(f"20 seats should give (1, 0) rows, got {rows_exact}")
                
                # Partial row test (25 seats = 1 complete row + 5 extra)
                rows_partial = safely_call_function(self.module_obj, "calculate_seats_per_row", 25)
                if rows_partial is None:
                    errors.append("calculate_seats_per_row returned None for 25 seats")
                elif rows_partial != (1, 5):
                    errors.append(f"25 seats should give (1, 5) rows, got {rows_partial}")
                
                # Multiple complete rows test (40 seats = 2 complete rows + 0 extra)
                rows_multiple = safely_call_function(self.module_obj, "calculate_seats_per_row", 40)
                if rows_multiple is None:
                    errors.append("calculate_seats_per_row returned None for 40 seats")
                elif rows_multiple != (2, 0):
                    errors.append(f"40 seats should give (2, 0) rows, got {rows_multiple}")
                
                # Large number test (150 seats = 7 complete rows + 10 extra)
                rows_large = safely_call_function(self.module_obj, "calculate_seats_per_row", 150)
                if rows_large is None:
                    errors.append("calculate_seats_per_row returned None for 150 seats")
                elif rows_large != (7, 10):
                    errors.append(f"150 seats should give (7, 10) rows, got {rows_large}")
                
                # Maximum zone capacity tests
                # Zone A: 200 seats = 10 complete rows + 0 extra
                rows_zone_a_max = safely_call_function(self.module_obj, "calculate_seats_per_row", 200)
                if rows_zone_a_max is None:
                    errors.append("calculate_seats_per_row returned None for Zone A max")
                elif rows_zone_a_max != (10, 0):
                    errors.append(f"200 seats should give (10, 0) rows, got {rows_zone_a_max}")
                
                # Zone B: 300 seats = 15 complete rows + 0 extra
                rows_zone_b_max = safely_call_function(self.module_obj, "calculate_seats_per_row", 300)
                if rows_zone_b_max is None:
                    errors.append("calculate_seats_per_row returned None for Zone B max")
                elif rows_zone_b_max != (15, 0):
                    errors.append(f"300 seats should give (15, 0) rows, got {rows_zone_b_max}")
                
                # Zone C: 500 seats = 25 complete rows + 0 extra
                rows_zone_c_max = safely_call_function(self.module_obj, "calculate_seats_per_row", 500)
                if rows_zone_c_max is None:
                    errors.append("calculate_seats_per_row returned None for Zone C max")
                elif rows_zone_c_max != (25, 0):
                    errors.append(f"500 seats should give (25, 0) rows, got {rows_zone_c_max}")
                
                # Boundary: Just below a complete row (19 seats = 0 complete + 19 extra)
                rows_just_below = safely_call_function(self.module_obj, "calculate_seats_per_row", 19)
                if rows_just_below is None:
                    errors.append("calculate_seats_per_row returned None for 19 seats")
                elif rows_just_below != (0, 19):
                    errors.append(f"19 seats should give (0, 19) rows, got {rows_just_below}")
                
                # Boundary: Just above a complete row (21 seats = 1 complete + 1 extra)
                rows_just_above = safely_call_function(self.module_obj, "calculate_seats_per_row", 21)
                if rows_just_above is None:
                    errors.append("calculate_seats_per_row returned None for 21 seats")
                elif rows_just_above != (1, 1):
                    errors.append(f"21 seats should give (1, 1) rows, got {rows_just_above}")
                
                # Single seat test
                rows_single = safely_call_function(self.module_obj, "calculate_seats_per_row", 1)
                if rows_single is None:
                    errors.append("calculate_seats_per_row returned None for 1 seat")
                elif rows_single != (0, 1):
                    errors.append(f"1 seat should give (0, 1) rows, got {rows_single}")
            else:
                errors.append("Function calculate_seats_per_row not found")
            
            # Final assertion
            if errors:
                self.test_obj.yakshaAssert("TestOccupancyAndRowsBoundary", False, "boundary")
                print("TestOccupancyAndRowsBoundary = Failed")
            else:
                self.test_obj.yakshaAssert("TestOccupancyAndRowsBoundary", True, "boundary")
                print("TestOccupancyAndRowsBoundary = Passed")
                
        except Exception as e:
            self.test_obj.yakshaAssert("TestOccupancyAndRowsBoundary", False, "boundary")
            print("TestOccupancyAndRowsBoundary = Failed")

if __name__ == '__main__':
    unittest.main()