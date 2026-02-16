# TLS/SSL Configuration Guide

## Overview

DICOM Creator now supports secure DICOM transmission over TLS/SSL. This feature allows you to:
- Encrypt DICOM data during transmission
- Authenticate clients using certificates
- Verify server identity
- Comply with security requirements for medical data transmission

## Enabling TLS

### Basic Setup

1. Open DICOM Creator
2. Navigate to the **Remote** tab
3. Check the **Use TLS/SSL** checkbox
4. Click **Remote** menu ? **TLS Settings...** to configure certificates

### TLS Settings Dialog

The TLS Settings dialog allows you to configure:

#### Certificate Files

- **Client Certificate (PEM)**: Your client certificate file in PEM format
- **Private Key (PEM)**: Private key for your certificate in PEM format
- **Key Password**: Optional password if your private key is encrypted
- **CA Certificate (PEM)**: Certificate Authority file to verify the server

#### TLS Options

- **Verify Server Certificate**: Validates the server's certificate against trusted CAs (recommended)
- **Verify Server Hostname**: Ensures the server hostname matches the certificate (recommended)
- **Allow Self-Signed Certificates**: Permits self-signed certificates (only for testing)
- **Minimum TLS Version**: Select TLSv1.1, TLSv1.2, or TLSv1.3 (TLSv1.2 recommended)
- **Cipher Suite**: Optionally specify custom cipher suites

## Certificate Formats

### Supported Formats

DICOM Creator accepts certificates in PEM format (.pem, .crt) and private keys in PEM format (.pem, .key).

### Converting Certificates

If you have certificates in other formats, you can convert them using OpenSSL:

```bash
# Convert PKCS12 (.p12, .pfx) to PEM
openssl pkcs12 -in certificate.p12 -out certificate.pem -nodes

# Extract certificate from PKCS12
openssl pkcs12 -in certificate.p12 -out certificate.pem -nokeys

# Extract private key from PKCS12
openssl pkcs12 -in certificate.p12 -out key.pem -nocerts -nodes

# Convert DER to PEM
openssl x509 -in certificate.der -inform DER -out certificate.pem -outform PEM
```

## Common Scenarios

### Scenario 1: Server with TLS, No Client Authentication

If the DICOM server requires TLS but not client certificates:

1. Enable **Use TLS/SSL** checkbox
2. In TLS Settings:
   - Leave **Client Certificate** and **Private Key** empty
   - Optionally provide **CA Certificate** if server uses custom CA
   - Keep **Verify Server Certificate** enabled
   - Configure **Minimum TLS Version** as required by server

### Scenario 2: Mutual TLS Authentication

If the server requires both server and client certificates:

1. Enable **Use TLS/SSL** checkbox
2. In TLS Settings:
   - Provide **Client Certificate** (your certificate)
   - Provide **Private Key** (your private key)
   - Provide **CA Certificate** (to verify server)
   - Keep **Verify Server Certificate** enabled
   - Configure **Minimum TLS Version**

### Scenario 3: Testing with Self-Signed Certificates

For testing environments with self-signed certificates:

1. Enable **Use TLS/SSL** checkbox
2. In TLS Settings:
   - Configure client certificate if required
   - Check **Allow Self-Signed Certificates**
   - Optionally disable **Verify Server Certificate** and **Verify Hostname**

**Warning**: Do not use this configuration in production!

## Saving TLS Settings

### With Server Presets

TLS settings are automatically saved with server presets:

1. Configure your TLS settings
2. Enable **Use TLS/SSL** checkbox
3. Enter a preset name or use server address as name
4. Click **Save Current** button

When you load the preset later, it will restore both server configuration and TLS settings.

### As Separate Configuration File

You can also save/load TLS configuration independently:

1. In TLS Settings dialog, click **Save Config**
2. Choose a location and filename (e.g., `hospital_tls.json`)
3. Later, click **Load Config** to restore these settings

## Troubleshooting

### Connection Fails with TLS Enabled

1. **Check certificate paths**: Ensure all certificate files exist and are readable
2. **Verify certificate format**: Certificates must be in PEM format
3. **Check server requirements**: Confirm the server expects TLS on the configured port
4. **Review TLS version**: Ensure minimum TLS version matches server requirements
5. **Check firewall**: TLS typically uses different ports than non-TLS

### Certificate Verification Errors

1. **Check CA certificate**: Ensure the CA certificate matches the server's certificate chain
2. **Verify hostname**: The server address must match the certificate's Common Name or SAN
3. **Check certificate expiry**: Ensure certificates are not expired
4. **Review intermediate certificates**: Some servers require intermediate CA certificates

### Self-Signed Certificate Issues

If using self-signed certificates:
1. Enable **Allow Self-Signed Certificates** option
2. Consider disabling **Verify Hostname** if hostname doesn't match
3. Provide the self-signed certificate as the CA certificate

## Security Best Practices

1. **Always use TLS in production** when transmitting medical data
2. **Keep verify options enabled** unless specifically needed for testing
3. **Use TLSv1.2 or higher** - avoid TLSv1.0 and TLSv1.1
4. **Protect private keys** - store them securely and use strong passwords
5. **Regularly update certificates** before they expire
6. **Use strong cipher suites** - avoid weak or deprecated ciphers
7. **Never disable verification in production** environments

## Technical Details

### TLS Implementation

DICOM Creator uses Python's `ssl` module and pynetdicom's TLS support to establish secure connections. The implementation:

- Supports TLS 1.1, 1.2, and 1.3
- Validates server certificates against system or custom CA certificates
- Supports client certificate authentication (mutual TLS)
- Allows hostname verification
- Supports custom cipher suite configuration

### Certificate Chain

For proper TLS operation, ensure your certificate chain is complete:
1. Your client certificate
2. Any intermediate CA certificates
3. The root CA certificate

Some certificate files include the full chain. If not, you may need to concatenate them:

```bash
cat client.pem intermediate.pem > full_chain.pem
```

## Support

For issues or questions:
1. Check the application logs for detailed error messages
2. Review the TLS Settings dialog help section
3. Consult your DICOM server administrator for server requirements
4. Refer to pynetdicom documentation for advanced TLS scenarios

## References

- [DICOM Standard PS3.15 - Security Profiles](http://dicom.nema.org/medical/dicom/current/output/html/part15.html)
- [pynetdicom TLS Documentation](https://pydicom.github.io/pynetdicom/stable/examples/tls.html)
- [OpenSSL Documentation](https://www.openssl.org/docs/)
- [Python SSL Module](https://docs.python.org/3/library/ssl.html)
