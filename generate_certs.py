"""
Generate complete set of TLS certificates for DICOM Creator
Uses OpenSSL via subprocess - no config files needed
"""
import subprocess
import sys
import os

# Global variable for OpenSSL executable
OPENSSL_EXECUTABLE = 'openssl'

def find_best_openssl():
    """Find the best OpenSSL executable (prefer standalone over PostgreSQL)"""
    # Try to find all OpenSSL installations
    if sys.platform == 'win32':
        try:
            result = subprocess.run(
                ['where', 'openssl'],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                paths = [p.strip() for p in result.stdout.split('\n') if p.strip()]
                
                # Prefer non-PostgreSQL OpenSSL
                for path in paths:
                    if 'postgresql' not in path.lower() and 'psql' not in path.lower():
                        print(f"Using OpenSSL: {path}")
                        return path
                
                # Fall back to any OpenSSL found
                if paths:
                    print(f"Using OpenSSL: {paths[0]}")
                    return paths[0]
        except:
            pass
    
    # Default to 'openssl' in PATH
    print("Using default OpenSSL from PATH")
    return 'openssl'

def create_minimal_openssl_config():
    """Create minimal OpenSSL configuration file with CA extensions"""
    config_content = """# Minimal OpenSSL Configuration
[ req ]
default_bits = 2048
distinguished_name = req_distinguished_name
prompt = no
x509_extensions = v3_ca

[ req_distinguished_name ]
C = US
ST = State
L = City
O = TestOrg
CN = DICOM Test

[ v3_ca ]
basicConstraints = critical,CA:TRUE
keyUsage = critical,keyCertSign,cRLSign
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid:always,issuer
"""
    config_path = os.path.join(os.getcwd(), 'openssl_minimal.cnf')
    with open(config_path, 'w') as f:
        f.write(config_content)
    return config_path

def run_openssl(args, description="", env=None):
    """Run OpenSSL command with error handling"""
    if description:
        print(f"  {description}...", end=" ", flush=True)
    
    # Use custom environment if provided
    if env is None:
        env = os.environ.copy()
    
    result = subprocess.run(
        [OPENSSL_EXECUTABLE] + args,
        capture_output=True,
        text=True,
        cwd=os.getcwd(),
        env=env
    )
    
    if result.returncode != 0:
        print("FAILED")
        print(f"Error: {result.stderr}")
        return False
    
    if description:
        print("OK")
    return True

def main():
    global OPENSSL_EXECUTABLE
    
    print("="*60)
    print("DICOM TLS Certificate Generator")
    print("="*60)
    
    # Find best OpenSSL executable
    print("\nSearching for OpenSSL...")
    OPENSSL_EXECUTABLE = find_best_openssl()
    
    # Ensure we're in the right directory
    cert_dir = r"C:\dicom-certs"
    os.makedirs(cert_dir, exist_ok=True)
    os.chdir(cert_dir)
    
    print(f"Working directory: {cert_dir}")
    
    # Create minimal OpenSSL config
    print("Creating OpenSSL configuration...")
    config_file = create_minimal_openssl_config()
    
    # Set up environment with config file
    env = os.environ.copy()
    env['OPENSSL_CONF'] = config_file
    
    print()
    
    # Get server address
    server = input("Enter server IP/hostname (default: localhost): ").strip()
    if not server:
        server = "localhost"
    
    print(f"\nGenerating certificates for: {server}")
    print("This will take about 1 minute...\n")
    
    # ====================================================================
    # 1. Generate CA (Certificate Authority)
    # ====================================================================
    print("1. Creating Certificate Authority (CA)")
    
    # Generate CA private key
    if not run_openssl(
        ['genrsa', '-out', 'ca_key.pem', '2048'],
        "Generating CA private key",
        env
    ):
        return False
    
    # Create CA certificate with proper extensions (v3_ca defined in config)
    if not run_openssl(
        ['req', '-new', '-x509', '-days', '3650', 
         '-key', 'ca_key.pem', '-out', 'ca_cert.pem',
         '-sha256', '-config', config_file,
         '-subj', '/C=US/ST=State/L=City/O=TestOrg/CN=DICOM Test CA'],
        "Creating CA certificate",
        env
    ):
        return False
    
    # ====================================================================
    # 2. Generate Server Certificate
    # ====================================================================
    print("\n2. Creating Server Certificate")
    
    # Generate server private key
    if not run_openssl(
        ['genrsa', '-out', 'server_key.pem', '2048'],
        "Generating server private key",
        env
    ):
        return False
    
    # Create server CSR
    if not run_openssl(
        ['req', '-new', '-key', 'server_key.pem',
         '-out', 'server.csr', '-sha256', '-config', config_file,
         '-subj', f'/C=US/ST=State/L=City/O=TestOrg/CN={server}'],
        "Creating certificate signing request",
        env
    ):
        return False
    
    # Create server extensions file
    with open('server_ext.cnf', 'w') as f:
        f.write(f'subjectAltName=DNS:{server},DNS:localhost,IP:127.0.0.1\n')
        f.write('extendedKeyUsage=serverAuth\n')
    
    # Sign server certificate
    if not run_openssl(
        ['x509', '-req', '-in', 'server.csr',
         '-CA', 'ca_cert.pem', '-CAkey', 'ca_key.pem',
         '-CAcreateserial', '-out', 'server_cert.pem',
         '-days', '365', '-sha256', '-extfile', 'server_ext.cnf'],
        "Signing server certificate",
        env
    ):
        return False
    
    # ====================================================================
    # 3. Generate Client Certificate
    # ====================================================================
    print("\n3. Creating Client Certificate")
    
    # Generate client private key
    if not run_openssl(
        ['genrsa', '-out', 'client_key.pem', '2048'],
        "Generating client private key",
        env
    ):
        return False
    
    # Create client CSR
    if not run_openssl(
        ['req', '-new', '-key', 'client_key.pem',
         '-out', 'client.csr', '-sha256', '-config', config_file,
         '-subj', '/C=US/ST=State/L=City/O=TestOrg/CN=DCMCREATOR Client'],
        "Creating certificate signing request",
        env
    ):
        return False
    
    # Create client extensions file
    with open('client_ext.cnf', 'w') as f:
        f.write('extendedKeyUsage=clientAuth\n')
    
    # Sign client certificate
    if not run_openssl(
        ['x509', '-req', '-in', 'client.csr',
         '-CA', 'ca_cert.pem', '-CAkey', 'ca_key.pem',
         '-CAcreateserial', '-out', 'client_cert.pem',
         '-days', '365', '-sha256', '-extfile', 'client_ext.cnf'],
        "Signing client certificate",
        env
    ):
        return False
    
    # ====================================================================
    # 4. Verify Certificates
    # ====================================================================
    print("\n4. Verifying Certificates")
    
    # Check that client cert and key match
    print("  Verifying client cert/key pair...", end=" ", flush=True)
    
    # Get modulus from cert
    cert_modulus = subprocess.run(
        [OPENSSL_EXECUTABLE, 'x509', '-noout', '-modulus', '-in', 'client_cert.pem'],
        capture_output=True, text=True
    ).stdout.strip()
    
    # Get modulus from key
    key_modulus = subprocess.run(
        [OPENSSL_EXECUTABLE, 'rsa', '-noout', '-modulus', '-in', 'client_key.pem'],
        capture_output=True, text=True
    ).stdout.strip()
    
    if cert_modulus == key_modulus:
        print("OK ✓")
    else:
        print("FAILED - cert and key don't match!")
        return False
    
    # Check hash algorithm
    print("  Checking signature algorithms...", end=" ", flush=True)
    for cert_file in ['ca_cert.pem', 'server_cert.pem', 'client_cert.pem']:
        result = subprocess.run(
            [OPENSSL_EXECUTABLE, 'x509', '-in', cert_file, '-noout', '-text'],
            capture_output=True, text=True
        )
        if 'sha256' not in result.stdout.lower():
            print(f"FAILED - {cert_file} not using SHA256!")
            return False
    print("OK (SHA256) ✓")
    
    # ====================================================================
    # 5. Cleanup
    # ====================================================================
    print("\n5. Cleaning up temporary files")
    for temp_file in ['server.csr', 'client.csr', 'server_ext.cnf', 
                      'client_ext.cnf', 'ca_cert.srl', 'openssl_minimal.cnf']:
        try:
            os.remove(temp_file)
        except:
            pass
    print("  Done")
    
    # ====================================================================
    # 6. Summary
    # ====================================================================
    print("\n" + "="*60)
    print("SUCCESS! All certificates generated")
    print("="*60)
    
    print(f"\nCertificate files in: {cert_dir}")
    print("\nGenerated files:")
    for filename in sorted(os.listdir('.')):
        if filename.endswith('.pem'):
            size = os.path.getsize(filename)
            print(f"  ✓ {filename:20s} ({size:,} bytes)")
    
    print("\n" + "="*60)
    print("DICOM Creator Configuration")
    print("="*60)
    
    print("\nIn DICOM Creator → Remote → TLS Settings:")
    print(f"  Client Certificate: {cert_dir}\\client_cert.pem")
    print(f"  Private Key:        {cert_dir}\\client_key.pem")
    print(f"  CA Certificate:     {cert_dir}\\ca_cert.pem")
    print("  Key Password:       [leave empty]")
    
    print("\n  Options:")
    print("    ☑ Allow Self-Signed Certificates")
    print("    ☐ Verify Server Certificate (disable for testing)")
    print("    ☐ Verify Hostname (disable for testing)")
    print("    Minimum TLS Version: TLSv1.2")
    
    print("\n" + "="*60)
    print("Test Server Configuration")
    print("="*60)
    
    print(f"\nFor Python test server (tls_test_server.py):")
    print(f"  Server Certificate: {cert_dir}\\server_cert.pem")
    print(f"  Server Key:         {cert_dir}\\server_key.pem")
    print(f"  CA Certificate:     {cert_dir}\\ca_cert.pem")
    
    print("\n✓ All done! Press Enter to exit...")
    input()
    return True

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nCancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)