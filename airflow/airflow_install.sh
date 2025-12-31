AIRFLOW_VERSION=3.0.6
PYTHON_VERSION=3.10
CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"

# create a python virtual env or conda env depending on preference

# conda create -n airflow python=3.10 -y
# conda activate airflow

# OR

# python3 -m venv airflow_env
# . airflow_env/bin/activate

pip install --upgrade setuptools pip flask_appbuilder
pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"
pip install apache-airflow-providers-fab

export AIRFLOW_HOME="$(pwd)"
export AIRFLOW__CORE__LOAD_EXAMPLES="False"
mkdir -p "$AIRFLOW_HOME"/{dags,logs,plugins}

# configuration
airflow config list --defaults > "${AIRFLOW_HOME}/airflow.cfg"

# ====
# make changes to airflow.cfg
# ====

# executor = LocalExecutor
# auth_manager = airflow.providers.fab.auth_manager.fab_auth_manager.FabAuthManager

# // create two tokens
# python -c "import secrets; print(secrets.token_urlsafe(32))"

# jwt_secret = {YOUR JWT SECRET}
# secret_key = {YOUR JWT SECRET}

# db setup
airflow db migrate

airflow users create \
    --username admin \
    --firstname First \
    --lastname Last \
    --role Admin \
    --email admin@example.com


# command to start server
# airflow api-server --port 8080