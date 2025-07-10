"""
Output Writer Module

This module handles exporting scraping results to various file formats
including CSV and Excel with proper formatting and organization.
"""

import logging
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("Warning: pandas not available. Using CSV-only output.")
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OutputWriter:
    """
    A class for writing scraping results to various output formats.
    
    This class provides methods to export results to CSV and Excel files
    with proper formatting and organization.
    """
    
    def __init__(self, output_dir: str = "output"):
        """
        Initialize the OutputWriter.
        
        Args:
            output_dir (str): Directory to save output files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def write_results_to_csv(self, results: List[Dict[str, Any]], 
                           filename: str = None) -> str:
        """
        Write scraping results to a CSV file.
        
        Args:
            results (List[Dict[str, Any]]): List of scraping results
            filename (str): Output filename (optional)
            
        Returns:
            str: Path to the created CSV file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"email_scraping_results_{timestamp}.csv"
        
        filepath = self.output_dir / filename
        
        try:
            # Convert results to DataFrame
            df = self._prepare_dataframe(results)
            
            # Write to CSV
            df.to_csv(filepath, index=False, encoding='utf-8')
            
            logger.info(f"Results written to CSV: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error writing CSV file: {e}")
            raise
    
    def write_results_to_excel(self, results: List[Dict[str, Any]], 
                              filename: str = None) -> str:
        """
        Write scraping results to an Excel file with multiple sheets.
        
        Args:
            results (List[Dict[str, Any]]): List of scraping results
            filename (str): Output filename (optional)
            
        Returns:
            str: Path to the created Excel file
        """
        if not PANDAS_AVAILABLE:
            raise ImportError("pandas is required for Excel output. Please install pandas.")
            
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"email_scraping_results_{timestamp}.xlsx"
        
        filepath = self.output_dir / filename
        
        try:
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Main results sheet
                main_df = self._prepare_dataframe(results)
                main_df.to_excel(writer, sheet_name='Email_Results', index=False)
                
                # Summary sheet
                summary_df = self._create_summary_dataframe(results)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # Social media results sheet
                social_results = [r for r in results if r.get('source_type') == 'social']
                if social_results:
                    social_df = self._prepare_social_dataframe(social_results)
                    social_df.to_excel(writer, sheet_name='Social_Media_Results', index=False)
                
                # Failed URLs sheet
                failed_results = [r for r in results if r.get('status') == 'failed']
                if failed_results:
                    failed_df = self._prepare_failed_dataframe(failed_results)
                    failed_df.to_excel(writer, sheet_name='Failed_URLs', index=False)
            
            logger.info(f"Results written to Excel: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error writing Excel file: {e}")
            raise
    
    def _prepare_dataframe(self, results: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Prepare a DataFrame from scraping results.
        
        Args:
            results (List[Dict[str, Any]]): List of scraping results
            
        Returns:
            pd.DataFrame: Formatted DataFrame
        """
        if not results:
            return pd.DataFrame()
        
        # Extract and flatten the data
        rows = []
        for result in results:
            url = result.get('url', '')
            status = result.get('status', 'unknown')
            emails = result.get('emails', [])
            source_page = result.get('source_page', '')
            scraping_method = result.get('scraping_method', '')
            error = result.get('error', '')
            
            if emails:
                # Create a row for each email found
                for email in emails:
                    rows.append({
                        'URL': url,
                        'Email': email,
                        'Source_Page': source_page,
                        'Status': status,
                        'Scraping_Method': scraping_method,
                        'Error': error,
                        'Timestamp': datetime.now().isoformat()
                    })
            else:
                # Create a row even if no emails found
                rows.append({
                    'URL': url,
                    'Email': '',
                    'Source_Page': source_page,
                    'Status': status,
                    'Scraping_Method': scraping_method,
                    'Error': error,
                    'Timestamp': datetime.now().isoformat()
                })
        
        df = pd.DataFrame(rows)
        
        # Reorder columns for better readability
        column_order = [
            'URL', 'Email', 'Source_Page', 'Status', 
            'Scraping_Method', 'Error', 'Timestamp'
        ]
        
        # Only include columns that exist
        existing_columns = [col for col in column_order if col in df.columns]
        df = df[existing_columns]
        
        return df
    
    def _create_summary_dataframe(self, results: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Create a summary DataFrame with statistics.
        
        Args:
            results (List[Dict[str, Any]]): List of scraping results
            
        Returns:
            pd.DataFrame: Summary DataFrame
        """
        total_urls = len(results)
        successful_urls = len([r for r in results if r.get('status') == 'success'])
        failed_urls = len([r for r in results if r.get('status') == 'failed'])
        
        all_emails = []
        for result in results:
            emails = result.get('emails', [])
            all_emails.extend(emails)
        
        unique_emails = list(set(all_emails))
        
        # Count emails by domain
        email_domains = {}
        for email in unique_emails:
            if '@' in email:
                domain = email.split('@')[1]
                email_domains[domain] = email_domains.get(domain, 0) + 1
        
        # Create summary data
        summary_data = {
            'Metric': [
                'Total URLs Processed',
                'Successful Scrapes',
                'Failed Scrapes',
                'Total Emails Found',
                'Unique Emails Found',
                'Success Rate (%)',
                'Average Emails per URL'
            ],
            'Value': [
                total_urls,
                successful_urls,
                failed_urls,
                len(all_emails),
                len(unique_emails),
                round((successful_urls / total_urls * 100) if total_urls > 0 else 0, 2),
                round(len(all_emails) / total_urls, 2) if total_urls > 0 else 0
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        
        # Add top email domains
        if email_domains:
            top_domains = sorted(email_domains.items(), key=lambda x: x[1], reverse=True)[:10]
            domain_data = {
                'Email Domain': [domain for domain, count in top_domains],
                'Count': [count for domain, count in top_domains]
            }
            domain_df = pd.DataFrame(domain_data)
            
            # Combine summary and domain data
            combined_data = {
                'Metric': summary_data['Metric'] + [''] + ['Top Email Domains:'] + [''] * (len(top_domains) - 1),
                'Value': summary_data['Value'] + [''] + [''] + [''] * (len(top_domains) - 1)
            }
            
            summary_df = pd.DataFrame(combined_data)
        
        return summary_df
    
    def _prepare_social_dataframe(self, social_results: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Prepare a DataFrame for social media scraping results.
        
        Args:
            social_results (List[Dict[str, Any]]): Social media scraping results
            
        Returns:
            pd.DataFrame: Social media results DataFrame
        """
        rows = []
        
        for result in social_results:
            platform = result.get('platform', '')
            url = result.get('url', '')
            title = result.get('title', '')
            emails = result.get('emails', [])
            contact_info = result.get('contact_info', {})
            
            if emails:
                for email in emails:
                    rows.append({
                        'Platform': platform,
                        'Profile_URL': url,
                        'Profile_Title': title,
                        'Email': email,
                        'Contact_Info': str(contact_info) if contact_info else ''
                    })
            else:
                rows.append({
                    'Platform': platform,
                    'Profile_URL': url,
                    'Profile_Title': title,
                    'Email': '',
                    'Contact_Info': str(contact_info) if contact_info else ''
                })
        
        return pd.DataFrame(rows)
    
    def _prepare_failed_dataframe(self, failed_results: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Prepare a DataFrame for failed scraping results.
        
        Args:
            failed_results (List[Dict[str, Any]]): Failed scraping results
            
        Returns:
            pd.DataFrame: Failed results DataFrame
        """
        rows = []
        
        for result in failed_results:
            rows.append({
                'URL': result.get('url', ''),
                'Error': result.get('error', ''),
                'Scraping_Method': result.get('scraping_method', ''),
                'Timestamp': datetime.now().isoformat()
            })
        
        return pd.DataFrame(rows)
    
    def write_detailed_report(self, results: List[Dict[str, Any]], 
                            filename: str = None) -> str:
        """
        Write a detailed report with comprehensive information.
        
        Args:
            results (List[Dict[str, Any]]): List of scraping results
            filename (str): Output filename (optional)
            
        Returns:
            str: Path to the created report file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"detailed_report_{timestamp}.txt"
        
        filepath = self.output_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("EMAIL SCRAPING DETAILED REPORT\n")
                f.write("=" * 50 + "\n\n")
                
                # Summary statistics
                total_urls = len(results)
                successful_urls = len([r for r in results if r.get('status') == 'success'])
                failed_urls = len([r for r in results if r.get('status') == 'failed'])
                
                f.write(f"SUMMARY STATISTICS:\n")
                f.write(f"Total URLs processed: {total_urls}\n")
                f.write(f"Successful scrapes: {successful_urls}\n")
                f.write(f"Failed scrapes: {failed_urls}\n")
                f.write(f"Success rate: {(successful_urls/total_urls*100):.2f}%\n\n")
                
                # Email statistics
                all_emails = []
                for result in results:
                    emails = result.get('emails', [])
                    all_emails.extend(emails)
                
                unique_emails = list(set(all_emails))
                
                f.write(f"EMAIL STATISTICS:\n")
                f.write(f"Total emails found: {len(all_emails)}\n")
                f.write(f"Unique emails: {len(unique_emails)}\n")
                f.write(f"Average emails per URL: {len(all_emails)/total_urls:.2f}\n\n")
                
                # Results by URL
                f.write("DETAILED RESULTS BY URL:\n")
                f.write("-" * 30 + "\n")
                
                for i, result in enumerate(results, 1):
                    f.write(f"\n{i}. {result.get('url', 'N/A')}\n")
                    f.write(f"   Status: {result.get('status', 'N/A')}\n")
                    f.write(f"   Method: {result.get('scraping_method', 'N/A')}\n")
                    
                    emails = result.get('emails', [])
                    if emails:
                        f.write(f"   Emails found: {len(emails)}\n")
                        for email in emails:
                            f.write(f"     - {email}\n")
                    else:
                        f.write("   No emails found\n")
                    
                    error = result.get('error')
                    if error:
                        f.write(f"   Error: {error}\n")
                
                # Unique emails list
                f.write(f"\n\nUNIQUE EMAILS FOUND:\n")
                f.write("-" * 20 + "\n")
                for email in sorted(unique_emails):
                    f.write(f"{email}\n")
            
            logger.info(f"Detailed report written: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error writing detailed report: {e}")
            raise
    
    def get_output_files(self) -> List[str]:
        """
        Get list of all output files in the output directory.
        
        Returns:
            List[str]: List of output file paths
        """
        files = []
        for file_path in self.output_dir.glob("*"):
            if file_path.is_file():
                files.append(str(file_path))
        
        return sorted(files)


# Convenience functions for quick output writing
def write_to_csv(results: List[Dict[str, Any]], filename: str = None) -> str:
    """
    Convenience function to write results to CSV.
    
    Args:
        results (List[Dict[str, Any]]): List of scraping results
        filename (str): Output filename (optional)
        
    Returns:
        str: Path to the created CSV file
    """
    writer = OutputWriter()
    return writer.write_results_to_csv(results, filename)


def write_to_excel(results: List[Dict[str, Any]], filename: str = None) -> str:
    """
    Convenience function to write results to Excel.
    
    Args:
        results (List[Dict[str, Any]]): List of scraping results
        filename (str): Output filename (optional)
        
    Returns:
        str: Path to the created Excel file
    """
    writer = OutputWriter()
    return writer.write_results_to_excel(results, filename) 