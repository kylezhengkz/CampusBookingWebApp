# TesterFailed: Exception when there exists at least 1 test that failed
class TesterFailed(Exception):
    def __init__(self, testName: str):
        super().__init__(f"There are some {testName} tests that failed!")