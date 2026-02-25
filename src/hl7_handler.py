"""Minimal HL7 v2.x parser/sender and FHIR R4 REST client."""
import socket
from datetime import datetime

MLLP_SB = b'\x0b'   # Start Block
MLLP_EB = b'\x1c'   # End Block
MLLP_CR = b'\x0d'   # Carriage Return


class HL7Handler:
    """Parses HL7 ADT/ORM messages, builds ORU messages, and communicates with FHIR R4 servers."""

    def __init__(self, logger=None):
        self.logger = logger

    # ── HL7 v2.x ─────────────────────────────────────────────────────────────

    def _segment(self, message, seg_id):
        """Return split fields for the first matching segment, or None."""
        for line in message.replace('\r', '\n').splitlines():
            if line.startswith(seg_id + '|'):
                return line.split('|')
        return None

    @staticmethod
    def _f(lst, idx, default=''):
        """Safe list index with default."""
        try:
            return lst[idx] or default
        except IndexError:
            return default

    def parse_adt(self, message):
        """Parse HL7 ADT message → patient demographics dict."""
        pid = self._segment(message, 'PID')
        if not pid:
            return {}
        f = self._f
        parts = f(pid, 5).split('^')
        last, first = parts[0], (parts[1] if len(parts) > 1 else '')
        return {
            'PatientID': f(pid, 3).split('^')[0],
            'PatientName': f"{last}^{first}" if first else last,
            'PatientBirthDate': f(pid, 7)[:8],
            'PatientSex': f(pid, 8),
            'PatientAddress': f(pid, 11).replace('^', ' ').strip(),
            'PatientTelephoneNumbers': f(pid, 13),
        }

    def parse_orm(self, message):
        """Parse HL7 ORM^O01 → order/study dict."""
        obr = self._segment(message, 'OBR')
        pv1 = self._segment(message, 'PV1')
        f = self._f
        result = {}
        if obr:
            desc = f(obr, 4)
            result['AccessionNumber'] = f(obr, 18)
            result['StudyDescription'] = desc.split('^')[-1] if '^' in desc else desc
            result['Modality'] = f(obr, 24)
            result['BodyPartExamined'] = f(obr, 15).split('^')[0]
        if pv1:
            result['StudyDate'] = f(pv1, 44)[:8]
        return result

    def build_oru(self, patient, study):
        """Build a minimal ORU^R01 message from patient/study dicts."""
        now = datetime.now().strftime('%Y%m%d%H%M%S')
        segments = [
            f"MSH|^~\\&|DCMCREATOR|||{now}||ORU^R01|MSG{now}|P|2.5",
            (f"PID|1||{patient.get('PatientID', '')}||{patient.get('PatientName', '')}||"
             f"{patient.get('PatientBirthDate', '')}|{patient.get('PatientSex', '')}"),
            f"OBR|1|{study.get('AccessionNumber', '')}||{study.get('StudyDescription', '')}|||{now}",
            "OBX|1|ST|StudyStatus||DICOM study created by DICOM Creator||||||F",
        ]
        return '\r'.join(segments) + '\r'

    def send_mllp(self, host, port, message, timeout=10):
        """Send HL7 message via MLLP. Returns (success, ack_or_error)."""
        try:
            data = MLLP_SB + message.encode('utf-8') + MLLP_EB + MLLP_CR
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                s.connect((host, port))
                s.sendall(data)
                raw = s.recv(4096)
            ack = raw.lstrip(MLLP_SB).decode('utf-8', errors='replace').strip()
            return True, ack
        except Exception as e:
            if self.logger:
                self.logger.exception("MLLP send failed")
            return False, str(e)

    # ── FHIR R4 ──────────────────────────────────────────────────────────────

    def fhir_get_patient(self, base_url, patient_id):
        """GET FHIR R4 Patient/{id}. Returns (success, dict_or_error)."""
        try:
            try:
                import requests
            except ImportError:
                return False, "'requests' library is not installed. Run: pip install requests"
            url = f"{base_url.rstrip('/')}/Patient/{patient_id}"
            resp = requests.get(url, timeout=10, headers={'Accept': 'application/fhir+json'})
            resp.raise_for_status()
            return True, self._fhir_to_dict(resp.json())
        except Exception as e:
            if self.logger:
                self.logger.exception("FHIR GET Patient failed")
            return False, str(e)

    def fhir_post_patient(self, base_url, patient_data):
        """POST FHIR R4 Patient resource. Returns (success, id_or_error)."""
        try:
            try:
                import requests
            except ImportError:
                return False, "'requests' library is not installed. Run: pip install requests"
            url = f"{base_url.rstrip('/')}/Patient"
            resp = requests.post(
                url, json=self._dict_to_fhir(patient_data), timeout=10,
                headers={'Content-Type': 'application/fhir+json', 'Accept': 'application/fhir+json'}
            )
            resp.raise_for_status()
            return True, resp.json().get('id', 'created')
        except Exception as e:
            if self.logger:
                self.logger.exception("FHIR POST Patient failed")
            return False, str(e)

    def _fhir_to_dict(self, resource):
        """Map FHIR Patient resource to form-field dict."""
        result = {'PatientID': resource.get('id', '')}
        names = resource.get('name', [])
        if names:
            n = names[0]
            given = ' '.join(n.get('given', []))
            result['PatientName'] = f"{n.get('family', '')}^{given}" if given else n.get('family', '')
        dob = resource.get('birthDate', '')
        result['PatientBirthDate'] = dob.replace('-', '')[:8]
        result['PatientSex'] = {'male': 'M', 'female': 'F', 'other': 'O'}.get(resource.get('gender', ''), '')
        phones = [t.get('value', '') for t in resource.get('telecom', []) if t.get('system') == 'phone']
        result['PatientTelephoneNumbers'] = phones[0] if phones else ''
        return result

    def _dict_to_fhir(self, data):
        """Map form-field dict to FHIR Patient resource."""
        resource = {'resourceType': 'Patient'}
        if data.get('PatientID'):
            resource['id'] = data['PatientID']
        name = data.get('PatientName', '')
        if name:
            parts = name.split('^')
            resource['name'] = [{'family': parts[0], 'given': [parts[1]] if len(parts) > 1 else []}]
        dob = data.get('PatientBirthDate', '')
        if len(dob) == 8:
            resource['birthDate'] = f"{dob[:4]}-{dob[4:6]}-{dob[6:]}"
        resource['gender'] = {'M': 'male', 'F': 'female', 'O': 'other'}.get(
            data.get('PatientSex', '').upper(), 'unknown')
        if data.get('PatientTelephoneNumbers'):
            resource['telecom'] = [{'system': 'phone', 'value': data['PatientTelephoneNumbers']}]
        return resource
