"""
Business logic and test execution methods for DICOM Creator.
Separated from GUI code for better maintainability and testability.
"""

import os
import threading
import socket
import json


class DicomLogicHandler:
    """Handles business logic, data processing, and test execution."""
    
    def __init__(self, logger, image_vars=None, pixel_array=None):
        """Initialize logic handler."""
        self.logger = logger
        self.pixel_array = pixel_array
        self.image_vars = image_vars or {}
        
    # ============ IMAGE OPERATIONS ============
    
    def process_image_to_uint8(self, arr):
        """Normalize arbitrary numeric array to uint8 [0,255] range for display."""
        import numpy as np
        
        if arr.dtype == np.uint8:
            return arr
        a = arr.astype(np.float32)
        mn = np.min(a)
        mx = np.max(a)
        if mx - mn > 1e-5:
            a = (a - mn) / (mx - mn) * 255.0
        else:
            a = np.zeros_like(a) if not np.any(a) else np.full_like(a, 255)
        return a.astype(np.uint8)
    
    # ============ CONNECTION TESTING ============
    
    def test_tcp_connection(self, server, port, timeout=5):
        """Test TCP connection to server."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((server, port))
            sock.close()
            return {
                'success': result == 0,
                'error': None if result == 0 else f"Connection failed (errno {result})"
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # ============ CONFIG FILE OPERATIONS ============
    
    def save_config_to_file(self, filename, config_data):
        """Save configuration dictionary to JSON file."""
        try:
            with open(filename, "w") as f:
                json.dump(config_data, f, indent=2)
            return True, f"Saved to {filename}"
        except Exception as e:
            self.logger.exception(f"Failed to save config to {filename}")
            return False, str(e)
    
    def load_config_from_file(self, filename):
        """Load configuration dictionary from JSON file."""
        try:
            if not os.path.exists(filename):
                return None, f"File not found: {filename}"
            with open(filename, "r") as f:
                return json.load(f), None
        except Exception as e:
            self.logger.exception(f"Failed to load config from {filename}")
            return None, str(e)
    
    # ============ DATA VALIDATION ============
    
    def validate_server_config(self, server, port_str, patient_id=""):
        """Validate server configuration values."""
        errors = []
        
        if not server or not server.strip():
            errors.append("Server address is required")
        
        try:
            port = int(port_str)
            if port < 1 or port > 65535:
                errors.append("Port must be between 1 and 65535")
        except ValueError:
            errors.append("Port must be a valid integer")
        
        return len(errors) == 0, errors
    
    # ============ FILE OPERATIONS ============
    
    def get_file_info(self, file_path):
        """Get file information (size, exists, etc)."""
        try:
            if not os.path.exists(file_path):
                return None, "File does not exist"
            
            size = os.path.getsize(file_path)
            return {
                'path': file_path,
                'size': size,
                'size_mb': size / (1024 * 1024),
                'exists': True
            }, None
        except Exception as e:
            return None, str(e)
    
    def find_files_in_directory(self, directory, extensions=None):
        """Find files in directory with optional extension filter."""
        if not os.path.isdir(directory):
            return [], f"Not a directory: {directory}"
        
        try:
            files = []
            for root, dirs, filenames in os.walk(directory):
                for filename in filenames:
                    if extensions is None or any(filename.lower().endswith(ext.lower()) for ext in extensions):
                        files.append(os.path.join(root, filename))
            return files, None
        except Exception as e:
            return [], str(e)
    
    # ============ STRESS TEST HELPERS ============
    
    def calculate_stress_test_params(self, files_per_second, duration_seconds, file_size_mb, workers):
        """Calculate stress test parameters."""
        total_files = files_per_second * duration_seconds
        total_mb = total_files * file_size_mb
        
        return {
            'total_files': total_files,
            'total_mb': total_mb,
            'files_per_second': files_per_second,
            'duration_seconds': duration_seconds,
            'file_size_mb': file_size_mb,
            'workers': workers,
            'mb_per_second': total_mb / duration_seconds if duration_seconds > 0 else 0
        }
    
    # ============ REPORT GENERATION ============
    
    def generate_connection_test_report(self, test_results):
        """Generate formatted connection test report."""
        report = "Connection Test Report\n"
        report += "=" * 60 + "\n\n"
        
        for test_name, result in test_results.items():
            report += f"{test_name}:\n"
            if isinstance(result, dict):
                for key, value in result.items():
                    report += f"  {key}: {value}\n"
            else:
                report += f"  {result}\n"
            report += "\n"
        
        return report
    
    # ============ ERROR HANDLING ============
    
    def format_error_message(self, error, context=""):
        """Format error message for display."""
        msg = f"Error"
        if context:
            msg += f" ({context})"
        msg += f": {error}"
        return msg
    
    # ============ STRESS TEST EXECUTION ============
    
    def run_stress_test_simulation(self, stress_runner, on_complete_callback, on_error_callback):
        """Run stress test simulation in a background thread.
        
        Args:
            stress_runner: StressTestRunner instance
            on_complete_callback: Callable(report_string) when test completes
            on_error_callback: Callable(error_string) on error
        """
        def test_worker():
            try:
                stress_runner.run_simulation()
                report = stress_runner.get_stress_test_report()
                on_complete_callback(report)
            except Exception as e:
                on_error_callback(str(e))
        
        import threading
        t = threading.Thread(target=test_worker, daemon=True)
        t.start()
    
    # ============ VR XML PARSING ============
    
    def parse_vr_xml(self, vr_file_path):
        """Parse VR.xml file and return structured data.
        
        Args:
            vr_file_path: Path to VR.xml file
            
        Returns:
            tuple: (success, data_or_error_msg)
                - success=True: data is list of dicts with keys: tag, name, keyword, vr, vm, status, is_retired
                - success=False: data is error message string
        """
        try:
            import xml.etree.ElementTree as ET
            
            if not os.path.exists(vr_file_path):
                return False, f"VR.xml not found at: {vr_file_path}"
            
            # Parse XML
            tree = ET.parse(vr_file_path)
            root = tree.getroot()
            
            # Define namespaces (including xml namespace for xml:id attribute)
            ns = {
                'd': 'http://docbook.org/ns/docbook',
                'xml': 'http://www.w3.org/XML/1998/namespace'
            }
            
            # Helper function to extract cell text
            def get_cell_text(cell):
                if cell is None:
                    return ""
                # Try to find emphasis first
                emphasis = cell.find('.//d:emphasis', ns)
                if emphasis is not None and emphasis.text:
                    return emphasis.text.strip()
                # Otherwise get direct text
                para = cell.find('.//d:para', ns)
                if para is not None:
                    return (para.text or "").strip()
                return (cell.text or "").strip()
            
            # Extract data from table
            vr_data = []
            for table in root.findall('.//d:table[@xml:id="table_6-1"]', ns):
                tbody = table.find('.//d:tbody', ns)
                if tbody is not None:
                    for row in tbody.findall('d:tr', ns):
                        try:
                            cells = row.findall('d:td', ns)
                            if len(cells) >= 5:
                                # Extract text from each cell
                                tag = get_cell_text(cells[0])
                                name = get_cell_text(cells[1])
                                keyword = get_cell_text(cells[2])
                                vr = get_cell_text(cells[3])
                                vm = get_cell_text(cells[4])
                                status = get_cell_text(cells[5]) if len(cells) > 5 else ""
                                
                                # Skip empty rows
                                if not tag or not name:
                                    continue
                                
                                # Determine if retired based on status or emphasis
                                is_retired = "RET" in status or any(
                                    cell.find('.//d:emphasis', ns) is not None 
                                    for cell in cells[:5]
                                )
                                
                                # Clean up status text
                                if is_retired and not status:
                                    status = "RET"
                                
                                vr_data.append({
                                    'tag': tag,
                                    'name': name,
                                    'keyword': keyword,
                                    'vr': vr,
                                    'vm': vm,
                                    'status': status,
                                    'is_retired': is_retired
                                })
                        except Exception as e:
                            self.logger.debug(f"Error parsing VR row: {e}")
                            continue
            
            return True, vr_data
            
        except Exception as e:
            error_msg = f"Failed to parse VR.xml: {e}"
            self.logger.exception("VR XML parsing error")
            return False, error_msg