def pytest_sessionfinish(session, exitstatus):
    print("\nTEST RESULT:", "PASSED" if exitstatus == 0 else "FAILED")
