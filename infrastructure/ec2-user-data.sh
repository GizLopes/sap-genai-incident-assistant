#!/bin/bash
set -euo pipefail

# SAP GenAI Incident Assistant - EC2 bootstrap
# Amazon Linux 2023. No AWS credentials are stored here.

APP_NAME="sap-genai-assistant"
APP_DIR="/opt/${APP_NAME}"
APP_USER="sapgenai"
REPOSITORY_URL=""
BRANCH="main"
STREAMLIT_PORT="8501"

log() {
  echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] $*"
}

log "Starting EC2 bootstrap."

dnf update -y
dnf install -y git python3 python3-pip

if ! id "${APP_USER}" >/dev/null 2>&1; then
  useradd --system --create-home --shell /bin/bash "${APP_USER}"
fi

mkdir -p "${APP_DIR}"
chown -R "${APP_USER}:${APP_USER}" "${APP_DIR}"

if [[ -n "${REPOSITORY_URL}" ]]; then
  log "Preparing application repository."

  if [[ -d "${APP_DIR}/.git" ]]; then
    sudo -u "${APP_USER}" git -C "${APP_DIR}" fetch origin "${BRANCH}"
    sudo -u "${APP_USER}" git -C "${APP_DIR}" checkout "${BRANCH}"
    sudo -u "${APP_USER}" git -C "${APP_DIR}" pull --ff-only origin "${BRANCH}"
  else
    rm -rf "${APP_DIR:?}"/*
    sudo -u "${APP_USER}" git clone \
      --branch "${BRANCH}" \
      --single-branch \
      "${REPOSITORY_URL}" \
      "${APP_DIR}"
  fi
else
  log "REPOSITORY_URL is empty. Repository clone skipped."
  log "Copy or clone the project into ${APP_DIR} before starting the service."
fi

if [[ -f "${APP_DIR}/requirements.txt" ]]; then
  log "Creating Python virtual environment."
  sudo -u "${APP_USER}" python3 -m venv "${APP_DIR}/.venv"
  sudo -u "${APP_USER}" "${APP_DIR}/.venv/bin/python" -m pip install --upgrade pip
  sudo -u "${APP_USER}" "${APP_DIR}/.venv/bin/pip" install -r "${APP_DIR}/requirements.txt"
else
  log "requirements.txt not found. Dependency installation skipped."
fi

cat > "/etc/systemd/system/${APP_NAME}.service" <<EOF
[Unit]
Description=SAP GenAI Incident Assistant
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=${APP_USER}
Group=${APP_USER}
WorkingDirectory=${APP_DIR}

Environment=PYTHONUNBUFFERED=1
Environment=AWS_REGION=us-east-1
Environment=APP_ENV=poc
Environment=SAP_MODULE=MM
Environment=USE_MOCK_SAP=true
Environment=ENABLE_AUDIT_LOGGING=true
Environment=BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-6
Environment=EMBEDDING_MODEL_ID=amazon.titan-embed-text-v2:0
Environment=MAX_RETRIEVAL_RESULTS=5
Environment=MINIMUM_GROUNDING_SCORE=0.50
Environment=DYNAMODB_TABLE=sap-genai-assistant-audit

ExecStart=${APP_DIR}/.venv/bin/streamlit run app/ui.py --server.address 0.0.0.0 --server.port ${STREAMLIT_PORT}
Restart=on-failure
RestartSec=5

NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=full
ProtectHome=true
ReadWritePaths=${APP_DIR}

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload

if [[ -x "${APP_DIR}/.venv/bin/streamlit" \
   && -f "${APP_DIR}/app/ui.py" \
   && -f "${APP_DIR}/data/faiss.index" \
   && -f "${APP_DIR}/data/faiss_metadata.json" ]]; then
  log "Enabling and starting ${APP_NAME}."
  systemctl enable --now "${APP_NAME}"
else
  log "Application or FAISS artifacts are missing; service created but not started."
fi

log "Bootstrap completed."
log "Application port: ${STREAMLIT_PORT}"
log "Restrict inbound access to port ${STREAMLIT_PORT} with the EC2 Security Group."
