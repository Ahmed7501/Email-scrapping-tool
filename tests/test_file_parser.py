import unittest
import os
from file_parser import FileParser

class TestFileParser(unittest.TestCase):
    def setUp(self):
        self.parser = FileParser()
        # Create test files
        with open('test_urls.txt', 'w') as f:
            f.write('https://example.com\nhttps://test.com\n')
        with open('test_urls.csv', 'w') as f:
            f.write('url\nhttps://csv.com\nhttps://csv2.com\n')
        with open('test_urls2.txt', 'w') as f:
            f.write('Some text https://inline.com and more text\n')
        # Create a minimal Excel file if pandas is available
        try:
            import pandas as pd
            df = pd.DataFrame({'url': ['https://excel.com', 'https://excel2.com']})
            df.to_excel('test_urls.xlsx', index=False)
            self.has_pandas = True
        except ImportError:
            self.has_pandas = False
        # Create a minimal DOCX file
        try:
            from docx import Document
            doc = Document()
            doc.add_paragraph('https://docx.com')
            doc.save('test_urls.docx')
            self.has_docx = True
        except ImportError:
            self.has_docx = False

    def tearDown(self):
        for fname in [
            'test_urls.txt', 'test_urls.csv', 'test_urls2.txt',
            'test_urls.xlsx', 'test_urls.docx']:
            if os.path.exists(fname):
                os.remove(fname)

    def test_parse_txt(self):
        urls = self.parser.parse_file('test_urls.txt')
        self.assertIn('https://example.com', urls)
        self.assertIn('https://test.com', urls)

    def test_parse_csv(self):
        urls = self.parser.parse_file('test_urls.csv')
        self.assertIn('https://csv.com', urls)
        self.assertIn('https://csv2.com', urls)

    def test_parse_txt_inline(self):
        urls = self.parser.parse_file('test_urls2.txt')
        self.assertIn('https://inline.com', urls)

    def test_parse_excel(self):
        if self.has_pandas:
            urls = self.parser.parse_file('test_urls.xlsx')
            self.assertIn('https://excel.com', urls)
            self.assertIn('https://excel2.com', urls)
        else:
            self.skipTest('pandas not available')

    def test_parse_docx(self):
        if self.has_docx:
            urls = self.parser.parse_file('test_urls.docx')
            self.assertIn('https://docx.com', urls)
        else:
            self.skipTest('python-docx not available')

    def test_file_info(self):
        info = self.parser.get_file_info('test_urls.txt')
        self.assertEqual(info['extension'], '.txt')
        self.assertTrue(info['size_bytes'] > 0)
        self.assertTrue(info['exists'])

if __name__ == '__main__':
    unittest.main() 