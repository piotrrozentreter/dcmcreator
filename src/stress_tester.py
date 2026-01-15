"""
Stress Testing Module for DICOM transmission.

Provides utilities to perform stress tests on DICOM servers with
rapid-fire transmission, sustained load testing, and failure analysis.
"""

import time
import threading
from datetime import datetime


class StressTestRunner:
    """Run stress tests on DICOM transmission infrastructure."""
    
    def __init__(self, logger=None):
        """Initialize stress test runner.
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger
        self.current_test = None
        self.results = []
        self.stop_flag = False
    
    def create_test_plan(self, 
                        name,
                        files_per_second=10,
                        duration_seconds=60,
                        file_size_mb=1.0,
                        concurrent_threads=1):
        """Create a stress test plan.
        
        Args:
            name: Test name
            files_per_second: Target send rate
            duration_seconds: How long to run test
            file_size_mb: Size of each test file
            concurrent_threads: Number of parallel threads
            
        Returns:
            Test plan dict
        """
        # Calculate expected volumes
        total_files = files_per_second * duration_seconds
        total_data_mb = total_files * file_size_mb
        
        plan = {
            'name': name,
            'files_per_second': files_per_second,
            'duration_seconds': duration_seconds,
            'file_size_mb': file_size_mb,
            'concurrent_threads': concurrent_threads,
            'expected_total_files': total_files,
            'expected_total_data_mb': total_data_mb,
            'description': (
                f"Send {files_per_second} files/sec for {duration_seconds}s "
                f"({total_files} total, ~{total_data_mb:.1f} MB)"
            )
        }
        
        if self.logger:
            self.logger.warning(f"Stress test plan created: {name}")
            self.logger.warning(f"  {plan['description']}")
        
        return plan
    
    def start_stress_test(self, plan):
        """Start a stress test execution.
        
        Args:
            plan: Test plan from create_test_plan
            
        Returns:
            Test execution object
        """
        self.current_test = {
            'plan': plan,
            'start_time': datetime.now(),
            'end_time': None,
            'files_sent': 0,
            'files_failed': 0,
            'total_bytes': 0,
            'errors': [],
            'throughput_results': [],
            'status': 'RUNNING'
        }
        
        self.stop_flag = False
        
        if self.logger:
            self.logger.warning(
                f"Stress test started: {plan['name']} at {self.current_test['start_time']}"
            )
        
        return self.current_test
    
    def run_simulation(self):
        """Simulate stress test transmission (non-blocking).
        
        Runs in a separate thread to simulate file transmissions.
        Updates current_test with results as it progresses.
        """
        if not self.current_test:
            return
        
        plan = self.current_test['plan']
        target_fps = plan['files_per_second']
        duration = plan['duration_seconds']
        file_size = plan['file_size_mb']
        
        bytes_per_file = int(file_size * 1024 * 1024)
        start_time = time.time()
        
        while not self.stop_flag:
            elapsed = time.time() - start_time
            
            # Stop if duration exceeded
            if elapsed >= duration:
                break
            
            # Calculate how many files should have been sent by now
            expected_files = int(elapsed * target_fps)
            sent_files = self.current_test['files_sent'] + self.current_test['files_failed']
            
            # Send files up to expected count
            while sent_files < expected_files and not self.stop_flag:
                # Simulate transmission time (typically 90-110% of ideal time)
                ideal_time = 1.0 / target_fps
                actual_time = ideal_time * (0.9 + (0.2 * (hash(time.time()) % 100) / 100))
                
                time.sleep(actual_time * 0.1)  # Simulate network latency
                
                # Record as successful (95% success rate simulation)
                success = (hash(sent_files) % 100) < 95
                
                if success:
                    self.record_file_sent(bytes_per_file, success=True, time_taken=actual_time)
                else:
                    self.record_file_sent(
                        0, 
                        success=False, 
                        error=f"Simulated transmission error for file {sent_files + 1}",
                        time_taken=actual_time
                    )
                
                sent_files += 1
            
            # Small sleep to prevent CPU spinning
            time.sleep(0.01)
        
        # End the test
        self.end_stress_test('COMPLETED' if not self.stop_flag else 'INTERRUPTED')
    
    def record_file_sent(self, bytes_sent, success=True, error=None, time_taken=0):
        """Record result of a file transmission during stress test.
        
        Args:
            bytes_sent: Number of bytes transmitted
            success: Boolean indicating success
            error: Error message if failed
            time_taken: Time taken in seconds
        """
        if not self.current_test:
            return
        
        if success:
            self.current_test['files_sent'] += 1
            self.current_test['total_bytes'] += bytes_sent
            
            # Calculate throughput for this file
            if time_taken > 0:
                mbps = (bytes_sent / 1024 / 1024) / time_taken
                self.current_test['throughput_results'].append(mbps)
        else:
            self.current_test['files_failed'] += 1
            if error:
                self.current_test['errors'].append({
                    'error': error,
                    'timestamp': datetime.now()
                })
    
    def end_stress_test(self, status='COMPLETED'):
        """End current stress test.
        
        Args:
            status: Final status (COMPLETED, INTERRUPTED, FAILED)
        """
        if not self.current_test:
            return None
        
        self.current_test['end_time'] = datetime.now()
        self.current_test['status'] = status
        
        # Calculate statistics
        duration = (self.current_test['end_time'] - 
                   self.current_test['start_time']).total_seconds()
        
        total_files = (self.current_test['files_sent'] + 
                      self.current_test['files_failed'])
        
        stats = {
            'duration_seconds': duration,
            'files_sent': self.current_test['files_sent'],
            'files_failed': self.current_test['files_failed'],
            'total_files': total_files,
            'success_rate': (
                self.current_test['files_sent'] / total_files * 100 
                if total_files > 0 else 0
            ),
            'total_bytes': self.current_test['total_bytes'],
            'avg_throughput_mbps': None,
            'peak_throughput_mbps': None,
            'min_throughput_mbps': None,
            'files_per_second': None
        }
        
        # Calculate throughput statistics
        if self.current_test['throughput_results']:
            import statistics
            results = self.current_test['throughput_results']
            stats['avg_throughput_mbps'] = round(statistics.mean(results), 2)
            stats['peak_throughput_mbps'] = round(max(results), 2)
            stats['min_throughput_mbps'] = round(min(results), 2)
        
        # Calculate files per second
        if duration > 0:
            stats['files_per_second'] = round(
                self.current_test['files_sent'] / duration, 2
            )
        
        self.current_test.update(stats)
        self.results.append(self.current_test)
        
        if self.logger:
            self.logger.warning(
                f"Stress test ended: {self.current_test['plan']['name']} - "
                f"Status: {status}, Files: {total_files}, Success: {stats['success_rate']:.1f}%"
            )
        
        return self.current_test
    
    def get_stress_test_report(self, test_index=-1):
        """Get formatted report for a stress test.
        
        Args:
            test_index: Index of test (-1 for last)
            
        Returns:
            Formatted string report
        """
        if not self.results:
            return "No stress tests run yet"
        
        if test_index < 0:
            test_index = len(self.results) + test_index
        
        if test_index < 0 or test_index >= len(self.results):
            return "Invalid test index"
        
        test = self.results[test_index]
        plan = test['plan']
        
        report = []
        report.append("=" * 70)
        report.append(f"STRESS TEST REPORT: {plan['name']}")
        report.append("=" * 70)
        report.append("")
        
        report.append("TEST CONFIGURATION")
        report.append("-" * 70)
        report.append(f"Files/Second Target:   {plan['files_per_second']}")
        report.append(f"Duration:              {plan['duration_seconds']} seconds")
        report.append(f"File Size:             {plan['file_size_mb']} MB")
        report.append(f"Concurrent Threads:    {plan['concurrent_threads']}")
        report.append(f"Expected Data Volume:  {plan['expected_total_data_mb']:.1f} MB")
        report.append("")
        
        report.append("TEST RESULTS")
        report.append("-" * 70)
        report.append(f"Status:                {test['status']}")
        report.append(f"Start Time:            {test['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Duration:              {test['duration_seconds']:.2f} seconds")
        report.append("")
        
        report.append("TRANSMISSION STATISTICS")
        report.append("-" * 70)
        report.append(f"Files Sent:            {test['files_sent']}")
        report.append(f"Files Failed:          {test['files_failed']}")
        report.append(f"Total Files:           {test['total_files']}")
        report.append(f"Success Rate:          {test['success_rate']:.1f}%")
        report.append(f"Files/Second Actual:   {test['files_per_second']:.2f}")
        report.append("")
        
        report.append("THROUGHPUT ANALYSIS")
        report.append("-" * 70)
        report.append(f"Total Data Sent:       {test['total_bytes'] / 1024 / 1024:.2f} MB")
        if test['avg_throughput_mbps']:
            report.append(f"Average Throughput:    {test['avg_throughput_mbps']:.2f} MB/s")
            report.append(f"Peak Throughput:       {test['peak_throughput_mbps']:.2f} MB/s")
            report.append(f"Minimum Throughput:    {test['min_throughput_mbps']:.2f} MB/s")
        report.append("")
        
        if test['errors']:
            report.append("ERRORS")
            report.append("-" * 70)
            for error in test['errors'][:10]:
                report.append(f"* {error['error']}")
            if len(test['errors']) > 10:
                report.append(f"... and {len(test['errors']) - 10} more errors")
            report.append("")
        
        report.append("=" * 70)
        
        return "\n".join(report)
    
    def get_all_stress_tests_summary(self):
        """Get summary of all stress tests run.
        
        Returns:
            Formatted string summary
        """
        if not self.results:
            return "No stress tests run yet"
        
        report = []
        report.append("=" * 70)
        report.append("ALL STRESS TESTS SUMMARY")
        report.append("=" * 70)
        report.append("")
        
        for i, test in enumerate(self.results, 1):
            report.append(f"{i}. {test['plan']['name']}")
            report.append(
                f"   Status: {test['status']} | "
                f"Files: {test['files_sent']}/{test['total_files']} | "
                f"Success: {test['success_rate']:.1f}% | "
                f"Throughput: {test['avg_throughput_mbps'] or 'N/A'} MB/s"
            )
        
        report.append("")
        report.append("-" * 70)
        report.append("TOTAL STATISTICS")
        report.append("-" * 70)
        
        total_tests = len(self.results)
        total_files = sum(t['total_files'] for t in self.results)
        total_sent = sum(t['files_sent'] for t in self.results)
        total_failed = sum(t['files_failed'] for t in self.results)
        total_bytes = sum(t['total_bytes'] for t in self.results)
        total_time = sum(t['duration_seconds'] for t in self.results)
        
        report.append(f"Total Tests Run:       {total_tests}")
        report.append(f"Total Files Sent:      {total_sent}")
        report.append(f"Total Failed:          {total_failed}")
        report.append(f"Total Data:            {total_bytes / 1024 / 1024:.2f} MB")
        report.append(f"Total Time:            {total_time:.2f} seconds")
        
        if total_time > 0:
            overall_throughput = total_bytes / total_time / 1024 / 1024
            report.append(f"Overall Throughput:    {overall_throughput:.2f} MB/s")
        
        report.append("=" * 70)
        
        return "\n".join(report)
    
    def request_stop(self):
        """Request stress test to stop gracefully."""
        self.stop_flag = True
        if self.logger:
            self.logger.warning("Stress test stop requested")
    
    def is_running(self):
        """Check if a stress test is currently running."""
        return self.current_test and self.current_test['status'] == 'RUNNING'
