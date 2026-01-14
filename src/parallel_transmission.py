"""
Parallel Transmission Module.

Provides multi-threaded transmission of DICOM files to maximize throughput
and reduce total transmission time.
"""

import threading
import queue
import time
from datetime import datetime


class ParallelTransmissionManager:
    """Manage parallel DICOM transmissions using multiple threads."""
    
    def __init__(self, logger=None, max_workers=3):
        """Initialize parallel transmission manager.
        
        Args:
            logger: Optional logger instance
            max_workers: Maximum number of concurrent transmission threads
        """
        self.logger = logger
        self.max_workers = max(1, min(max_workers, 10))  # Clamp between 1-10
        
        self.work_queue = queue.Queue()
        self.result_queue = queue.Queue()
        self.workers = []
        self.running = False
        self.current_session = None
    
    def start_session(self, name="Parallel Transmission"):
        """Start a new parallel transmission session.
        
        Args:
            name: Name of the session
            
        Returns:
            Session object
        """
        self.current_session = {
            'name': name,
            'start_time': datetime.now(),
            'end_time': None,
            'total_queued': 0,
            'total_completed': 0,
            'total_successful': 0,
            'total_failed': 0,
            'total_bytes': 0,
            'results': [],
            'status': 'RUNNING'
        }
        
        self.running = True
        self._start_workers()
        
        if self.logger:
            self.logger.warning(
                f"Parallel transmission session started: {name} "
                f"(workers: {self.max_workers})"
            )
        
        return self.current_session
    
    def _start_workers(self):
        """Start worker threads."""
        for i in range(self.max_workers):
            worker = threading.Thread(
                target=self._worker_loop,
                name=f"TransmissionWorker-{i}",
                daemon=True
            )
            worker.start()
            self.workers.append(worker)
    
    def _worker_loop(self):
        """Worker thread main loop."""
        while self.running:
            try:
                # Get work item with timeout
                job = self.work_queue.get(timeout=1)
                
                if job is None:  # Poison pill to stop
                    break
                
                result = self._execute_transmission(job)
                self.result_queue.put(result)
                
                # Update session stats
                if self.current_session:
                    self.current_session['total_completed'] += 1
                    if result['success']:
                        self.current_session['total_successful'] += 1
                        self.current_session['total_bytes'] += result.get('bytes_sent', 0)
                    else:
                        self.current_session['total_failed'] += 1
                    
                    self.current_session['results'].append(result)
                
                self.work_queue.task_done()
            
            except queue.Empty:
                continue
            except Exception as e:
                if self.logger:
                    self.logger.exception(f"Worker error: {e}")
    
    def _execute_transmission(self, job):
        """Execute a transmission job.
        
        Args:
            job: dict with keys: 'send_function', 'file_info', etc.
            
        Returns:
            Result dict
        """
        result = {
            'file_info': job.get('file_info'),
            'success': False,
            'bytes_sent': 0,
            'duration_seconds': 0,
            'throughput_mbps': None,
            'error': None,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            send_func = job.get('send_function')
            file_path = job.get('file_path')
            
            start_time = time.time()
            
            # Call the transmission function
            bytes_sent = send_func(file_path) if file_path else 0
            
            duration = time.time() - start_time
            
            result['success'] = True
            result['bytes_sent'] = bytes_sent
            result['duration_seconds'] = round(duration, 2)
            
            if duration > 0:
                result['throughput_mbps'] = round(
                    (bytes_sent / 1024 / 1024) / duration, 2
                )
        
        except Exception as e:
            result['success'] = False
            result['error'] = str(e)
            if self.logger:
                self.logger.exception(f"Transmission job failed: {e}")
        
        return result
    
    def queue_transmission(self, file_path, send_function, file_info=None):
        """Queue a file for transmission.
        
        Args:
            file_path: Path to DICOM file
            send_function: Callable that transmits the file
            file_info: Optional metadata dict
            
        Returns:
            True if queued successfully
        """
        try:
            job = {
                'file_path': file_path,
                'send_function': send_function,
                'file_info': file_info or {}
            }
            
            self.work_queue.put(job)
            
            if self.current_session:
                self.current_session['total_queued'] += 1
            
            return True
        
        except Exception as e:
            if self.logger:
                self.logger.exception(f"Failed to queue transmission: {e}")
            return False
    
    def queue_batch(self, file_paths, send_function):
        """Queue multiple files for transmission.
        
        Args:
            file_paths: List of file paths
            send_function: Callable for transmission
            
        Returns:
            Number of files queued
        """
        count = 0
        for file_path in file_paths:
            if self.queue_transmission(file_path, send_function):
                count += 1
        
        if self.logger:
            self.logger.warning(f"Queued {count} files for parallel transmission")
        
        return count
    
    def wait_for_completion(self, timeout=None):
        """Wait for all queued transmissions to complete.
        
        Args:
            timeout: Timeout in seconds (None = wait forever)
            
        Returns:
            True if all completed, False if timeout
        """
        try:
            self.work_queue.join()
            return True
        except Exception:
            return False
    
    def stop_session(self):
        """Stop current parallel transmission session.
        
        Returns:
            Session summary dict
        """
        self.running = False
        
        # Send poison pills to stop workers
        for _ in range(self.max_workers):
            try:
                self.work_queue.put(None, timeout=1)
            except queue.Full:
                pass
        
        if self.current_session:
            self.current_session['end_time'] = datetime.now()
            self.current_session['status'] = 'COMPLETED'
            
            duration = (
                self.current_session['end_time'] - 
                self.current_session['start_time']
            ).total_seconds()
            
            session = self.current_session.copy()
            session['duration_seconds'] = round(duration, 2)
            
            if duration > 0:
                session['files_per_second'] = round(
                    self.current_session['total_completed'] / duration, 2
                )
            
            if self.logger:
                self.logger.warning(
                    f"Parallel transmission session ended: {session['name']} - "
                    f"Success: {session['total_successful']}, "
                    f"Failed: {session['total_failed']}"
                )
            
            return session
        
        return None
    
    def get_progress(self):
        """Get current progress of transmission session.
        
        Returns:
            dict with progress information
        """
        if not self.current_session:
            return None
        
        return {
            'name': self.current_session['name'],
            'queued': self.current_session['total_queued'],
            'completed': self.current_session['total_completed'],
            'successful': self.current_session['total_successful'],
            'failed': self.current_session['total_failed'],
            'bytes_transferred': self.current_session['total_bytes'],
            'pending': self.current_session['total_queued'] - self.current_session['total_completed']
        }
    
    def get_session_report(self):
        """Get formatted report of current or last session.
        
        Returns:
            Formatted string report
        """
        if not self.current_session:
            return "No parallel transmission session active"
        
        session = self.current_session
        report = []
        
        report.append("=" * 70)
        report.append(f"PARALLEL TRANSMISSION REPORT - {session['name']}")
        report.append("=" * 70)
        report.append("")
        
        report.append("CONFIGURATION")
        report.append("-" * 70)
        report.append(f"Worker Threads:        {self.max_workers}")
        report.append(f"Status:                {session['status']}")
        report.append("")
        
        report.append("TRANSMISSION RESULTS")
        report.append("-" * 70)
        report.append(f"Total Queued:          {session['total_queued']}")
        report.append(f"Completed:             {session['total_completed']}")
        report.append(f"Successful:            {session['total_successful']}")
        report.append(f"Failed:                {session['total_failed']}")
        
        if session['total_completed'] > 0:
            success_rate = (
                session['total_successful'] / session['total_completed'] * 100
            )
            report.append(f"Success Rate:          {success_rate:.1f}%")
        
        report.append("")
        
        report.append("PERFORMANCE")
        report.append("-" * 70)
        report.append(
            f"Total Data:            "
            f"{session['total_bytes'] / 1024 / 1024:.2f} MB"
        )
        
        if session['end_time']:
            duration = (
                session['end_time'] - session['start_time']
            ).total_seconds()
            report.append(f"Duration:              {duration:.2f} seconds")
            
            if duration > 0:
                throughput = (
                    session['total_bytes'] / 1024 / 1024 / duration
                )
                report.append(f"Average Throughput:    {throughput:.2f} MB/s")
                
                files_per_sec = session['total_completed'] / duration
                report.append(f"Files/Second:          {files_per_sec:.2f}")
        
        report.append("")
        report.append("=" * 70)
        
        return "\n".join(report)
    
    def get_worker_status(self):
        """Get status of worker threads.
        
        Returns:
            dict with worker information
        """
        return {
            'max_workers': self.max_workers,
            'active_workers': len([w for w in self.workers if w.is_alive()]),
            'running': self.running,
            'queue_size': self.work_queue.qsize()
        }
