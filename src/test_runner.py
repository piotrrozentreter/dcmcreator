"""
Test Runner for DICOM transmission testing.

Provides utilities to run various transmission tests and generate reports.
"""

import os
import time
from datetime import datetime
from pathlib import Path


class TestRunner:
    """Execute transmission tests and track results."""
    
    def __init__(self, logger=None):
        """Initialize test runner.
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger
        self.test_results = []
        self.current_test = None
    
    def start_test(self, test_name, description=""):
        """Start a new test.
        
        Args:
            test_name: Name of the test
            description: Optional description
        """
        self.current_test = {
            'name': test_name,
            'description': description,
            'start_time': datetime.now(),
            'end_time': None,
            'status': 'RUNNING',
            'files_sent': 0,
            'files_failed': 0,
            'total_bytes': 0,
            'errors': []
        }
        
        if self.logger:
            self.logger.warning(f"Test started: {test_name}")
    
    def add_file_result(self, filename, success, bytes_sent=0, time_taken=0, error=None):
        """Record result for a transmitted file.
        
        Args:
            filename: File that was sent
            success: Boolean indicating success
            bytes_sent: Number of bytes transmitted
            time_taken: Time to transmit in seconds
            error: Error message if failed
        """
        if not self.current_test:
            return
        
        if success:
            self.current_test['files_sent'] += 1
            self.current_test['total_bytes'] += bytes_sent
        else:
            self.current_test['files_failed'] += 1
            if error:
                self.current_test['errors'].append({
                    'file': filename,
                    'error': error,
                    'time': datetime.now()
                })
    
    def end_test(self, status='PASSED'):
        """End current test.
        
        Args:
            status: Test status (PASSED, FAILED, INTERRUPTED)
        """
        if not self.current_test:
            return
        
        self.current_test['end_time'] = datetime.now()
        self.current_test['status'] = status
        
        duration = (self.current_test['end_time'] - 
                   self.current_test['start_time']).total_seconds()
        
        # Calculate stats
        total_files = (self.current_test['files_sent'] + 
                      self.current_test['files_failed'])
        success_rate = (self.current_test['files_sent'] / total_files * 100 
                       if total_files > 0 else 0)
        throughput = (self.current_test['total_bytes'] / duration / 1024 / 1024 
                     if duration > 0 else 0)
        
        self.current_test['duration'] = duration
        self.current_test['success_rate'] = success_rate
        self.current_test['throughput_mbps'] = throughput
        
        self.test_results.append(self.current_test)
        
        if self.logger:
            self.logger.warning(
                f"Test ended: {self.current_test['name']} - "
                f"Status: {status}, Duration: {duration:.1f}s, "
                f"Success Rate: {success_rate:.1f}%"
            )
        
        self.current_test = None
    
    def get_test_report(self, test_index=-1):
        """Get formatted test report.
        
        Args:
            test_index: Index of test to report (-1 for last)
            
        Returns:
            Formatted string report
        """
        if not self.test_results:
            return "No tests run yet"
        
        if test_index < 0:
            test_index = len(self.test_results) + test_index
        
        if test_index < 0 or test_index >= len(self.test_results):
            return "Invalid test index"
        
        test = self.test_results[test_index]
        
        report = []
        report.append("=" * 60)
        report.append(f"Test Report: {test['name']}")
        report.append("=" * 60)
        
        if test['description']:
            report.append(f"Description: {test['description']}")
        
        report.append("")
        report.append("SUMMARY")
        report.append("-" * 60)
        report.append(f"Status:           {test['status']}")
        report.append(f"Started:          {test['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Duration:         {test['duration']:.2f} seconds")
        report.append("")
        
        report.append("TRANSMISSION RESULTS")
        report.append("-" * 60)
        total_files = test['files_sent'] + test['files_failed']
        report.append(f"Files Sent:       {test['files_sent']}")
        report.append(f"Files Failed:     {test['files_failed']}")
        report.append(f"Total Files:      {total_files}")
        report.append(f"Success Rate:     {test['success_rate']:.1f}%")
        report.append("")
        
        report.append("PERFORMANCE")
        report.append("-" * 60)
        report.append(f"Total Data:       {test['total_bytes'] / 1024 / 1024:.2f} MB")
        report.append(f"Throughput:       {test['throughput_mbps']:.2f} MB/s")
        
        if test['duration'] > 0:
            avg_file_time = test['duration'] / total_files if total_files > 0 else 0
            report.append(f"Avg Time/File:    {avg_file_time:.2f} seconds")
        
        report.append("")
        
        if test['errors']:
            report.append("ERRORS")
            report.append("-" * 60)
            for error in test['errors'][:10]:  # Show first 10 errors
                report.append(f"File: {error['file']}")
                report.append(f"  Error: {error['error']}")
            if len(test['errors']) > 10:
                report.append(f"... and {len(test['errors']) - 10} more errors")
            report.append("")
        
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def get_all_tests_summary(self):
        """Get summary of all tests run.
        
        Returns:
            Formatted string summary
        """
        if not self.test_results:
            return "No tests run yet"
        
        report = []
        report.append("=" * 60)
        report.append("All Tests Summary")
        report.append("=" * 60)
        report.append("")
        
        total_sent = 0
        total_failed = 0
        total_bytes = 0
        total_time = 0
        
        for i, test in enumerate(self.test_results, 1):
            total_sent += test['files_sent']
            total_failed += test['files_failed']
            total_bytes += test['total_bytes']
            total_time += test['duration']
            
            report.append(f"{i}. {test['name']}")
            report.append(f"   Status: {test['status']} | "
                         f"Files: {test['files_sent']}/{test['files_sent'] + test['files_failed']} | "
                         f"Rate: {test['success_rate']:.1f}%")
        
        report.append("")
        report.append("-" * 60)
        report.append("TOTAL STATISTICS")
        report.append("-" * 60)
        report.append(f"Total Files Sent: {total_sent}")
        report.append(f"Total Failed:     {total_failed}")
        report.append(f"Total Data:       {total_bytes / 1024 / 1024:.2f} MB")
        report.append(f"Total Time:       {total_time:.2f} seconds")
        
        if total_time > 0:
            overall_throughput = total_bytes / total_time / 1024 / 1024
            report.append(f"Avg Throughput:   {overall_throughput:.2f} MB/s")
        
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def clear_results(self):
        """Clear all test results."""
        self.test_results = []
        self.current_test = None
    
    def export_results(self, filepath):
        """Export test results to file.
        
        Args:
            filepath: Path to export file
            
        Returns:
            True if successful
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("TRANSMISSION TEST RESULTS\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 60 + "\n\n")
                
                for i in range(len(self.test_results)):
                    f.write(self.get_test_report(i))
                    f.write("\n\n")
                
                f.write(self.get_all_tests_summary())
            
            if self.logger:
                self.logger.warning(f"Results exported to: {filepath}")
            
            return True
        except Exception as e:
            if self.logger:
                self.logger.exception(f"Failed to export results: {e}")
            return False
