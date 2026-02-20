"""
DICOM Query/Retrieve Module - C-FIND Implementation
Provides patient/study/series search capabilities against remote PACS.
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from dataclasses import dataclass

try:
    from pynetdicom import AE, evt, debug_logger
    from pynetdicom.sop_class import (
        PatientRootQueryRetrieveInformationModelFind,
        StudyRootQueryRetrieveInformationModelFind,
    )
    from pydicom.dataset import Dataset
    PYNETDICOM_AVAILABLE = True
except ImportError:
    PYNETDICOM_AVAILABLE = False
    AE = None
    Dataset = None


@dataclass
class QueryResult:
    """Represents a single C-FIND query result."""
    level: str  # PATIENT, STUDY, SERIES, IMAGE
    patient_id: str = ""
    patient_name: str = ""
    patient_birth_date: str = ""
    patient_sex: str = ""
    study_uid: str = ""
    study_date: str = ""
    study_time: str = ""
    study_description: str = ""
    accession_number: str = ""
    modality: str = ""
    series_uid: str = ""
    series_number: str = ""
    series_description: str = ""
    num_instances: int = 0
    sop_instance_uid: str = ""
    
    # Store the full dataset for detailed inspection
    dataset: Optional[Any] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for display."""
        return {
            'level': self.level,
            'patient_id': self.patient_id,
            'patient_name': self.patient_name,
            'patient_birth_date': self.patient_birth_date,
            'patient_sex': self.patient_sex,
            'study_uid': self.study_uid,
            'study_date': self.study_date,
            'study_time': self.study_time,
            'study_description': self.study_description,
            'accession_number': self.accession_number,
            'modality': self.modality,
            'series_uid': self.series_uid,
            'series_number': self.series_number,
            'series_description': self.series_description,
            'num_instances': self.num_instances,
            'sop_instance_uid': self.sop_instance_uid,
        }


