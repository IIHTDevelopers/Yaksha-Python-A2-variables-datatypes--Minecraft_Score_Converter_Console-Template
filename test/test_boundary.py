import unittest
import os
import importlib
import sys
import io
import contextlib
from decimal import Decimal, InvalidOperation
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

def check_class_exists(module, class_name):
    """Check if a class exists in a module."""
    return hasattr(module, class_name) and isinstance(getattr(module, class_name), type)

def safely_call_function(module, function_name, *args, **kwargs):
    """Safely call a function, returning None if it fails."""
    if not check_function_exists(module, function_name):
        return None
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            return getattr(module, function_name)(*args, **kwargs)
    except Exception:
        return None

def safely_create_instance(module, class_name, *args, **kwargs):
    """Safely create an instance of a class, returning None if it fails."""
    if not check_class_exists(module, class_name):
        return None
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            cls = getattr(module, class_name)
            return cls(*args, **kwargs)
    except Exception:
        return None

def safely_get_attribute(obj, attr_name):
    """Safely get an attribute from an object, returning None if it fails."""
    if obj is None:
        return None
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            return getattr(obj, attr_name)
    except Exception:
        return None

def safely_set_attribute(obj, attr_name, value):
    """Safely set an attribute on an object, returning False if it fails."""
    if obj is None:
        return False
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            setattr(obj, attr_name, value)
            return True
    except Exception:
        return False

def safely_call_method(obj, method_name, *args, **kwargs):
    """Safely call a method on an object, returning None if it fails."""
    if obj is None:
        return None
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            if hasattr(obj, method_name):
                method = getattr(obj, method_name)
                if callable(method):
                    return method(*args, **kwargs)
    except Exception:
        return None
    return None

def check_raises(func, args, expected_exception=Exception):
    """Check if a function raises an expected exception."""
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            func(*args)
        return False
    except expected_exception:
        return True
    except Exception:
        return False

def load_module_dynamically():
    """Load the student's module for testing"""
    module_obj = safely_import_module("banking_system_error_handling_framework")
    if module_obj is None:
        module_obj = safely_import_module("solution")
    return module_obj

