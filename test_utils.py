# test_utils.py
import unittest
import logging
from utils import LoginLogger

class TestLoginLogger(unittest.TestCase):
    def setUp(self):
        self.logger_file = 'test.log'
        self.logger = LoginLogger(logger_file=self.logger_file, debug=True)

    def test_debug_logging(self):
        self.logger.logger.debug('This is a debug message')
        with open(self.logger_file, 'r') as f:
            log_content = f.read()
        self.assertIn('This is a debug message', log_content)

    def test_info_logging(self):
        self.logger.logger.info('This is an info message')
        with open(self.logger_file, 'r') as f:
            log_content = f.read()
        self.assertIn('This is an info message', log_content)

    def test_error_logging(self):
        self.logger.logger.error('This is an error message')
        with open(self.logger_file, 'r') as f:
            log_content = f.read()
        self.assertIn('This is an error message', log_content)

if __name__ == '__main__':
    unittest.main()