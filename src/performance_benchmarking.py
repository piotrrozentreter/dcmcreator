"""
Performance Benchmarking Module.

Provides utilities to benchmark DICOM transmission performance and
generate comprehensive performance reports.
"""

import time
from datetime import datetime


class PerformanceBenchmark:
    """Run and analyze performance benchmarks for DICOM transmission."""
    
    def __init__(self, logger=None):
        """Initialize performance benchmarking.
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger
        self.benchmarks = []
    
    def run_file_size_benchmark(self, send_function, sizes_mb=None, iterations=3):
        """Benchmark transmission performance with different file sizes.
        
        Args:
            send_function: Callable that takes (size_mb) and returns bytes_sent, time_taken
            sizes_mb: List of sizes to test (default: [0.5, 1, 2, 5, 10])
            iterations: Number of iterations per size
            
        Returns:
            Benchmark result dict
        """
        if sizes_mb is None:
            sizes_mb = [0.5, 1.0, 2.0, 5.0, 10.0]
        
        result = {
            'benchmark_type': 'FILE_SIZE',
            'timestamp': datetime.now().isoformat(),
            'sizes_tested': sizes_mb,
            'iterations': iterations,
            'results_by_size': {},
            'summary': None
        }
        
        for size_mb in sizes_mb:
            times = []
            throughputs = []
            
            for _ in range(iterations):
                try:
                    bytes_sent, time_taken = send_function(size_mb)
                    times.append(time_taken)
                    
                    if time_taken > 0:
                        mbps = (bytes_sent / 1024 / 1024) / time_taken
                        throughputs.append(mbps)
                except Exception as e:
                    if self.logger:
                        self.logger.exception(f"Benchmark iteration failed: {e}")
            
            if times and throughputs:
                import statistics
                
                result['results_by_size'][size_mb] = {
                    'avg_time': round(statistics.mean(times), 3),
                    'min_time': round(min(times), 3),
                    'max_time': round(max(times), 3),
                    'avg_throughput': round(statistics.mean(throughputs), 2),
                    'peak_throughput': round(max(throughputs), 2),
                    'min_throughput': round(min(throughputs), 2)
                }
        
        self.benchmarks.append(result)
        return result
    
    def run_latency_benchmark(self, ping_function, iterations=10):
        """Benchmark server latency and connection quality.
        
        Args:
            ping_function: Callable that returns latency in ms
            iterations: Number of pings
            
        Returns:
            Benchmark result dict
        """
        result = {
            'benchmark_type': 'LATENCY',
            'timestamp': datetime.now().isoformat(),
            'iterations': iterations,
            'latencies_ms': [],
            'statistics': {}
        }
        
        latencies = []
        
        for _ in range(iterations):
            try:
                latency = ping_function()
                if latency is not None:
                    latencies.append(latency)
                    result['latencies_ms'].append(latency)
            except Exception as e:
                if self.logger:
                    self.logger.exception(f"Latency ping failed: {e}")
        
        if latencies:
            import statistics
            
            result['statistics'] = {
                'min_ms': round(min(latencies), 2),
                'max_ms': round(max(latencies), 2),
                'avg_ms': round(statistics.mean(latencies), 2),
                'std_dev_ms': round(statistics.stdev(latencies), 2) if len(latencies) > 1 else 0,
                'successful_pings': len(latencies),
                'failed_pings': iterations - len(latencies)
            }
        
        self.benchmarks.append(result)
        return result
    
    def run_throughput_benchmark(self, send_batch_function, num_files, file_size_mb):
        """Benchmark throughput over multiple files.
        
        Args:
            send_batch_function: Callable that takes (num_files, file_size_mb) 
                                and returns (total_bytes, total_time)
            num_files: Number of files to send
            file_size_mb: Size of each file
            
        Returns:
            Benchmark result dict
        """
        result = {
            'benchmark_type': 'THROUGHPUT',
            'timestamp': datetime.now().isoformat(),
            'configuration': {
                'num_files': num_files,
                'file_size_mb': file_size_mb,
                'expected_total_mb': num_files * file_size_mb
            },
            'measurements': []
        }
        
        try:
            total_bytes, total_time = send_batch_function(num_files, file_size_mb)
            
            total_mb = total_bytes / 1024 / 1024
            avg_mbps = total_mb / total_time if total_time > 0 else 0
            
            result['measurements'] = {
                'total_bytes_sent': total_bytes,
                'total_mb_sent': round(total_mb, 2),
                'total_time_seconds': round(total_time, 2),
                'avg_throughput_mbps': round(avg_mbps, 2),
                'files_per_second': round(num_files / total_time, 2) if total_time > 0 else 0
            }
        
        except Exception as e:
            if self.logger:
                self.logger.exception(f"Throughput benchmark failed: {e}")
        
        self.benchmarks.append(result)
        return result
    
    def compare_benchmarks(self, benchmark_indices=None):
        """Compare multiple benchmarks.
        
        Args:
            benchmark_indices: List of benchmark indices to compare (None = all)
            
        Returns:
            Comparison report dict
        """
        if benchmark_indices is None:
            benchmarks = self.benchmarks
        else:
            benchmarks = [self.benchmarks[i] for i in benchmark_indices 
                         if 0 <= i < len(self.benchmarks)]
        
        if not benchmarks:
            return None
        
        # Group by type
        by_type = {}
        for bench in benchmarks:
            btype = bench['benchmark_type']
            if btype not in by_type:
                by_type[btype] = []
            by_type[btype].append(bench)
        
        comparison = {
            'timestamp': datetime.now().isoformat(),
            'benchmarks_compared': len(benchmarks),
            'by_type': by_type,
            'summary': f"Compared {len(benchmarks)} benchmarks across {len(by_type)} types"
        }
        
        return comparison
    
    def get_benchmark_report(self, benchmark_index):
        """Get formatted report for a benchmark.
        
        Args:
            benchmark_index: Index of benchmark
            
        Returns:
            Formatted string report
        """
        if benchmark_index < 0 or benchmark_index >= len(self.benchmarks):
            return "Invalid benchmark index"
        
        bench = self.benchmarks[benchmark_index]
        report = []
        
        report.append("=" * 70)
        report.append(f"PERFORMANCE BENCHMARK REPORT - {bench['benchmark_type']}")
        report.append("=" * 70)
        report.append("")
        report.append(f"Timestamp: {bench['timestamp']}")
        report.append("")
        
        if bench['benchmark_type'] == 'FILE_SIZE':
            report.append("FILE SIZE PERFORMANCE ANALYSIS")
            report.append("-" * 70)
            
            for size, metrics in bench['results_by_size'].items():
                report.append(f"\n{size} MB Files:")
                report.append(f"  Time:       {metrics['avg_time']:.3f}s "
                            f"(min: {metrics['min_time']:.3f}s, "
                            f"max: {metrics['max_time']:.3f}s)")
                report.append(f"  Throughput: {metrics['avg_throughput']:.2f} MB/s "
                            f"(peak: {metrics['peak_throughput']:.2f} MB/s)")
        
        elif bench['benchmark_type'] == 'LATENCY':
            report.append("LATENCY ANALYSIS")
            report.append("-" * 70)
            
            stats = bench['statistics']
            report.append(f"Minimum:        {stats['min_ms']} ms")
            report.append(f"Maximum:        {stats['max_ms']} ms")
            report.append(f"Average:        {stats['avg_ms']} ms")
            report.append(f"Std Deviation:  {stats['std_dev_ms']} ms")
            report.append(f"Successful:     {stats['successful_pings']}/{bench['iterations']}")
        
        elif bench['benchmark_type'] == 'THROUGHPUT':
            report.append("THROUGHPUT ANALYSIS")
            report.append("-" * 70)
            
            config = bench['configuration']
            report.append(f"Configuration:")
            report.append(f"  Files:            {config['num_files']}")
            report.append(f"  Size per file:    {config['file_size_mb']} MB")
            report.append(f"  Expected total:   {config['expected_total_mb']} MB")
            report.append("")
            
            if bench['measurements']:
                m = bench['measurements']
                report.append(f"Results:")
                report.append(f"  Total sent:       {m['total_mb_sent']} MB")
                report.append(f"  Time:             {m['total_time_seconds']} seconds")
                report.append(f"  Throughput:       {m['avg_throughput_mbps']} MB/s")
                report.append(f"  Files/Second:     {m['files_per_second']}")
        
        report.append("")
        report.append("=" * 70)
        
        return "\n".join(report)
    
    def get_all_benchmarks_summary(self):
        """Get summary of all benchmarks.
        
        Returns:
            Formatted string summary
        """
        if not self.benchmarks:
            return "No benchmarks run yet"
        
        report = []
        report.append("=" * 70)
        report.append("ALL BENCHMARKS SUMMARY")
        report.append("=" * 70)
        report.append("")
        
        # Group by type
        by_type = {}
        for bench in self.benchmarks:
            btype = bench['benchmark_type']
            if btype not in by_type:
                by_type[btype] = []
            by_type[btype].append(bench)
        
        for btype, benches in by_type.items():
            report.append(f"{btype} Benchmarks: {len(benches)}")
            
            for i, bench in enumerate(benches, 1):
                if btype == 'FILE_SIZE':
                    avg_throughputs = [
                        m['avg_throughput'] 
                        for m in bench['results_by_size'].values()
                    ]
                    if avg_throughputs:
                        report.append(
                            f"  {i}. Avg throughput: "
                            f"{sum(avg_throughputs)/len(avg_throughputs):.2f} MB/s"
                        )
                elif btype == 'LATENCY':
                    avg = bench['statistics'].get('avg_ms', 'N/A')
                    report.append(f"  {i}. Avg latency: {avg} ms")
                elif btype == 'THROUGHPUT':
                    avg_mbps = bench['measurements'].get('avg_throughput_mbps', 'N/A')
                    report.append(f"  {i}. Throughput: {avg_mbps} MB/s")
        
        report.append("")
        report.append("=" * 70)
        
        return "\n".join(report)
    
    def clear_benchmarks(self):
        """Clear all benchmark results."""
        self.benchmarks = []
        if self.logger:
            self.logger.warning("All benchmarks cleared")