class TestBankingSystemBoundaries(unittest.TestCase):
    def setUp(self):
        """Standard setup for all test methods"""
        self.test_obj = TestUtils()
        self.module_obj = load_module_dynamically()
    
    def test_banking_system_boundaries(self):
        """Test all boundary conditions and edge cases for the banking system"""
        try:
            # Check if module can be imported
            if self.module_obj is None:
                self.test_obj.yakshaAssert("TestBankingSystemBoundaries", False, "boundary")
                print("TestBankingSystemBoundaries = Failed")
                return
            
            errors = []
            
            # Test InputValidator class and methods
            if not check_class_exists(self.module_obj, "InputValidator"):
                errors.append("InputValidator class not found")
            else:
                # Test validate_amount method with valid amounts
                if check_function_exists(self.module_obj.InputValidator, "validate_amount"):
                    # Valid decimal string
                    result = safely_call_function(self.module_obj.InputValidator, "validate_amount", "100")
                    if result is None:
                        errors.append("validate_amount failed with valid string input")
                    elif str(result) != "100":
                        errors.append(f"validate_amount returned {result}, expected 100")
                    
                    # Valid minimal amount
                    result = safely_call_function(self.module_obj.InputValidator, "validate_amount", "0.01")
                    if result is None:
                        errors.append("validate_amount failed with minimal valid amount")
                    elif str(result) != "0.01":
                        errors.append(f"validate_amount returned {result}, expected 0.01")
                    
                    # Valid decimal object
                    if check_class_exists(self.module_obj, "Decimal") or "Decimal" in dir(self.module_obj):
                        decimal_input = Decimal("100.50")
                        result = safely_call_function(self.module_obj.InputValidator, "validate_amount", decimal_input)
                        if result is None:
                            errors.append("validate_amount failed with Decimal input")
                        elif str(result) != "100.50":
                            errors.append(f"validate_amount returned {result}, expected 100.50")
                    
                    # Test invalid amounts - zero (might be allowed for initial balance)
                    zero_result = safely_call_function(self.module_obj.InputValidator, "validate_amount", "0")
                    zero_raises = check_raises(self.module_obj.InputValidator.validate_amount, ["0"], Exception)
                    # Accept either behavior - some implementations allow 0 for initial balance
                    
                    # Test invalid amounts - negative
                    negative_raises = check_raises(self.module_obj.InputValidator.validate_amount, ["-10"], Exception)
                    if not negative_raises:
                        result = safely_call_function(self.module_obj.InputValidator, "validate_amount", "-10")
                        if result is not None:
                            errors.append("validate_amount should reject negative amount")
                    
                    # Test invalid amounts - non-numeric
                    non_numeric_raises = check_raises(self.module_obj.InputValidator.validate_amount, ["abc"], Exception)
                    if not non_numeric_raises:
                        result = safely_call_function(self.module_obj.InputValidator, "validate_amount", "abc")
                        if result is not None:
                            errors.append("validate_amount should reject non-numeric input")
                    
                    # Test with very small amounts (precision testing)
                    small_amounts = ["0.001", "0.0001", "0.00001"]
                    for amount in small_amounts:
                        result = safely_call_function(self.module_obj.InputValidator, "validate_amount", amount)
                        if result is None:
                            errors.append(f"Failed to validate very small amount: {amount}")
                    
                    # Test with special string formats
                    special_formats = ["1.0", "1.", ".5", "1e2", "1E2"]
                    for amount in special_formats:
                        result = safely_call_function(self.module_obj.InputValidator, "validate_amount", amount)
                        # Don't require these to work, just ensure they don't crash
                else:
                    errors.append("InputValidator.validate_amount method not found")
                
                # Test validate_account_id method
                if check_function_exists(self.module_obj.InputValidator, "validate_account_id"):
                    # Valid IDs within 8-12 character limit
                    test_ids = ["ACCT123456", "12345678", "ABCDEFGHIJ", "123456789012"]
                    for test_id in test_ids:
                        if len(test_id) <= 12:
                            result = safely_call_function(self.module_obj.InputValidator, "validate_account_id", test_id)
                            if result is None:
                                errors.append(f"validate_account_id failed with valid ID: {test_id}")
                            elif result != test_id:
                                errors.append(f"validate_account_id returned {result}, expected {test_id}")
                    
                    # Invalid IDs - too short
                    short_raises = check_raises(self.module_obj.InputValidator.validate_account_id, ["ACCT"], Exception)
                    if not short_raises:
                        result = safely_call_function(self.module_obj.InputValidator, "validate_account_id", "ACCT")
                        if result is not None:
                            errors.append("validate_account_id should reject too short ID")
                    
                    # Invalid IDs - too long
                    long_raises = check_raises(self.module_obj.InputValidator.validate_account_id, ["ACCT123456789"], Exception)
                    if not long_raises:
                        result = safely_call_function(self.module_obj.InputValidator, "validate_account_id", "ACCT123456789")
                        if result is not None:
                            errors.append("validate_account_id should reject too long ID")
                    
                    # Invalid IDs - non-alphanumeric
                    special_raises = check_raises(self.module_obj.InputValidator.validate_account_id, ["ACCT-123!"], Exception)
                    if not special_raises:
                        result = safely_call_function(self.module_obj.InputValidator, "validate_account_id", "ACCT-123!")
                        if result is not None:
                            errors.append("validate_account_id should reject non-alphanumeric ID")
                    
                    # Test boundary ID lengths
                    min_length_id = "12345678"  # 8 characters
                    max_length_id = "123456789012"  # 12 characters
                    
                    min_result = safely_call_function(self.module_obj.InputValidator, "validate_account_id", min_length_id)
                    if min_result is None:
                        errors.append("Should accept minimum length account ID")
                    
                    max_result = safely_call_function(self.module_obj.InputValidator, "validate_account_id", max_length_id)
                    if max_result is None:
                        errors.append("Should accept maximum length account ID")
                else:
                    errors.append("InputValidator.validate_account_id method not found")
            
            # Test BankAccount class
            if not check_class_exists(self.module_obj, "BankAccount"):
                errors.append("BankAccount class not found")
            else:
                # Valid account creation
                account1 = safely_create_instance(self.module_obj, "BankAccount", "ACCT123456", "John Doe", 1000)
                if account1 is None:
                    errors.append("Failed to create BankAccount with valid parameters")
                else:
                    # Test basic property access
                    if safely_get_attribute(account1, "account_id") != "ACCT123456":
                        errors.append("BankAccount account_id property incorrect")
                    if safely_get_attribute(account1, "owner_name") != "John Doe":
                        errors.append("BankAccount owner_name property incorrect")
                    
                    balance = safely_get_attribute(account1, "balance")
                    if balance is None:
                        errors.append("BankAccount balance property not accessible")
                    elif str(balance) != "1000":
                        errors.append(f"BankAccount balance incorrect: {balance}, expected 1000")
                
                # Invalid account creation - invalid ID
                invalid_id_account = safely_create_instance(self.module_obj, "BankAccount", "A", "John Doe", 1000)
                if invalid_id_account is not None:
                    errors.append("BankAccount should not be created with invalid ID")
                
                # Invalid account creation - empty name
                empty_name_account = safely_create_instance(self.module_obj, "BankAccount", "ACCT123456", "", 1000)
                if empty_name_account is not None:
                    errors.append("BankAccount should not be created with empty name")
                
                # Test account creation with zero balance (might be allowed)
                zero_balance_account = safely_create_instance(self.module_obj, "BankAccount", "ACCT123456", "John Doe", 0)
                # Don't fail the test if zero balance is allowed
                
                # Invalid account creation - negative balance
                negative_balance_account = safely_create_instance(self.module_obj, "BankAccount", "ACCT123456", "John Doe", -100)
                if negative_balance_account is not None:
                    errors.append("BankAccount should not be created with negative balance")
                
                # Test with very long names
                long_name = "A" * 1000
                long_name_account = safely_create_instance(self.module_obj, "BankAccount", "ACCT888888", long_name, 1000)
                if long_name_account is not None:
                    retrieved_name = safely_get_attribute(long_name_account, "owner_name")
                    if retrieved_name != long_name:
                        errors.append("Account should handle very long owner names")
                
                # Test with special characters in names
                special_names = ["José María", "O'Connor", "Smith-Jones", "李小明"]
                for name in special_names:
                    account_id = f"ACCT{hash(name) % 100000:05d}"[:12]
                    special_account = safely_create_instance(self.module_obj, "BankAccount", account_id, name, 1000)
                    if special_account is not None:
                        retrieved_name = safely_get_attribute(special_account, "owner_name")
                        if retrieved_name != name:
                            errors.append(f"Account should handle special characters in name: {name}")
            
            # Test deposit and withdrawal operations
            account2 = safely_create_instance(self.module_obj, "BankAccount", "ACCT654321", "Jane Doe", 500)
            if account2 is not None:
                # Valid deposits
                deposit_result = safely_call_method(account2, "deposit", "100")
                if deposit_result is None:
                    errors.append("deposit method failed with valid amount")
                else:
                    current_balance = safely_get_attribute(account2, "balance")
                    if current_balance is None or str(current_balance) != "600":
                        errors.append(f"Balance after deposit incorrect: {current_balance}, expected 600")
                
                # Test minimal valid deposit
                deposit_min_result = safely_call_method(account2, "deposit", 0.01)
                if deposit_min_result is None:
                    errors.append("deposit method failed with minimal valid amount")
                
                # Invalid deposit - zero
                zero_deposit_raises = check_raises(lambda: account2.deposit(0), [], Exception)
                if not zero_deposit_raises:
                    deposit_result = safely_call_method(account2, "deposit", 0)
                    if deposit_result is not None:
                        errors.append("deposit should reject zero amount")
                
                # Invalid deposit - negative
                negative_deposit_raises = check_raises(lambda: account2.deposit(-50), [], Exception)
                if not negative_deposit_raises:
                    deposit_result = safely_call_method(account2, "deposit", -50)
                    if deposit_result is not None:
                        errors.append("deposit should reject negative amount")
                
                # Invalid deposit - non-numeric
                non_numeric_deposit_raises = check_raises(lambda: account2.deposit("abc"), [], Exception)
                if not non_numeric_deposit_raises:
                    deposit_result = safely_call_method(account2, "deposit", "abc")
                    if deposit_result is not None:
                        errors.append("deposit should reject non-numeric input")
                
                # Valid withdrawals
                withdraw_result = safely_call_method(account2, "withdraw", "0.01")
                if withdraw_result is None:
                    errors.append("withdraw method failed with minimal valid amount")
                
                withdraw_result2 = safely_call_method(account2, "withdraw", 100)
                if withdraw_result2 is None:
                    errors.append("withdraw method failed with valid amount")
                
                # Invalid withdrawal - zero
                zero_withdraw_raises = check_raises(lambda: account2.withdraw(0), [], Exception)
                if not zero_withdraw_raises:
                    withdraw_result = safely_call_method(account2, "withdraw", 0)
                    if withdraw_result is not None:
                        errors.append("withdraw should reject zero amount")
                
                # Invalid withdrawal - negative
                negative_withdraw_raises = check_raises(lambda: account2.withdraw(-50), [], Exception)
                if not negative_withdraw_raises:
                    withdraw_result = safely_call_method(account2, "withdraw", -50)
                    if withdraw_result is not None:
                        errors.append("withdraw should reject negative amount")
                
                # Invalid withdrawal - exceeding balance
                current_balance = safely_get_attribute(account2, "balance")
                if current_balance is not None:
                    excess_amount = float(str(current_balance)) + 100
                    excess_withdraw_raises = check_raises(lambda: account2.withdraw(excess_amount), [], Exception)
                    if not excess_withdraw_raises:
                        withdraw_result = safely_call_method(account2, "withdraw", excess_amount)
                        if withdraw_result is not None:
                            errors.append("withdraw should reject amount exceeding balance")
                
                # Test with very large amounts
                large_amount_account = safely_create_instance(self.module_obj, "BankAccount", "ACCT999999", "Large Amount User", "1000000000")
                if large_amount_account is not None:
                    # Test deposit with very large amount
                    large_deposit = safely_call_method(large_amount_account, "deposit", "999999999")
                    if large_deposit is None:
                        errors.append("Failed to handle very large deposit amount")
                    
                    # Test withdrawal with very large amount
                    large_withdraw = safely_call_method(large_amount_account, "withdraw", "1000000000")
                    if large_withdraw is None:
                        errors.append("Failed to handle very large withdrawal amount")
                
                # Test rapid successive operations
                rapid_account = safely_create_instance(self.module_obj, "BankAccount", "ACCT777777", "Rapid User", 10000)
                if rapid_account is not None:
                    # Perform many small operations
                    for i in range(10):
                        safely_call_method(rapid_account, "deposit", 1)
                        safely_call_method(rapid_account, "withdraw", 1)
                    
                    # Check final balance and history
                    final_balance = safely_get_attribute(rapid_account, "balance")
                    if final_balance is None:
                        errors.append("Account should handle rapid successive operations")
                    
                    history = safely_call_method(rapid_account, "get_transaction_history")
                    if history is None:
                        errors.append("Transaction history should be accessible after rapid operations")
            
            # Test transfer function
            if check_function_exists(self.module_obj, "transfer"):
                account3 = safely_create_instance(self.module_obj, "BankAccount", "ACCT111111", "Alice Smith", 1000)
                account4 = safely_create_instance(self.module_obj, "BankAccount", "ACCT222222", "Bob Smith", 500)

                if account3 is not None and account4 is not None:
                    # Valid transfer
                    initial_balance3 = safely_get_attribute(account3, "balance")
                    initial_balance4 = safely_get_attribute(account4, "balance")

                    transfer_result = safely_call_function(self.module_obj, "transfer", account3, account4, 200)
                    if transfer_result is None:
                        errors.append("transfer function failed with valid parameters")
                    else:
                        final_balance3 = safely_get_attribute(account3, "balance")
                        final_balance4 = safely_get_attribute(account4, "balance")

                        if initial_balance3 is not None and final_balance3 is not None:
                            expected_balance3 = float(str(initial_balance3)) - 200
                            if abs(float(str(final_balance3)) - expected_balance3) > 0.01:
                                errors.append(f"Source account balance incorrect after transfer: {final_balance3}, expected {expected_balance3}")

                        if initial_balance4 is not None and final_balance4 is not None:
                            expected_balance4 = float(str(initial_balance4)) + 200
                            if abs(float(str(final_balance4)) - expected_balance4) > 0.01:
                                errors.append(f"Destination account balance incorrect after transfer: {final_balance4}, expected {expected_balance4}")

                        # Check transfer result
                        if isinstance(transfer_result, dict):
                            if transfer_result.get('status') != 'completed':
                                errors.append("Transfer result should indicate completion")

                    # Invalid transfer - exceeding source balance
                    current_balance = safely_get_attribute(account3, "balance")
                    if current_balance is not None:
                        excess_amount = float(str(current_balance)) + 100
                        excess_transfer_raises = check_raises(self.module_obj.transfer, [account3, account4, excess_amount], Exception)
                        if not excess_transfer_raises:
                            transfer_result = safely_call_function(self.module_obj, "transfer", account3, account4, excess_amount)
                            if transfer_result is not None:
                                errors.append("transfer should reject amount exceeding source balance")

                    # Logical error check - verify money conservation
                    balance3_before = safely_get_attribute(account3, "balance")
                    balance4_before = safely_get_attribute(account4, "balance")

                    if balance3_before is not None and balance4_before is not None:
                        total_before = float(str(balance3_before)) + float(str(balance4_before))

                        # Perform another transfer (smaller amount to ensure it doesn't exceed balance)
                        transfer_amount = min(100, float(str(balance3_before)) - 1)  # Ensure we don't exceed balance
                        if transfer_amount > 0:
                            safely_call_function(self.module_obj, "transfer", account3, account4, transfer_amount)

                            balance3_after = safely_get_attribute(account3, "balance")
                            balance4_after = safely_get_attribute(account4, "balance")

                            if balance3_after is not None and balance4_after is not None:
                                total_after = float(str(balance3_after)) + float(str(balance4_after))

                                if abs(total_before - total_after) > 0.01:  # Allow for small decimal precision issues
                                    errors.append(f"Money not conserved during transfer: before={total_before}, after={total_after}")
            else:
                errors.append("transfer function not found")
            
            # Test transaction history
            account5 = safely_create_instance(self.module_obj, "BankAccount", "ACCT333333", "Carol Brown", 1000)
            if account5 is not None:
                # Perform some operations
                safely_call_method(account5, "deposit", 200)
                safely_call_method(account5, "withdraw", 100)
                
                # Get transaction history
                history = safely_call_method(account5, "get_transaction_history")
                if history is None:
                    errors.append("get_transaction_history method not found or failed")
                elif not isinstance(history, list):
                    errors.append("get_transaction_history should return a list")
                
                # Test failed transaction recording
                try:
                    account5.withdraw(2000)  # Should fail
                except:
                    pass  # Expected to fail
                
                # Just check that history is still accessible
                final_history = safely_call_method(account5, "get_transaction_history")
                if final_history is None:
                    errors.append("Transaction history should still be accessible after failed operations")
            
            # Test exception classes exist
            exception_classes = ["BankingException", "InvalidInputError", "InvalidAmountError", "InsufficientFundsError"]
            for exc_class in exception_classes:
                if not check_class_exists(self.module_obj, exc_class):
                    errors.append(f"{exc_class} exception class not found")
            
            # Final assertion
            if errors:
                self.test_obj.yakshaAssert("TestBankingSystemBoundaries", False, "boundary")
                print("TestBankingSystemBoundaries = Failed")
            else:
                self.test_obj.yakshaAssert("TestBankingSystemBoundaries", True, "boundary")
                print("TestBankingSystemBoundaries = Passed")
                
        except Exception as e:
            self.test_obj.yakshaAssert("TestBankingSystemBoundaries", False, "boundary")
            print("TestBankingSystemBoundaries = Failed")

if __name__ == '__main__':
    unittest.main()