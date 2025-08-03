import os
import io
import boto3
from flask import Flask, request, jsonify
from google.cloud import storage
from dotenv import load_dotenv
import logging


# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# AWS S3 setup
s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)

# Google Cloud Storage setup
gcs_client = storage.Client.from_service_account_json(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
gcs_bucket = gcs_client.bucket(os.getenv("GCP_BUCKET_NAME"))

@app.route("/v1/replicate", methods=["POST"])
def replicate_file():
    """
    POST endpoint to replicate a file from AWS S3 to Google Cloud Storage.
    Expects JSON with s3_bucket and s3_key.
    """
    data = request.get_json()

    # Validate payload
    s3_bucket = data.get("s3_bucket")
    s3_key = data.get("s3_key")

    if not s3_bucket or not s3_key:
        return jsonify({"error": "Missing s3_bucket or s3_key in JSON payload"}), 400

    try:
        # Check if file already exists in GCS (idempotent behavior)
        blob = gcs_bucket.blob(s3_key)
        if blob.exists():
            logging.info(f"File '{s3_key}' already exists in GCS. Skipping upload.")
            return jsonify({"status": "already exists"}), 200

        # Download file from S3
        logging.info(f"Downloading file '{s3_key}' from S3 bucket '{s3_bucket}'...")
        s3_object = s3.get_object(Bucket=s3_bucket, Key=s3_key)
        stream = io.BytesIO(s3_object['Body'].read())

        # Upload to GCS
        logging.info(f"Uploading file '{s3_key}' to GCS bucket...")
        blob.upload_from_file(stream)
        logging.info(f"File '{s3_key}' replicated successfully.")

        return jsonify({"status": "success"}), 200

    except Exception as e:
        logging.error(f"Replication failed: {e}")
        return jsonify({"error": str(e)}), 500

# Start Flask app
if __name__ == "__main__":
    app.run(debug=True, port=5000)
