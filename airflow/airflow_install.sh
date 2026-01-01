#!/bin/bash
set -e  # Exit on error

AIRFLOW_VERSION=3.0.6
PYTHON_VERSION=3.10
CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"

# Parse command line arguments
ENV_TYPE="${1:-conda}"  # Default to conda if no argument provided

if [[ "$ENV_TYPE" != "conda" && "$ENV_TYPE" != "venv" ]]; then
    echo "Error: Invalid environment type. Use 'conda' or 'venv'"
    echo "Usage: $0 [conda|venv]"
    exit 1
fi

echo "Setting up Airflow with ${ENV_TYPE}..."

# Create and activate environment based on type
if [[ "$ENV_TYPE" == "conda" ]]; then
    # Check if conda environment already exists
    if conda env list | grep -q "^airflow "; then
        echo "Conda environment 'airflow' already exists. Activating..."
    else
        echo "Creating conda environment 'airflow'..."
        conda create -n airflow python=${PYTHON_VERSION} -y
    fi
    
    # Activate conda environment
    eval "$(conda shell.bash hook)"
    conda activate airflow
    
else
    # Python venv
    if [ -d "airflow_env" ]; then
        echo "Virtual environment 'airflow_env' already exists. Activating..."
    else
        echo "Creating Python virtual environment 'airflow_env'..."
        python3 -m venv airflow_env
    fi
    
    # Activate venv
    source airflow_env/bin/activate
fi

pip install --upgrade setuptools pip flask_appbuilder
pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"
pip install apache-airflow-providers-fab

export AIRFLOW_HOME="$(pwd)"
export AIRFLOW__CORE__LOAD_EXAMPLES="False"
mkdir -p "$AIRFLOW_HOME"/{logs,plugins}

# configuration
airflow config list --defaults > "${AIRFLOW_HOME}/airflow.cfg"

# ====
# Automated configuration of airflow.cfg
# ====

echo "Configuring airflow.cfg..."

# Generate JWT secrets
JWT_SECRET=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

# Update executor to LocalExecutor
sed -i.bak 's/^executor = .*/executor = LocalExecutor/' "${AIRFLOW_HOME}/airflow.cfg"

# Update auth_manager (on macOS use -i.bak, on Linux use -i'')
sed -i.bak 's|^# auth_manager = .*|auth_manager = airflow.providers.fab.auth_manager.fab_auth_manager.FabAuthManager|' "${AIRFLOW_HOME}/airflow.cfg"

# Set JWT secret
sed -i.bak "s|^# jwt_secret = .*|jwt_secret = ${JWT_SECRET}|" "${AIRFLOW_HOME}/airflow.cfg"

# Set secret key
sed -i.bak "s|^secret_key = .*|secret_key = ${SECRET_KEY}|" "${AIRFLOW_HOME}/airflow.cfg"

echo "Configuration complete!"
echo "Secrets generated and saved to airflow.cfg"

# db setup
airflow db migrate

airflow users create \
    --username admin \
    --firstname First \
    --lastname Last \
    --role Admin \
    --email admin@example.com \
    --password admin


# command to start server
airflow api-server --port 8080