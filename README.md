#  Cross-Cloud Event-Driven Storage Replicator

This project is a simple Python Flask service that listens for a POST request containing AWS S3 file info and replicates the file to Google Cloud Storage.

---

## Features

- Event-driven replication from **AWS S3 ➡️ GCP Cloud Storage**
- Flask API endpoint to trigger replication
- Uses `boto3` for AWS and `google-cloud-storage` for GCP
- Loads configuration from `.env` file
- Includes basic error handling and idempotency logic
- Easy to deploy and test locally

---

##  Dependencies

Install them with:

```bash
pip install -r requirements.txt
