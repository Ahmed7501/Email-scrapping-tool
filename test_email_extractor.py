"""
Unit tests for the email_extractor module.
"""

import unittest
from email_extractor import EmailExtractor, extract_emails


class TestEmailExtractor(unittest.TestCase):
    """Test cases for EmailExtractor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.extractor = EmailExtractor()
    
    def test_extract_emails_from_text_simple(self):
        """Test extracting simple email addresses from text."""
        text = "Contact us at john@example.com or support@test.org"
        emails = self.extractor.extract_emails_from_text(text)
        
        self.assertEqual(len(emails), 2)
        self.assertIn('john@example.com', emails)
        self.assertIn('support@test.org', emails)
    
    def test_extract_emails_from_text_complex(self):
        """Test extracting emails from complex text."""
        text = """
        Our team members:
        - Alice Johnson: alice.johnson@company.com
        - Bob Smith: bob.smith@company.com
        - Carol Davis: carol.davis@company.com
        
        For support: help@company.com
        For sales: sales@company.com
        """
        
        emails = self.extractor.extract_emails_from_text(text)
        
        self.assertEqual(len(emails), 5)
        expected_emails = [
            'alice.johnson@company.com',
            'bob.smith@company.com',
            'carol.davis@company.com',
            'help@company.com',
            'sales@company.com'
        ]
        
        for email in expected_emails:
            self.assertIn(email, emails)
    
    def test_extract_emails_from_html(self):
        """Test extracting emails from HTML content."""
        html = """
        <html>
            <body>
                <p>Contact us at <a href="mailto:contact@example.com">contact@example.com</a></p>
                <p>Email: info@example.com</p>
                <div data-email="support@example.com">Support</div>
            </body>
        </html>
        """
        
        emails_with_context = self.extractor.extract_emails_from_html(html)
        
        self.assertEqual(len(emails_with_context), 3)
        
        emails = [email for email, context in emails_with_context]
        self.assertIn('contact@example.com', emails)
        self.assertIn('info@example.com', emails)
        self.assertIn('support@example.com', emails)
    
    def test_filter_false_positives(self):
        """Test filtering out false positive emails."""
        text = """
        Valid emails: user@company.com, admin@business.org
        False positives: user@example.com, test@test.com, admin@localhost
        """
        
        emails = self.extractor.extract_emails_from_text(text)
        
        # Should filter out false positives
        self.assertNotIn('user@example.com', emails)
        self.assertNotIn('test@test.com', emails)
        self.assertNotIn('admin@localhost', emails)
        
        # Should keep valid emails
        self.assertIn('user@company.com', emails)
        self.assertIn('admin@business.org', emails)
    
    def test_trusted_domains(self):
        """Test that trusted domains are always accepted."""
        text = "Contact: user@gmail.com, admin@yahoo.com, support@hotmail.com"
        
        emails = self.extractor.extract_emails_from_text(text)
        
        self.assertEqual(len(emails), 3)
        self.assertIn('user@gmail.com', emails)
        self.assertIn('admin@yahoo.com', emails)
        self.assertIn('support@hotmail.com', emails)
    
    def test_empty_input(self):
        """Test handling of empty input."""
        emails = self.extractor.extract_emails_from_text("")
        self.assertEqual(emails, [])
    
    def test_invalid_emails(self):
        """Test filtering of invalid email formats."""
        text = """
        Invalid: user@, @domain.com, user.domain.com, user@domain
        Valid: user@domain.com, user.name@domain.org
        """
        
        emails = self.extractor.extract_emails_from_text(text)
        
        # Should only contain valid emails
        self.assertEqual(len(emails), 2)
        self.assertIn('user@domain.com', emails)
        self.assertIn('user.name@domain.org', emails)
    
    def test_convenience_function(self):
        """Test the convenience function."""
        text = "Contact: test@example.com"
        emails = extract_emails(text)
        
        self.assertEqual(len(emails), 1)
        self.assertIn('test@example.com', emails)
    
    def test_filter_by_domain(self):
        """Test filtering emails by domain."""
        emails = [
            'user@company.com',
            'admin@company.com',
            'support@other.com',
            'info@company.com'
        ]
        
        target_domains = {'company.com'}
        filtered = self.extractor.filter_emails_by_domain(emails, target_domains)
        
        self.assertEqual(len(filtered), 3)
        self.assertIn('user@company.com', filtered)
        self.assertIn('admin@company.com', filtered)
        self.assertIn('info@company.com', filtered)
        self.assertNotIn('support@other.com', filtered)


class TestEmailExtractorEdgeCases(unittest.TestCase):
    """Test edge cases for EmailExtractor."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.extractor = EmailExtractor()
    
    def test_very_long_emails(self):
        """Test handling of very long email addresses."""
        long_email = "a" * 50 + "@" + "b" * 50 + ".com"
        text = f"Email: {long_email}"
        
        emails = self.extractor.extract_emails_from_text(text)
        self.assertEqual(len(emails), 1)
        self.assertIn(long_email, emails)
    
    def test_special_characters(self):
        """Test emails with special characters."""
        text = "Emails: user+tag@domain.com, user.name@domain.com, user-name@domain.com"
        
        emails = self.extractor.extract_emails_from_text(text)
        
        self.assertEqual(len(emails), 3)
        self.assertIn('user+tag@domain.com', emails)
        self.assertIn('user.name@domain.com', emails)
        self.assertIn('user-name@domain.com', emails)
    
    def test_multiple_at_symbols(self):
        """Test handling of text with multiple @ symbols."""
        text = "Contact: user@domain.com and also check @username on Twitter"
        
        emails = self.extractor.extract_emails_from_text(text)
        
        self.assertEqual(len(emails), 1)
        self.assertIn('user@domain.com', emails)


if __name__ == '__main__':
    unittest.main() 