import unittest
import os
from output_writer import OutputWriter

class TestOutputWriter(unittest.TestCase):
    def setUp(self):
        self.writer = OutputWriter(output_dir="test_output")
        self.results = [
            {
                'url': 'https://example.com',
                'emails': ['a@example.com', 'b@example.com'],
                'source_page': 'https://example.com',
                'status': 'success',
                'scraping_method': 'requests',
                'error': '',
                'timestamp': '2024-01-01T00:00:00',
            },
            {
                'url': 'https://fail.com',
                'emails': [],
                'source_page': 'https://fail.com',
                'status': 'failed',
                'scraping_method': 'requests',
                'error': 'Timeout',
                'timestamp': '2024-01-01T00:00:01',
            }
        ]

    def tearDown(self):
        # Remove all files in test_output
        for fname in os.listdir('test_output'):
            os.remove(os.path.join('test_output', fname))
        os.rmdir('test_output')

    def test_write_results_to_csv(self):
        csv_path = self.writer.write_results_to_csv(self.results, filename="test_results.csv")
        self.assertTrue(os.path.exists(csv_path))
        with open(csv_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('a@example.com', content)
            self.assertIn('b@example.com', content)
            self.assertIn('Timeout', content)

    def test_write_results_to_excel(self):
        try:
            import pandas as pd
            excel_path = self.writer.write_results_to_excel(self.results, filename="test_results.xlsx")
            self.assertTrue(os.path.exists(excel_path))
        except ImportError:
            self.skipTest('pandas not available')

    def test_write_detailed_report(self):
        report_path = self.writer.write_detailed_report(self.results, filename="test_report.txt")
        self.assertTrue(os.path.exists(report_path))
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('EMAIL SCRAPING DETAILED REPORT', content)
            self.assertIn('a@example.com', content)
            self.assertIn('Timeout', content)

    def test_get_output_files(self):
        self.writer.write_results_to_csv(self.results, filename="test_results.csv")
        files = self.writer.get_output_files()
        self.assertTrue(any(f.endswith('.csv') for f in files))

if __name__ == '__main__':
    unittest.main() 