class DicomQueryHandler:
    """
    Handles DICOM C-FIND queries to remote PACS servers.
    
    Supports Patient Root and Study Root query models at multiple levels:
    - PATIENT level: Search for patients
    - STUDY level: Search for studies
    - SERIES level: Search for series within studies
    - IMAGE level: Search for individual instances
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize the query handler.
        
        Args:
            logger: Logger instance for diagnostic output
        """
        self.logger = logger or logging.getLogger(__name__)
        
        if not PYNETDICOM_AVAILABLE:
            self.logger.error("pynetdicom is not available - C-FIND queries will not work")
        
        self.last_results: List[QueryResult] = []
        self.last_query_params: Dict = {}
    
    def is_available(self) -> bool:
        """Check if query functionality is available."""
        return PYNETDICOM_AVAILABLE
    
    def query_pacs(
        self,
        server: str,
        port: int,
        calling_ae: str,
        called_ae: str,
        query_level: str,
        search_criteria: Dict[str, str],
        query_model: str = "StudyRoot",
        timeout: int = 30,
        use_tls: bool = False,
        tls_config: Optional[Dict] = None
    ) -> Tuple[bool, List[QueryResult], str]:
        """
        Perform C-FIND query against PACS.
        
        Args:
            server: PACS server IP/hostname
            port: PACS port (typically 104 or 11112)
            calling_ae: This application's AE title
            called_ae: PACS AE title
            query_level: Query level (PATIENT, STUDY, SERIES, IMAGE)
            search_criteria: Dictionary of search fields and values
            query_model: Query model (StudyRoot or PatientRoot)
            timeout: Network timeout in seconds
            use_tls: Whether to use TLS encryption
            tls_config: TLS configuration if use_tls is True
            
        Returns:
            Tuple of (success: bool, results: List[QueryResult], message: str)
        """
        if not PYNETDICOM_AVAILABLE:
            return False, [], "pynetdicom is not available"
        
        self.logger.info(f"Starting C-FIND query: {server}:{port} [{calling_ae} -> {called_ae}]")
        self.logger.info(f"Query Level: {query_level}, Model: {query_model}")
        self.logger.info(f"Search Criteria: {search_criteria}")

        # Quick connection test
        import socket
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((server, port))
            sock.close()
            if result != 0:
                error_msg = (
                    f"Cannot connect to {server}:{port}\n\n"
                    f"TCP connection failed (error code: {result})\n\n"
                    "Possible causes:\n"
                    "1. PACS server not running\n"
                    "2. Wrong IP address or port\n"
                    "3. Firewall blocking connection\n"
                    "4. Network connectivity issue"
                )
                self.logger.error(f"TCP connection test failed: {result}")
                return False, [], error_msg
            self.logger.info("TCP connection test passed")
        except Exception as conn_error:
            error_msg = f"Connection test failed: {str(conn_error)}"
            self.logger.error(error_msg)
            return False, [], error_msg

        # Store query parameters
        self.last_query_params = {
            'server': server,
            'port': port,
            'calling_ae': calling_ae,
            'called_ae': called_ae,
            'query_level': query_level,
            'search_criteria': search_criteria,
            'query_model': query_model,
            'timestamp': datetime.now().isoformat()
        }
        
        results = []
        error_message = ""
        
        try:
            # Create Application Entity
            ae = AE(ae_title=calling_ae)
            
            # Add presentation context for C-FIND
            if query_model == "PatientRoot":
                ae.add_requested_context(PatientRootQueryRetrieveInformationModelFind)
            else:  # StudyRoot (default)
                ae.add_requested_context(StudyRootQueryRetrieveInformationModelFind)
            
            # Build query dataset
            query_ds = self._build_query_dataset(query_level, search_criteria)
            
            # Establish association
            self.logger.info(f"Establishing association with {server}:{port}")
            
            assoc_kwargs = {}
            if use_tls and tls_config:
                # TODO: Add TLS support
                self.logger.warning("TLS support not yet implemented for C-FIND")
            
            assoc = ae.associate(
                server, 
                port, 
                ae_title=called_ae,
                **assoc_kwargs
            )
            
            if assoc.is_established:
                self.logger.info("Association established successfully")
                
                # Send C-FIND request
                if query_model == "PatientRoot":
                    responses = assoc.send_c_find(
                        query_ds,
                        PatientRootQueryRetrieveInformationModelFind
                    )
                else:
                    responses = assoc.send_c_find(
                        query_ds,
                        StudyRootQueryRetrieveInformationModelFind
                    )
                
                # Process responses
                response_count = 0
                for status, identifier in responses:
                    response_count += 1

                    if status and status.Status in (0xFF00, 0xFF01):
                        # Pending status - valid result
                        if identifier:
                            result = self._parse_query_response(query_level, identifier)
                            results.append(result)
                            self.logger.debug(f"Result {response_count}: {result.patient_name} - {result.study_description}")
                    elif status and status.Status == 0x0000:
                        # Success - query complete
                        self.logger.info(f"Query completed successfully. Found {len(results)} results")
                        break
                    else:
                        # Error or warning - interpret status code
                        status_code = status.Status
                        error_msg = self._interpret_status_code(status_code)
                        self.logger.warning(f"Query status: 0x{status_code:04X} - {error_msg}")
                        error_message = error_msg
                
                # Release association
                assoc.release()
                self.logger.info("Association released")
                
                self.last_results = results
                
                if len(results) == 0 and not error_message:
                    return True, results, "Query completed - No results found"
                elif error_message:
                    return False, results, error_message
                else:
                    return True, results, f"Found {len(results)} results"
                
            else:
                error_message = "Failed to establish association with PACS"
                self.logger.error(error_message)

                # Build detailed error message for user
                detailed_error = f"{error_message}\n\nPossible causes:\n"
                detailed_error += f"1. PACS server not running at {server}:{port}\n"
                detailed_error += f"2. Calling AE '{calling_ae}' not registered on PACS\n"
                detailed_error += f"3. Called AE '{called_ae}' does not match PACS configuration\n"
                detailed_error += f"4. Firewall blocking connection\n"
                detailed_error += f"5. PACS does not support C-FIND queries"

                # Try to get rejection details if available
                try:
                    if hasattr(assoc, 'rejected'):
                        rejection_info = str(assoc.rejected)
                        self.logger.error(f"Association rejected: {rejection_info}")
                        detailed_error += f"\n\nRejection details: {rejection_info}"
                    if hasattr(assoc, 'rejected_contexts'):
                        contexts = str(assoc.rejected_contexts)
                        self.logger.error(f"Rejected contexts: {contexts}")
                except Exception as detail_error:
                    self.logger.debug(f"Could not get rejection details: {detail_error}")

                return False, [], detailed_error
                
        except Exception as e:
            error_message = f"Query failed: {str(e)}"
            self.logger.exception("C-FIND query exception")
            return False, [], error_message
    
    def _interpret_status_code(self, status_code: int) -> str:
        """
        Interpret DICOM C-FIND status codes and return user-friendly messages.

        Args:
            status_code: DICOM status code (e.g., 0xC808)

        Returns:
            User-friendly error message
        """
        # DICOM C-FIND Status Codes
        status_messages = {
            # Success
            0x0000: "Success",

            # Pending
            0xFF00: "Pending - Matches are continuing",
            0xFF01: "Pending - Matches are continuing with optional keys",

            # Failure - Refused
            0xA700: "Out of resources - Unable to perform sub-operations",
            0xA900: "Identifier does not match SOP class",

            # Failure - Error Cannot Understand
            0xC000: "Unable to process - General failure",
            0xC001: "More than one match found",
            0xC002: "Unable to support requested template",

            # Failure - Failed
            0xC100: "SOP Class not supported",
            0xC200: "Duplicate invocation",
            0xC300: "Class-Instance conflict",
            0xC400: "Duplicate transaction UID",
            0xC500: "Invalid argument value",
            0xC600: "Attribute value out of range",
            0xC700: "Invalid object instance",
            0xC800: "Missing attribute",
            0xC801: "Missing attribute value",
            0xC802: "Attribute value out of range",
            0xC803: "Invalid attribute value",
            0xC804: "Invalid syntax",
            0xC805: "Missing mandatory matching key attribute",
            0xC806: "Duplicate matching key attribute",
            0xC807: "Invalid matching key attribute",
            0xC808: "Unable to process - Query attributes invalid or unsupported",
            0xC809: "Unable to process - Query attributes invalid or unsupported",
            0xC80A: "Unable to process - Query attributes invalid or unsupported",

            # Cancel
            0xFE00: "Query/Retrieve cancelled",
        }

        # Get message or return generic error
        if status_code in status_messages:
            message = status_messages[status_code]
        else:
            message = f"Unknown status code: 0x{status_code:04X}"

        # Add troubleshooting hints for common errors
        if status_code == 0xC808:
            message += "\n\nPossible causes:\n"
            message += "- Query level not supported by PACS\n"
            message += "- Search criteria contains invalid attributes\n"
            message += "- Date format is incorrect (should be YYYYMMDD)\n"
            message += "- Required matching key is missing\n"
            message += "- PACS does not support this query model (try PatientRoot instead of StudyRoot)"
        elif status_code == 0xC000:
            message += "\n\nPossible causes:\n"
            message += "- PACS internal error\n"
            message += "- Database connection issue\n"
            message += "- Query timeout\n"
            message += "- Insufficient permissions"
        elif status_code == 0xA700:
            message += "\n\nPossible causes:\n"
            message += "- PACS is overloaded\n"
            message += "- Too many concurrent queries\n"
            message += "- Narrow your search criteria to reduce results"

        return message

    def _build_query_dataset(self, query_level: str, criteria: Dict[str, str]) -> Dataset:
        """
        Build a DICOM dataset for C-FIND query.
        
        Args:
            query_level: Query level (PATIENT, STUDY, SERIES, IMAGE)
            criteria: Search criteria dictionary
            
        Returns:
            Configured Dataset for query
        """
        ds = Dataset()
        ds.QueryRetrieveLevel = query_level.upper()
        
        # Patient level fields (always include for all levels)
        if 'PatientName' in criteria and criteria['PatientName']:
            ds.PatientName = criteria['PatientName']
        else:
            ds.PatientName = ''  # Universal match
        
        if 'PatientID' in criteria and criteria['PatientID']:
            ds.PatientID = criteria['PatientID']
        else:
            ds.PatientID = ''
        
        ds.PatientBirthDate = criteria.get('PatientBirthDate', '')
        ds.PatientSex = criteria.get('PatientSex', '')
        
        # Study level fields (for STUDY, SERIES, IMAGE queries)
        if query_level.upper() in ['STUDY', 'SERIES', 'IMAGE']:
            ds.StudyInstanceUID = criteria.get('StudyInstanceUID', '')
            ds.StudyDate = criteria.get('StudyDate', '')
            ds.StudyTime = criteria.get('StudyTime', '')
            ds.StudyDescription = criteria.get('StudyDescription', '')
            ds.AccessionNumber = criteria.get('AccessionNumber', '')
            ds.StudyID = criteria.get('StudyID', '')
            ds.Modality = criteria.get('Modality', '')
        
        # Series level fields (for SERIES, IMAGE queries)
        if query_level.upper() in ['SERIES', 'IMAGE']:
            ds.SeriesInstanceUID = criteria.get('SeriesInstanceUID', '')
            ds.SeriesNumber = criteria.get('SeriesNumber', '')
            ds.SeriesDescription = criteria.get('SeriesDescription', '')
            ds.NumberOfSeriesRelatedInstances = ''  # Request instance count
        
        # Image level fields (for IMAGE queries)
        if query_level.upper() == 'IMAGE':
            ds.SOPInstanceUID = criteria.get('SOPInstanceUID', '')
            ds.InstanceNumber = criteria.get('InstanceNumber', '')
        
        self.logger.debug(f"Built query dataset: {ds}")
        return ds
    
    def _parse_query_response(self, query_level: str, dataset: Dataset) -> QueryResult:
        """
        Parse a C-FIND response dataset into a QueryResult object.
        
        Args:
            query_level: The query level (PATIENT, STUDY, SERIES, IMAGE)
            dataset: Response dataset from PACS
            
        Returns:
            QueryResult object with parsed data
        """
        result = QueryResult(level=query_level.upper(), dataset=dataset)
        
        # Patient level data (always present)
        result.patient_id = str(getattr(dataset, 'PatientID', ''))
        result.patient_name = str(getattr(dataset, 'PatientName', ''))
        result.patient_birth_date = str(getattr(dataset, 'PatientBirthDate', ''))
        result.patient_sex = str(getattr(dataset, 'PatientSex', ''))
        
        # Study level data
        if hasattr(dataset, 'StudyInstanceUID'):
            result.study_uid = str(dataset.StudyInstanceUID)
        if hasattr(dataset, 'StudyDate'):
            result.study_date = str(dataset.StudyDate)
        if hasattr(dataset, 'StudyTime'):
            result.study_time = str(dataset.StudyTime)
        if hasattr(dataset, 'StudyDescription'):
            result.study_description = str(dataset.StudyDescription)
        if hasattr(dataset, 'AccessionNumber'):
            result.accession_number = str(dataset.AccessionNumber)
        if hasattr(dataset, 'Modality'):
            result.modality = str(dataset.Modality)
        
        # Series level data
        if hasattr(dataset, 'SeriesInstanceUID'):
            result.series_uid = str(dataset.SeriesInstanceUID)
        if hasattr(dataset, 'SeriesNumber'):
            result.series_number = str(dataset.SeriesNumber)
        if hasattr(dataset, 'SeriesDescription'):
            result.series_description = str(dataset.SeriesDescription)
        if hasattr(dataset, 'NumberOfSeriesRelatedInstances'):
            try:
                result.num_instances = int(dataset.NumberOfSeriesRelatedInstances)
            except (ValueError, TypeError):
                result.num_instances = 0
        
        # Image level data
        if hasattr(dataset, 'SOPInstanceUID'):
            result.sop_instance_uid = str(dataset.SOPInstanceUID)
        
        return result
    
    def get_last_results(self) -> List[QueryResult]:
        """Get results from the last query."""
        return self.last_results
    
    def get_last_query_params(self) -> Dict:
        """Get parameters from the last query."""
        return self.last_query_params
    
    def clear_results(self):
        """Clear stored query results."""
        self.last_results = []
        self.last_query_params = {}
