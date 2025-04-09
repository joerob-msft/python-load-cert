
from flask import Flask, jsonify
from OpenSSL import crypto
import os

app = Flask(__name__)

@app.route('/check_certificates', methods=['GET'])
def check_certificates():
    try:
        # Directory where certificates are stored
        certs_dir = '/var/ssl/certs'  # Common directory for certificates in Azure Web Apps
        
        # List to store certificate details
        certs_info = []

        # Iterate over files in the directory
        for filename in os.listdir(certs_dir):
            if filename.endswith('.pem'):
                cert_path = os.path.join(certs_dir, filename)
                
                # Load the certificate from the file
                with open(cert_path, 'r') as cert_file:
                    cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert_file.read())
                
                # Check if the private key is present
                private_key_present = cert.has_private_key()
                
                # Append certificate info to the list
                certs_info.append({
                    'certificate': filename,
                    'private_key_present': private_key_present
                })
        
        return jsonify(certs_info)
    except Exception as e:
        return jsonify({'error': str(e)})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
