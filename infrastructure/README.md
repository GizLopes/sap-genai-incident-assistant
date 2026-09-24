# Infrastructure

This directory contains the minimum deployment artifacts for the SAP GenAI Incident Assistant POC on Amazon EC2.

## Files

```text
infrastructure/
├── README.md
├── ec2-user-data.sh
└── iam-policy.json
```

## Runtime

The EC2 instance hosts the Streamlit UI, Python application, SAP mock, deterministic control layer, and local FAISS index.

Amazon Bedrock provides Claude Sonnet 4.6 inference and Titan Text Embeddings V2. DynamoDB stores audit records.

The runtime does not use Amazon Bedrock Knowledge Bases. Retrieval is performed locally with FAISS using the prebuilt `data/faiss.index` and `data/faiss_metadata.json` artifacts.

## IAM

Attach an EC2 instance role containing the permissions in `iam-policy.json`.

The policy is limited to:

- Claude Sonnet 4.6 inference through the configured cross-Region inference profile;
- Titan Text Embeddings V2 invocation in `us-east-1`;
- read/write access required by the application for the dedicated DynamoDB audit table.

AWS access keys must not be stored in the repository, `.env`, user data, or Streamlit configuration.

## EC2 bootstrap

`ec2-user-data.sh` targets Amazon Linux 2023. Before using it, configure:

```bash
REPOSITORY_URL="https://github.com/<organization>/<repository>.git"
```

The script installs the Python runtime and dependencies, creates the `sapgenai` service user, configures the application as a systemd service, and starts Streamlit only when the application and FAISS artifacts are present.

The application listens on TCP port `8501`. Restrict the EC2 Security Group source to the IP range required for the POC.

## Validation

After deployment:

```bash
cd /opt/sap-genai-assistant
source .venv/bin/activate
python scripts/healthcheck.py --aws
```

Expected result:

```text
Overall: HEALTHY
```

Check the service:

```bash
sudo systemctl status sap-genai-assistant
sudo journalctl -u sap-genai-assistant -f
```

Restart when required:

```bash
sudo systemctl restart sap-genai-assistant
```

## POC boundary

The deployment uses the SAP mock and read-only analysis workflow. The AI may analyze evidence and recommend diagnostic checks. SAP state-changing actions remain outside the POC and require human authorization.
