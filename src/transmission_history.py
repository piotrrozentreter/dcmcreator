"""
Transmission History Tracker.

Maintains a persistent record of all DICOM transmissions with detailed metrics
and provides querying and reporting capabilities.
"""

import os
import json
import sqlite3
from datetime import datetime
from pathlib import Path


class TransmissionHistory:
    """Track and manage DICOM transmission history."""
    
    def __init__(self, db_path=None, logger=None):
        """Initialize transmission history tracker.
        
        Args:
            db_path: Path to SQLite database (creates if not exists)
            logger: Optional logger instance
        """
        self.logger = logger
        
        # Default to ~/.dcmcreator/transmission_history.db
        if db_path is None:
            home = Path.home()
            dcm_dir = home / '.dcmcreator'
            dcm_dir.mkdir(exist_ok=True)
            db_path = dcm_dir / 'transmission_history.db'
        
        self.db_path = str(db_path)
        self._initialize_db()
    
    def _initialize_db(self):
        """Create database schema if not exists."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Transmissions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transmissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    filename TEXT,
                    server_ip TEXT,
                    server_port INTEGER,
                    calling_ae TEXT,
                    called_ae TEXT,
                    success BOOLEAN,
                    bytes_sent INTEGER,
                    duration_seconds REAL,
                    throughput_mbps REAL,
                    error_message TEXT,
                    patient_name TEXT,
                    patient_id TEXT,
                    study_uid TEXT,
                    series_uid TEXT
                )
            ''')
            
            # Batch transmissions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS batch_transmissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    batch_name TEXT,
                    server_ip TEXT,
                    server_port INTEGER,
                    total_files INTEGER,
                    files_sent INTEGER,
                    files_failed INTEGER,
                    total_bytes INTEGER,
                    duration_seconds REAL,
                    avg_throughput_mbps REAL,
                    status TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            
            if self.logger:
                self.logger.debug(f"Transmission history database initialized: {self.db_path}")
        
        except Exception as e:
            if self.logger:
                self.logger.exception(f"Failed to initialize transmission history DB: {e}")
    
    def record_transmission(self,
                          filename=None,
                          server_ip=None,
                          server_port=None,
                          calling_ae=None,
                          called_ae=None,
                          success=False,
                          bytes_sent=0,
                          duration_seconds=0,
                          error_message=None,
                          patient_name=None,
                          patient_id=None,
                          study_uid=None,
                          series_uid=None):
        """Record a single DICOM transmission.
        
        Args:
            filename: Name of transmitted file
            server_ip: Server IP address
            server_port: Server port
            calling_ae: Our AE title
            called_ae: Server AE title
            success: Whether transmission succeeded
            bytes_sent: Number of bytes sent
            duration_seconds: Time taken
            error_message: Error if failed
            patient_name: Patient name
            patient_id: Patient ID
            study_uid: Study UID
            series_uid: Series UID
        """
        try:
            throughput = None
            if success and duration_seconds > 0 and bytes_sent > 0:
                throughput = (bytes_sent / 1024 / 1024) / duration_seconds
            
            timestamp = datetime.now().isoformat()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO transmissions (
                    timestamp, filename, server_ip, server_port,
                    calling_ae, called_ae, success, bytes_sent,
                    duration_seconds, throughput_mbps, error_message,
                    patient_name, patient_id, study_uid, series_uid
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                timestamp, filename, server_ip, server_port,
                calling_ae, called_ae, success, bytes_sent,
                duration_seconds, throughput, error_message,
                patient_name, patient_id, study_uid, series_uid
            ))
            
            conn.commit()
            conn.close()
            
            if self.logger:
                self.logger.warning(
                    f"Transmission recorded: {filename} to {server_ip}:{server_port} - "
                    f"{'SUCCESS' if success else 'FAILED'}"
                )
        
        except Exception as e:
            if self.logger:
                self.logger.exception(f"Failed to record transmission: {e}")
    
    def record_batch_transmission(self,
                                 batch_name,
                                 server_ip,
                                 server_port,
                                 total_files,
                                 files_sent,
                                 files_failed,
                                 total_bytes,
                                 duration_seconds,
                                 status='COMPLETED'):
        """Record a batch transmission event.
        
        Args:
            batch_name: Name of batch
            server_ip: Server IP
            server_port: Server port
            total_files: Total files in batch
            files_sent: Successfully sent
            files_failed: Failed sends
            total_bytes: Total bytes sent
            duration_seconds: Total duration
            status: Batch status
        """
        try:
            avg_throughput = None
            if duration_seconds > 0:
                avg_throughput = (total_bytes / 1024 / 1024) / duration_seconds
            
            timestamp = datetime.now().isoformat()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO batch_transmissions (
                    timestamp, batch_name, server_ip, server_port,
                    total_files, files_sent, files_failed, total_bytes,
                    duration_seconds, avg_throughput_mbps, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                timestamp, batch_name, server_ip, server_port,
                total_files, files_sent, files_failed, total_bytes,
                duration_seconds, avg_throughput, status
            ))
            
            conn.commit()
            conn.close()
            
            if self.logger:
                self.logger.warning(
                    f"Batch transmission recorded: {batch_name} - "
                    f"{files_sent}/{total_files} files sent"
                )
        
        except Exception as e:
            if self.logger:
                self.logger.exception(f"Failed to record batch transmission: {e}")
    
    def get_recent_transmissions(self, limit=50):
        """Get recent transmissions.
        
        Args:
            limit: Maximum number to return
            
        Returns:
            List of transmission records
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM transmissions
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
        
        except Exception as e:
            if self.logger:
                self.logger.exception(f"Failed to get recent transmissions: {e}")
            return []
    
    def get_transmissions_by_server(self, server_ip, server_port=None, limit=100):
        """Get transmissions to specific server.
        
        Args:
            server_ip: Server IP to filter by
            server_port: Optional server port filter
            limit: Maximum records
            
        Returns:
            List of transmission records
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if server_port:
                cursor.execute('''
                    SELECT * FROM transmissions
                    WHERE server_ip = ? AND server_port = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (server_ip, server_port, limit))
            else:
                cursor.execute('''
                    SELECT * FROM transmissions
                    WHERE server_ip = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (server_ip, limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
        
        except Exception as e:
            if self.logger:
                self.logger.exception(f"Failed to get transmissions by server: {e}")
            return []
    
    def get_statistics(self):
        """Get overall transmission statistics.
        
        Returns:
            dict with statistics
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total transmissions
            cursor.execute('SELECT COUNT(*) FROM transmissions')
            total = cursor.fetchone()[0]
            
            # Successful transmissions
            cursor.execute('SELECT COUNT(*) FROM transmissions WHERE success = 1')
            successful = cursor.fetchone()[0]
            
            # Failed transmissions
            cursor.execute('SELECT COUNT(*) FROM transmissions WHERE success = 0')
            failed = cursor.fetchone()[0]
            
            # Total bytes
            cursor.execute('SELECT SUM(bytes_sent) FROM transmissions WHERE success = 1')
            total_bytes = cursor.fetchone()[0] or 0
            
            # Average throughput
            cursor.execute(
                'SELECT AVG(throughput_mbps) FROM transmissions '
                'WHERE success = 1 AND throughput_mbps IS NOT NULL'
            )
            avg_throughput = cursor.fetchone()[0] or 0
            
            conn.close()
            
            success_rate = (successful / total * 100) if total > 0 else 0
            
            return {
                'total_transmissions': total,
                'successful': successful,
                'failed': failed,
                'success_rate': round(success_rate, 1),
                'total_bytes_transferred': total_bytes,
                'total_mb_transferred': round(total_bytes / 1024 / 1024, 2),
                'avg_throughput_mbps': round(avg_throughput, 2)
            }
        
        except Exception as e:
            if self.logger:
                self.logger.exception(f"Failed to get statistics: {e}")
            return {}
    
    def export_to_json(self, filepath, days=None):
        """Export transmission history to JSON file.
        
        Args:
            filepath: Path to export file
            days: Optional - only export last N days
            
        Returns:
            True if successful
        """
        try:
            transmissions = self.get_recent_transmissions(limit=10000)
            
            export = {
                'exported_at': datetime.now().isoformat(),
                'total_records': len(transmissions),
                'transmissions': transmissions,
                'statistics': self.get_statistics()
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export, f, indent=2, default=str)
            
            if self.logger:
                self.logger.warning(f"History exported to {filepath}")
            
            return True
        
        except Exception as e:
            if self.logger:
                self.logger.exception(f"Failed to export history: {e}")
            return False
    
    def clear_old_records(self, days=90):
        """Clear transmission records older than N days.
        
        Args:
            days: Records older than this many days will be deleted
            
        Returns:
            Number of records deleted
        """
        try:
            from datetime import timedelta
            
            cutoff = (datetime.now() - timedelta(days=days)).isoformat()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM transmissions WHERE timestamp < ?', (cutoff,))
            deleted = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            if self.logger:
                self.logger.warning(f"Deleted {deleted} old transmission records")
            
            return deleted
        
        except Exception as e:
            if self.logger:
                self.logger.exception(f"Failed to clear old records: {e}")
            return 0
