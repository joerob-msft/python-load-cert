from flask import Flask, render_template_string
import os
import glob
import ssl
import datetime
import subprocess
import OpenSSL.crypto as crypto

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Azure App Service Certificates</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            line-height: 1.6;
        }
        h1 {
            color: #0078D4;
            border-bottom: 2px solid #0078D4;
            padding-bottom: 10px;
        }
        h2 {
            color: #505050;
            margin-top: 30px;
        }
        .cert-container {
            margin-bottom: 30px;
        }
        .cert {
            background-color: #f5f5f5;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
        }
        .cert-name {
            font-weight: bold;
            font-size: 18px;
            margin-bottom: 10px;
        }
        .cert-details {
            margin-left: 15px;
        }
        .cert-item {
            margin-bottom: 8px;
        }
        .cert-path {
            font-family: monospace;
            color: #555;
        }
        .error {
            color: #D83B01;
            font-style: italic;
        }
        .no-certs {
            color: #666;
            font-style: italic;
        }
        .status-valid {
            color: #107C10;
        }
        .status-warning {
            color: #D83B01;
        }
        .status-expired {
            color: #D83B01;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <h1>Azure App Service Certificate Inventory</h1>
    
    <p>Generated on: {{ current_time }}</p>
    <p>Hostname: {{ hostname }}</p>
    
    <div class="cert-container">
        <h2>TLS/SSL Certificates</h2>
        {% if tls_certs %}
            {% for cert in tls_certs %}
                <div class="cert">
                    <div class="cert-name">{{ cert.name }}</div>
                    <div class="cert-path">{{ cert.path }}</div>
                    <div class="cert-details">
                        {% if cert.error %}
                            <div class="error">{{ cert.error }}</div>
                        {% else %}
                            <div class="cert-item">Subject: {{ cert.subject }}</div>
                            <div class="cert-item">Issuer: {{ cert.issuer }}</div>
                            <div class="cert-item">Serial Number: {{ cert.serial }}</div>
                            <div class="cert-item">Valid From: {{ cert.valid_from }}</div>
                            <div class="cert-item">Valid Until: {{ cert.valid_until }}</div>
                            <div class="cert-item">
                                Status: 
                                {% if cert.status == "Valid" %}
                                    <span class="status-valid">{{ cert.status }}</span>
                                {% elif cert.status == "Warning" %}
                                    <span class="status-warning">{{ cert.status }} (Expires in {{ cert.days_left }} days)</span>
                                {% else %}
                                    <span class="status-expired">{{ cert.status }}</span>
                                {% endif %}
                            </div>
                            <div class="cert-item">Fingerprint (SHA1): {{ cert.fingerprint }}</div>
                        {% endif %}
                    </div>
                </div>
            {% endfor %}
        {% else %}
            <div class="no-certs">No TLS/SSL certificates found</div>
        {% endif %}
    </div>
    
    <div class="cert-container">
        <h2>Client Certificates</h2>
        {% if client_certs %}
            {% for cert in client_certs %}
                <div class="cert">
                    <div class="cert-name">{{ cert.name }}</div>
                    <div class="cert-path">{{ cert.path }}</div>
                    <div class="cert-details">
                        {% if cert.error %}
                            <div class="error">{{ cert.error }}</div>
                        {% else %}
                            <div class="cert-item">Subject: {{ cert.subject }}</div>
                            <div class="cert-item">Issuer: {{ cert.issuer }}</div>
                            <div class="cert-item">Serial Number: {{ cert.serial }}</div>
                            <div class="cert-item">Valid From: {{ cert.valid_from }}</div>
                            <div class="cert-item">Valid Until: {{ cert.valid_until }}</div>
                            <div class="cert-item">
                                Status: 
                                {% if cert.status == "Valid" %}
                                    <span class="status-valid">{{ cert.status }}</span>
                                {% elif cert.status == "Warning" %}
                                    <span class="status-warning">{{ cert.status }} (Expires in {{ cert.days_left }} days)</span>
                                {% else %}
                                    <span class="status-expired">{{ cert.status }}</span>
                                {% endif %}
                            </div>
                            <div class="cert-item">Fingerprint (SHA1): {{ cert.fingerprint }}</div>
                        {% endif %}
                    </div>
                </div>
            {% endfor %}
        {% else %}
            <div class="no-certs">No client certificates found</div>
        {% endif %}
    </div>
    
    <div class="cert-container">
        <h2>Environment Information</h2>
        <div class="cert">
            <div class="cert-details">
                <div class="cert-item">WEBSITE_LOAD_CERTIFICATES: {{ cert_env_var }}</div>
                <div class="cert-item">App Service SSL Settings: {{ ssl_settings }}</div>
            </div>
        </div>
    </div>
</body>
</html>
'''

def get_certificate_info(cert_path):
    try:
        with open(cert_path, 'rb') as cert_file:
            cert_data = cert_file.read()
            
        if cert_path.endswith('.pfx'):
            # For PFX files, we can't easily extract info without a password
            # Just return basic info
            return {
                'name': os.path.basename(cert_path),
                'path': cert_path,
                'subject': 'PFX file (password protected)',
                'issuer': 'Unknown (PFX format)',
                'serial': 'Unknown',
                'valid_from': 'Unknown',
                'valid_until': 'Unknown',
                'status': 'Unknown',
                'days_left': 'Unknown',
                'fingerprint': 'Unknown'
            }
        
        try:
            # Try to load as a PEM certificate
            cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert_data)
        except crypto.Error:
            try:
                # Try to load as a DER certificate
                cert = crypto.load_certificate(crypto.FILETYPE_ASN1, cert_data)
            except crypto.Error:
                return {
                    'name': os.path.basename(cert_path),
                    'path': cert_path,
                    'error': 'Unable to parse certificate format'
                }
                
        # Extract certificate details
        subject = ", ".join([f"{name.decode()}={value.decode()}" 
                            for name, value in cert.get_subject().get_components()])
        issuer = ", ".join([f"{name.decode()}={value.decode()}" 
                          for name, value in cert.get_issuer().get_components()])
        
        # Get validity dates
        not_before = datetime.datetime.strptime(cert.get_notBefore().decode(), "%Y%m%d%H%M%SZ")
        not_after = datetime.datetime.strptime(cert.get_notAfter().decode(), "%Y%m%d%H%M%SZ")
        
        # Calculate days left and status
        now = datetime.datetime.utcnow()
        days_left = (not_after - now).days
        
        if now > not_after:
            status = "Expired"
        elif days_left < 30:
            status = "Warning"
        else:
            status = "Valid"
            
        # Get fingerprint
        fingerprint = cert.digest("sha1").decode()
        
        return {
            'name': os.path.basename(cert_path),
            'path': cert_path,
            'subject': subject,
            'issuer': issuer,
            'serial': format(cert.get_serial_number(), 'x'),
            'valid_from': not_before.strftime("%Y-%m-%d %H:%M:%S UTC"),
            'valid_until': not_after.strftime("%Y-%m-%d %H:%M:%S UTC"),
            'status': status,
            'days_left': days_left,
            'fingerprint': fingerprint
        }
    except Exception as e:
        return {
            'name': os.path.basename(cert_path),
            'path': cert_path,
            'error': f"Error processing certificate: {str(e)}"
        }

def find_certificates():
    # Common certificate paths in Azure App Service Linux
    tls_cert_paths = [
        # Standard SSL certificate paths
        "/var/ssl/certs/*.crt",
        "/var/ssl/certs/*.cer",
        "/var/ssl/certs/*.pem",
        "/var/ssl/certs/*.pfx",
        # App Service certificate paths
        "/var/appservice/certs/*.crt",
        "/var/appservice/certs/*.cer",
        "/var/appservice/certs/*.pem",
        "/var/appservice/certs/*.pfx",
        # Additional paths
        "/home/site/certs/*.crt",
        "/home/site/certs/*.cer",
        "/home/site/certs/*.pem",
        "/home/site/certs/*.pfx",
    ]
    
    # Client certificate paths
    client_cert_paths = [
        # Standard client certificate paths
        "/var/client-certs/*.crt",
        "/var/client-certs/*.cer",
        "/var/client-certs/*.pem",
        "/var/client-certs/*.pfx",
        # App Service client certificate paths
        "/home/site/wwwroot/certs/*.crt",
        "/home/site/wwwroot/certs/*.cer",
        "/home/site/wwwroot/certs/*.pem",
        "/home/site/wwwroot/certs/*.pfx",
    ]
    
    tls_certs = []
    for path_pattern in tls_cert_paths:
        for cert_path in glob.glob(path_pattern):
            tls_certs.append(get_certificate_info(cert_path))
    
    client_certs = []
    for path_pattern in client_cert_paths:
        for cert_path in glob.glob(path_pattern):
            client_certs.append(get_certificate_info(cert_path))
    
    return tls_certs, client_certs

def get_ssl_settings():
    try:
        # Try to use App Service-specific SSL settings command if available
        result = subprocess.run(['/opt/appservice/ssl-settings', 'list'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return result.stdout.strip()
        return "Not available (command not found or failed)"
    except:
        return "Not available (error running command)"

@app.route('/')
def home():
    tls_certs, client_certs = find_certificates()
    
    hostname = "Unknown"
    try:
        hostname = os.environ.get('WEBSITE_HOSTNAME', subprocess.check_output(['hostname']).decode().strip())
    except:
        pass
    
    cert_env_var = os.environ.get('WEBSITE_LOAD_CERTIFICATES', 'Not set')
    
    return render_template_string(HTML_TEMPLATE, 
                                 tls_certs=tls_certs,
                                 client_certs=client_certs,
                                 current_time=datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                                 hostname=hostname,
                                 cert_env_var=cert_env_var,
                                 ssl_settings=get_ssl_settings())

if __name__ == '__main__':
    # When running locally, use debug mode
    if os.environ.get('WEBSITE_HOSTNAME') is None:
        app.run(debug=True, port=5000)
    else:
        # In production, use the production server
        app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
