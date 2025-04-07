import OpenSSL.crypto
from OpenSSL.crypto import X509Store, X509StoreContext, X509StoreContextError

def get_certificate_info(subject_name):
    # Create a store and add certificates to it
    store = X509Store()
    
    # Load the certificates from the cert store
    # This part will depend on where your certificates are stored
    # For example, you might load them from files or a specific directory
    # Here, we assume you have a list of certificate files
    cert_files = ["path/to/cert1.pem", "path/to/cert2.pem"]  # Update with actual paths
    
    for cert_file in cert_files:
        with open(cert_file, "rb") as f:
            cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, f.read())
            store.add_cert(cert)
    
    # Find the certificate by subject name
    cert = None
    for cert_file in cert_files:
        with open(cert_file, "rb") as f:
            cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, f.read())
            if cert.get_subject().CN == subject_name:
                break
    
    if cert is None:
        print(f"No certificate found with subject name {subject_name}")
        return
    
    # Get the thumbprint of the certificate
    thumbprint = cert.digest("sha1")
    
    # Check if the certificate has a private key
    # This part will depend on how you manage private keys
    # Here, we assume you have a list of private key files
    private_key_files = ["path/to/key1.pem", "path/to/key2.pem"]  # Update with actual paths
    has_private_key = False
    
    for key_file in private_key_files:
        with open(key_file, "rb") as f:
            private_key = OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_PEM, f.read())
            try:
                X509StoreContext(store, cert, private_key)
                has_private_key = True
                break
            except X509StoreContextError:
                continue
    
    print(f"Thumbprint: {thumbprint}")
    print(f"Has Private Key: {has_private_key}")

# Call the function with the subject name "CN=joerob.local"
get_certificate_info("CN=joerob.local")
