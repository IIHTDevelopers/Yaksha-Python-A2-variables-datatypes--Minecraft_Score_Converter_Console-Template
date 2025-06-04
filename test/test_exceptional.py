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

def check_exception_type(func, args, expected_exception_name):
    """Check if a function raises an exception with the expected name."""
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            func(*args)
        return False, None
    except Exception as e:
        return True, type(e).__name__

def load_module_dynamically():
    """Load the student's module for testing"""
    module_obj = safely_import_module("banking_system_error_handling_framework")
    if module_obj is None:
        module_obj = safely_import_module("solution")
    return module_obj

class TestBankingExceptionHandling(unittest.TestCase):
    def setUp(self):
        """Standard setup for all test methods"""
        self.test_obj = TestUtils()
        self.module_obj = load_module_dynamically()
    
    def test_exception_handling(self):
        """Test all exception handling across the banking system"""
        try:
            # Check if module can be imported
            if self.module_obj is None:
                self.test_obj.yakshaAssert("TestBankingExceptionHandling", False, "exception")
                print("TestBankingExceptionHandling = Failed")
                return
            
            errors = []
            
            # Test BankingException base class
            if check_class_exists(self.module_obj, "BankingException"):
                # Test with error code
                banking_error = safely_create_instance(self.module_obj, "BankingException", "Test error message", "E999")
                if banking_error is not None:
                    error_str = str(banking_error)
                    if "E999" not in error_str or "Test error message" not in error_str:
                        errors.append("BankingException should format error with code properly")
                
                # Test without error code
                banking_error_no_code = safely_create_instance(self.module_obj, "BankingException", "Test error message")
                if banking_error_no_code is not None:
                    error_str = str(banking_error_no_code)
                    if "Test error message" not in error_str:
                        errors.append("BankingException should format error without code properly")
            else:
                errors.append("BankingException class not found")
            
            # Test InputValidator exceptions
            if check_class_exists(self.module_obj, "InputValidator"):
                # Test amount validation exceptions
                if check_function_exists(self.module_obj.InputValidator, "validate_amount"):
                    # Test non-numeric input
                    raised, exc_name = check_exception_type(
                        self.module_obj.InputValidator.validate_amount, 
                        ["invalid"], 
                        "InvalidInputError"
                    )
                    if not raised:
                        result = safely_call_function(self.module_obj.InputValidator, "validate_amount", "invalid")
                        if result is not None:
                            errors.append("validate_amount should raise exception for non-numeric input")
                    elif exc_name and "InvalidInputError" not in exc_name:
                        errors.append(f"Expected InvalidInputError for non-numeric input, got {exc_name}")
                    
                    # Test negative amount
                    raised, exc_name = check_exception_type(
                        self.module_obj.InputValidator.validate_amount, 
                        ["-100"], 
                        "InvalidAmountError"
                    )
                    if not raised:
                        result = safely_call_function(self.module_obj.InputValidator, "validate_amount", "-100")
                        if result is not None:
                            errors.append("validate_amount should raise exception for negative amount")
                    elif exc_name and "InvalidAmountError" not in exc_name:
                        errors.append(f"Expected InvalidAmountError for negative amount, got {exc_name}")
                    
                    # Test zero amount
                    raised, exc_name = check_exception_type(
                        self.module_obj.InputValidator.validate_amount, 
                        ["0"], 
                        "InvalidAmountError"
                    )
                    if not raised:
                        result = safely_call_function(self.module_obj.InputValidator, "validate_amount", "0")
                        if result is not None:
                            errors.append("validate_amount should raise exception for zero amount")
                    elif exc_name and "InvalidAmountError" not in exc_name:
                        errors.append(f"Expected InvalidAmountError for zero amount, got {exc_name}")
                
                # Test account ID validation exceptions
                if check_function_exists(self.module_obj.InputValidator, "validate_account_id"):
                    # Test non-string ID
                    raised, exc_name = check_exception_type(
                        self.module_obj.InputValidator.validate_account_id, 
                        [123], 
                        "InvalidInputError"
                    )
                    if not raised:
                        result = safely_call_function(self.module_obj.InputValidator, "validate_account_id", 123)
                        if result is not None:
                            errors.append("validate_account_id should raise exception for non-string ID")
                    
                    # Test too short ID
                    raised, exc_name = check_exception_type(
                        self.module_obj.InputValidator.validate_account_id, 
                        ["ABC"], 
                        "InvalidInputError"
                    )
                    if not raised:
                        result = safely_call_function(self.module_obj.InputValidator, "validate_account_id", "ABC")
                        if result is not None:
                            errors.append("validate_account_id should raise exception for too short ID")
                    
                    # Test invalid characters
                    raised, exc_name = check_exception_type(
                        self.module_obj.InputValidator.validate_account_id, 
                        ["ABCD123!@#"], 
                        "InvalidInputError"
                    )
                    if not raised:
                        result = safely_call_function(self.module_obj.InputValidator, "validate_account_id", "ABCD123!@#")
                        if result is not None:
                            errors.append("validate_account_id should raise exception for invalid characters")
            
            # Test BankAccount creation exceptions
            if check_class_exists(self.module_obj, "BankAccount"):
                # Test invalid ID
                invalid_id_account = safely_create_instance(self.module_obj, "BankAccount", "ABC", "John Doe", 100)
                if invalid_id_account is not None:
                    errors.append("BankAccount should not be created with invalid ID")
                
                # Test empty name
                empty_name_account = safely_create_instance(self.module_obj, "BankAccount", "ACCT123456", "", 100)
                if empty_name_account is not None:
                    errors.append("BankAccount should not be created with empty name")
                
                # Test negative balance
                negative_balance_account = safely_create_instance(self.module_obj, "BankAccount", "ACCT123456", "John Doe", -100)
                if negative_balance_account is not None:
                    errors.append("BankAccount should not be created with negative balance")
                
                # Test non-numeric balance
                non_numeric_balance_account = safely_create_instance(self.module_obj, "BankAccount", "ACCT123456", "John Doe", "abc")
                if non_numeric_balance_account is not None:
                    errors.append("BankAccount should not be created with non-numeric balance")
            
            # Create a valid account for further testing
            account = safely_create_instance(self.module_obj, "BankAccount", "ACCT123456", "John Doe", 1000)
            
            if account is not None:
                # Test deposit exceptions
                # Test negative deposit
                negative_deposit_raised = check_raises(lambda: account.deposit(-100), [], Exception)
                if not negative_deposit_raised:
                    result = safely_call_method(account, "deposit", -100)
                    if result is not None:
                        errors.append("deposit should raise exception for negative amount")
                
                # Test non-numeric deposit
                non_numeric_deposit_raised = check_raises(lambda: account.deposit("abc"), [], Exception)
                if not non_numeric_deposit_raised:
                    result = safely_call_method(account, "deposit", "abc")
                    if result is not None:
                        errors.append("deposit should raise exception for non-numeric amount")
                
                # Test zero deposit
                zero_deposit_raised = check_raises(lambda: account.deposit(0), [], Exception)
                if not zero_deposit_raised:
                    result = safely_call_method(account, "deposit", 0)
                    if result is not None:
                        errors.append("deposit should raise exception for zero amount")
                
                # Test withdrawal exceptions
                # Test negative withdrawal
                negative_withdraw_raised = check_raises(lambda: account.withdraw(-100), [], Exception)
                if not negative_withdraw_raised:
                    result = safely_call_method(account, "withdraw", -100)
                    if result is not None:
                        errors.append("withdraw should raise exception for negative amount")
                
                # Test non-numeric withdrawal
                non_numeric_withdraw_raised = check_raises(lambda: account.withdraw("abc"), [], Exception)
                if not non_numeric_withdraw_raised:
                    result = safely_call_method(account, "withdraw", "abc")
                    if result is not None:
                        errors.append("withdraw should raise exception for non-numeric amount")
                
                # Test zero withdrawal
                zero_withdraw_raised = check_raises(lambda: account.withdraw(0), [], Exception)
                if not zero_withdraw_raised:
                    result = safely_call_method(account, "withdraw", 0)
                    if result is not None:
                        errors.append("withdraw should raise exception for zero amount")
                
                # Test insufficient funds
                current_balance = safely_get_attribute(account, "balance")
                if current_balance is not None:
                    excessive_amount = float(str(current_balance)) + 1000
                    insufficient_funds_raised, exc_name = check_exception_type(
                        account.withdraw, 
                        [excessive_amount], 
                        "InsufficientFundsError"
                    )
                    if not insufficient_funds_raised:
                        result = safely_call_method(account, "withdraw", excessive_amount)
                        if result is not None:
                            errors.append("withdraw should raise exception for insufficient funds")
                    elif exc_name and "InsufficientFundsError" not in exc_name:
                        errors.append(f"Expected InsufficientFundsError for insufficient funds, got {exc_name}")
            else:
                errors.append("Failed to create valid BankAccount for testing operations")
            
            # Test exception message content
            if check_class_exists(self.module_obj, "InvalidAmountError"):
                try:
                    # Try to trigger InvalidAmountError with InputValidator
                    if check_class_exists(self.module_obj, "InputValidator") and check_function_exists(self.module_obj.InputValidator, "validate_amount"):
                        self.module_obj.InputValidator.validate_amount("-50")
                    else:
                        # Create exception directly
                        raise self.module_obj.InvalidAmountError("-50")
                except Exception as e:
                    error_message = str(e)
                    if "Invalid amount" not in error_message and "-50" not in error_message:
                        errors.append("InvalidAmountError should contain descriptive message")
                    if hasattr(e, "error_code") and e.error_code != "E001":
                        errors.append(f"InvalidAmountError should have error code E001, got {e.error_code}")
            
            if check_class_exists(self.module_obj, "InsufficientFundsError"):
                try:
                    # Create exception directly to test message format
                    insufficient_error = self.module_obj.InsufficientFundsError("ACC123", Decimal("200"), Decimal("100"))
                    error_message = str(insufficient_error)
                    if all(text not in error_message for text in ["Insufficient funds", "ACC123", "200", "100"]):
                        errors.append("InsufficientFundsError should contain descriptive message with account details")
                    if hasattr(insufficient_error, "error_code") and insufficient_error.error_code != "T001":
                        errors.append(f"InsufficientFundsError should have error code T001, got {insufficient_error.error_code}")
                except Exception as e:
                    errors.append(f"Failed to create InsufficientFundsError: {e}")
            
            # Test transfer exceptions
            if check_function_exists(self.module_obj, "transfer"):
                account1 = safely_create_instance(self.module_obj, "BankAccount", "ACCT111111", "Alice Smith", 500)
                account2 = safely_create_instance(self.module_obj, "BankAccount", "ACCT222222", "Bob Smith", 300)
                
                if account1 is not None and account2 is not None:
                    # Test invalid amount transfer
                    negative_transfer_raised = check_raises(self.module_obj.transfer, [account1, account2, -100], Exception)
                    if not negative_transfer_raised:
                        result = safely_call_function(self.module_obj, "transfer", account1, account2, -100)
                        if result is not None:
                            errors.append("transfer should raise exception for negative amount")
                    
                    # Test insufficient funds transfer
                    current_balance = safely_get_attribute(account1, "balance")
                    if current_balance is not None:
                        excessive_amount = float(str(current_balance)) + 100
                        insufficient_transfer_raised, exc_name = check_exception_type(
                            self.module_obj.transfer, 
                            [account1, account2, excessive_amount], 
                            "InsufficientFundsError"
                        )
                        if not insufficient_transfer_raised:
                            result = safely_call_function(self.module_obj, "transfer", account1, account2, excessive_amount)
                            if result is not None:
                                errors.append("transfer should raise exception for insufficient funds")
                        elif exc_name and "InsufficientFundsError" not in exc_name:
                            errors.append(f"Expected InsufficientFundsError for insufficient transfer, got {exc_name}")
            
            # Test transaction history error recording
            account3 = safely_create_instance(self.module_obj, "BankAccount", "ACCT333333", "Charlie Davis", 1000)
            if account3 is not None:
                # Record successful transaction
                safely_call_method(account3, "deposit", 500)
                
                # Record failed transaction
                try:
                    account3.withdraw(2000)  # Should fail
                except:
                    pass  # Expected to fail
                
                # Check transaction history
                history = safely_call_method(account3, "get_transaction_history")
                if history is not None and isinstance(history, list):
                    # Look for completed and failed transactions
                    completed_found = False
                    failed_found = False
                    
                    for transaction in history:
                        if isinstance(transaction, dict):
                            if transaction.get('status') == 'completed':
                                completed_found = True
                                if 'error' in transaction:
                                    errors.append("Completed transaction should not have error field")
                            elif transaction.get('status') == 'failed':
                                failed_found = True
                                if 'error' not in transaction:
                                    errors.append("Failed transaction should have error field")
                    
                    if not completed_found:
                        errors.append("Transaction history should record completed transactions")
                    if not failed_found:
                        errors.append("Transaction history should record failed transactions")
                else:
                    errors.append("get_transaction_history should return a list")
            
            # Test exception inheritance
            exception_classes = {}
            for exc_name in ["BankingException", "InvalidInputError", "InvalidAmountError", "InsufficientFundsError"]:
                if check_class_exists(self.module_obj, exc_name):
                    exception_classes[exc_name] = getattr(self.module_obj, exc_name)
            
            # Test inheritance relationships
            if "BankingException" in exception_classes and "InvalidInputError" in exception_classes:
                if not issubclass(exception_classes["InvalidInputError"], exception_classes["BankingException"]):
                    errors.append("InvalidInputError should inherit from BankingException")
            
            if "InvalidInputError" in exception_classes and "InvalidAmountError" in exception_classes:
                if not issubclass(exception_classes["InvalidAmountError"], exception_classes["InvalidInputError"]):
                    errors.append("InvalidAmountError should inherit from InvalidInputError")
            
            if "BankingException" in exception_classes and "InsufficientFundsError" in exception_classes:
                if not issubclass(exception_classes["InsufficientFundsError"], exception_classes["BankingException"]):
                    errors.append("InsufficientFundsError should inherit from BankingException")
            
            # Test that exceptions inherit from Exception
            for exc_name, exc_class in exception_classes.items():
                if not issubclass(exc_class, Exception):
                    errors.append(f"{exc_name} should inherit from Exception")
            
            # Test rollback functionality with simulated failure
            if check_function_exists(self.module_obj, "transfer"):
                account4 = safely_create_instance(self.module_obj, "BankAccount", "ACCT444444", "David Wilson", 1000)
                account5 = safely_create_instance(self.module_obj, "BankAccount", "ACCT555555", "Eve Wilson", 500)
                
                if account4 is not None and account5 is not None:
                    # Record initial balances
                    initial_balance4 = safely_get_attribute(account4, "balance")
                    initial_balance5 = safely_get_attribute(account5, "balance")
                    
                    # Try to manipulate account5 to simulate deposit failure
                    # This is a complex test that may not work with all implementations
                    if hasattr(account5, 'deposit'):
                        original_deposit = account5.deposit
                        
                        def failing_deposit(amount):
                            # Check if the first part of transfer was created properly 
                            if check_class_exists(self.module_obj, "BankingException"):
                                raise self.module_obj.BankingException("Simulated deposit failure", "TEST001")
                            else:
                                raise Exception("Simulated deposit failure")
                        
                        # Replace deposit method temporarily
                        account5.deposit = failing_deposit
                        
                        try:
                            # This transfer should fail and rollback
                            self.module_obj.transfer(account4, account5, 200)
                            errors.append("Transfer should have failed due to deposit failure")
                        except Exception:
                            # Check if rollback occurred
                            final_balance4 = safely_get_attribute(account4, "balance")
                            final_balance5 = safely_get_attribute(account5, "balance")
                            
                            if (initial_balance4 is not None and final_balance4 is not None and 
                                str(initial_balance4) != str(final_balance4)):
                                errors.append("Transfer should rollback source account on failure")
                            
                            if (initial_balance5 is not None and final_balance5 is not None and 
                                str(initial_balance5) != str(final_balance5)):
                                errors.append("Transfer should not affect destination account on failure")
                        
                        # Restore original method
                        account5.deposit = original_deposit
            
            # Final assertion
            if errors:
                self.test_obj.yakshaAssert("TestBankingExceptionHandling", False, "exception")
                print("TestBankingExceptionHandling = Failed")
            else:
                self.test_obj.yakshaAssert("TestBankingExceptionHandling", True, "exception")
                print("TestBankingExceptionHandling = Passed")
                
        except Exception as e:
            self.test_obj.yakshaAssert("TestBankingExceptionHandling", False, "exception")
            print("TestBankingExceptionHandling = Failed")

    def test_error_recovery(self):
        """Test system's ability to recover from errors and maintain consistency"""
        try:
            # Check if module can be imported
            if self.module_obj is None:
                self.test_obj.yakshaAssert("TestErrorRecovery", False, "exception")
                print("TestErrorRecovery = Failed")
                return
            
            errors = []
            
            # Test account state after failed operations
            account = safely_create_instance(self.module_obj, "BankAccount", "ACCT999999", "Recovery Test", 1000)
            if account is not None:
                initial_balance = safely_get_attribute(account, "balance")
                
                # Try several invalid operations
                invalid_operations = [
                    lambda: account.deposit(-100),
                    lambda: account.deposit("invalid"),
                    lambda: account.withdraw(-50),
                    lambda: account.withdraw("invalid"),
                    lambda: account.withdraw(2000),  # Exceeds balance
                ]
                
                for operation in invalid_operations:
                    try:
                        operation()
                    except:
                        pass  # Expected to fail
                    
                    # Check that balance hasn't changed
                    current_balance = safely_get_attribute(account, "balance")
                    if current_balance is None:
                        errors.append("Account balance should remain accessible after failed operations")
                        break
                    elif str(current_balance) != str(initial_balance):
                        errors.append("Account balance should not change after failed operations")
                        break
                
                # Test that valid operations still work after failures
                initial_balance_before_test = safely_get_attribute(account, "balance")
                final_deposit = safely_call_method(account, "deposit", 100)
                if final_deposit is None:
                    errors.append("Valid operations should work after failed operations")
                else:
                    final_balance = safely_get_attribute(account, "balance")
                    if final_balance is None:
                        errors.append("Balance should be accessible after deposit")
                    elif initial_balance_before_test is not None:
                        expected_final = float(str(initial_balance_before_test)) + 100
                        if abs(float(str(final_balance)) - expected_final) > 0.01:
                            errors.append("Account should function normally after error recovery")
            
            # Test multiple account interactions with errors
            if check_function_exists(self.module_obj, "transfer"):
                account1 = safely_create_instance(self.module_obj, "BankAccount", "ACCT888888", "Multi Test 1", 1000)
                account2 = safely_create_instance(self.module_obj, "BankAccount", "ACCT777777", "Multi Test 2", 500)
                
                if account1 is not None and account2 is not None:
                    # Record initial state
                    initial_total = 0
                    balance1 = safely_get_attribute(account1, "balance")
                    balance2 = safely_get_attribute(account2, "balance")
                    if balance1 is not None and balance2 is not None:
                        initial_total = float(str(balance1)) + float(str(balance2))
                    
                    # Try invalid transfers
                    invalid_transfers = [
                        lambda: self.module_obj.transfer(account1, account2, -100),
                        lambda: self.module_obj.transfer(account1, account2, 2000),  # Exceeds balance
                    ]
                    
                    for transfer_op in invalid_transfers:
                        try:
                            transfer_op()
                        except:
                            pass  # Expected to fail
                        
                        # Check total money conservation
                        balance1 = safely_get_attribute(account1, "balance")
                        balance2 = safely_get_attribute(account2, "balance")
                        if balance1 is not None and balance2 is not None:
                            current_total = float(str(balance1)) + float(str(balance2))
                            if abs(current_total - initial_total) > 0.01:
                                errors.append("Total money should be conserved even after failed transfers")
                                break
                    
                    # Test that valid transfer still works
                    valid_transfer = safely_call_function(self.module_obj, "transfer", account1, account2, 200)
                    if valid_transfer is None:
                        errors.append("Valid transfers should work after failed transfer attempts")
            
            # Test exception chaining and context
            if check_class_exists(self.module_obj, "InputValidator"):
                # Test that exceptions provide useful context
                try:
                    if check_function_exists(self.module_obj.InputValidator, "validate_amount"):
                        self.module_obj.InputValidator.validate_amount("clearly not a number")
                except Exception as e:
                    error_message = str(e)
                    if len(error_message) < 10:
                        errors.append("Exception messages should be descriptive")
                    
                    # Check if error has useful attributes
                    if not hasattr(e, 'args') or len(e.args) == 0:
                        errors.append("Exceptions should have meaningful arguments")
            
            # Test system state after multiple errors
            if check_class_exists(self.module_obj, "BankAccount"):
                stress_account = safely_create_instance(self.module_obj, "BankAccount", "ACCT666666", "Stress Test", 5000)
                if stress_account is not None:
                    # Perform mix of valid and invalid operations
                    operations = [
                        lambda: stress_account.deposit(100),     # Valid
                        lambda: stress_account.withdraw(-50),    # Invalid
                        lambda: stress_account.deposit(200),     # Valid
                        lambda: stress_account.withdraw(10000),  # Invalid
                        lambda: stress_account.withdraw(100),    # Valid
                        lambda: stress_account.deposit("bad"),   # Invalid
                    ]
                    
                    valid_operations = 0
                    for i, operation in enumerate(operations):
                        try:
                            result = operation()
                            if result is not None:
                                valid_operations += 1
                        except:
                            pass  # Some operations are expected to fail
                    
                    # Check final state
                    final_balance = safely_get_attribute(stress_account, "balance")
                    if final_balance is None:
                        errors.append("Account should remain functional after stress testing")
                    
                    # Check transaction history
                    history = safely_call_method(stress_account, "get_transaction_history")
                    if history is not None and isinstance(history, list):
                        completed_count = sum(1 for tx in history if isinstance(tx, dict) and tx.get('status') == 'completed')
                        failed_count = sum(1 for tx in history if isinstance(tx, dict) and tx.get('status') == 'failed')
                        
                        if completed_count == 0:
                            errors.append("Should have some completed transactions in history")
                        if failed_count == 0:
                            errors.append("Should have some failed transactions in history")
            
            # Final assertion
            if errors:
                self.test_obj.yakshaAssert("TestErrorRecovery", False, "exception")
                print("TestErrorRecovery = Failed")
            else:
                self.test_obj.yakshaAssert("TestErrorRecovery", True, "exception")
                print("TestErrorRecovery = Passed")
                
        except Exception as e:
            self.test_obj.yakshaAssert("TestErrorRecovery", False, "exception")
            print("TestErrorRecovery = Failed")

if __name__ == '__main__':
    unittest.main()