import unittest
import os

def run_all_tests():
    loader = unittest.TestLoader()
    suite = loader.discover(os.path.dirname(__file__), pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    with open(os.path.join(os.path.dirname(__file__), "test_results.txt"), "w", encoding="utf-8") as f:
        runner = unittest.TextTestRunner(stream=f, verbosity=2)
        result = runner.run(suite)
    print("测试已完成，结果已保存到 test/test_results.txt")

if __name__ == "__main__":
    run_all_tests()
