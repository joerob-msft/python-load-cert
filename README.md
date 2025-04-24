# Azure App Service Certificate Inventory

![Azure](https://img.shields.io/badge/azure-%230072C6.svg?style=for-the-badge&logo=microsoftazure&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)

A lightweight web application that provides a human-readable inventory of TLS/SSL certificates and client certificates in your Azure App Service Linux environment.

## Features

- Lists public certificates (DER format) from `/var/ssl/certs`
- Lists private certificates (P12 format) from `/var/ssl/private`
- Displays certificate metadata including:
  - Subject and issuer information
  - Validity dates and expiration status
  - Serial numbers and fingerprints
  - File details for password-protected certificates
- Shows environment variables related to certificates
- Simple, clean, responsive web interface

## Screenshot
![image](https://github.com/user-attachments/assets/f08c9ff4-897b-4523-ad89-fdbbe9647cac)

## Deployment

### Prerequisites

- An Azure App Service (Linux)
- GitHub account to host the repository
- Access to GitHub Actions or Azure DevOps pipelines

### Deployment Methods

#### 1. GitHub Actions (Recommended)

1. Fork or clone this repository to your GitHub account
2. In your GitHub repository settings, add these secrets:
   - `AZURE_WEBAPP_NAME`: Your App Service name
   - `AZURE_WEBAPP_PUBLISH_PROFILE`: Your publish profile XML content (download from Azure Portal)
3. Push to the main branch, and GitHub Actions will deploy to your Azure App Service

#### 2. Manual Deployment via Azure Portal

1. Clone this repository to your local machine
2. In the Azure Portal, navigate to your App Service
3. Go to Deployment Center
4. Choose your preferred deployment method (Local Git, GitHub, etc.)
5. Follow the prompts to connect your repository
6. Deploy the code to your App Service

#### 3. Azure CLI

```bash
# Login to Azure
az login

# Set your subscription
az account set --subscription <subscription-id>

# Deploy to App Service
az webapp up --name <app-name> --resource-group <resource-group-name> --runtime "PYTHON:3.9"
```

## Required App Service Configuration

Ensure your App Service has these configurations:

1. **Runtime Stack**: Python 3.9 or later
2. **Startup Command**: `gunicorn --bind=0.0.0.0 --timeout 600 app:app`
3. **Application Settings**:
   - `SCM_DO_BUILD_DURING_DEPLOYMENT`: Set to `true`
   - `PYTHONPATH`: `/home/site/wwwroot`

## Connecting to the Deployments Blade

To monitor and manage deployments through the Azure Portal:

1. Navigate to your App Service in the Azure Portal
2. Select "Deployment Center" from the left navigation menu
3. If using GitHub Actions, you'll see your deployments listed here
4. Select a deployment to view logs and status details
5. Use "Logs" tab to troubleshoot any deployment issues

## Certificate Access Requirements

For the application to access certificates:

1. The application needs read access to `/var/ssl/certs` for public DER certificates
2. The application needs read access to `/var/ssl/private` for private P12 certificates
3. Ensure `WEBSITE_LOAD_CERTIFICATES` is set to `*` to load all certificates or specific thumbprints to load individual certificates

## Development

### Local Development

```bash
# Clone repository
git clone https://github.com/yourusername/azure-cert-inventory.git
cd azure-cert-inventory

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app locally
python app.py
```

### Requirements

```
Flask==2.3.3
pyOpenSSL==23.2.0
cryptography==41.0.3
```

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
