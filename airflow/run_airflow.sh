#!/bin/bash
# start_airflow.sh
# Exit on any error
set -e
export AIRFLOW_HOME="$(pwd)"
source $(AIRFLOW_HOME)/airflow_env/bin/activate

echo "Starting all Airflow components..."

# Start components in the background and store their PIDs
airflow scheduler &
PIDS[0]=$!

airflow dag-processor &
PIDS[1]=$!

airflow triggerer &
PIDS[2]=$!

airflow api-server --port 8080 &  
PIDS[3]=$!

# Function to clean up and kill all background processes
cleanup() {
    echo "Shutting down all Airflow components..."
    for PID in ${PIDS[*]}; do
        kill $PID 2>/dev/null
    done
}

# Set a trap to run the cleanup function on script exit (e.g., Ctrl+C)
trap cleanup EXIT

# Wait for any background process to exit
# wait -n

# Poll for any process exiting (portable alternative to `wait -n`)
while true; do
  for PID in "${PIDS[@]}"; do
    # If the process no longer exists, handle its exit
    if ! kill -0 "$PID" 2>/dev/null; then
      # Collect exit code for the finished process
      wait "$PID"
      EXIT_CODE=$?

      if [ "$EXIT_CODE" -ne 0 ]; then
        echo "A component failed with exit code $EXIT_CODE. Stopping all other components."
        # Trap will run cleanup; exit with the failing code
        exit "$EXIT_CODE"
      else
        echo "A component finished successfully. Shutting down."
        exit 0
      fi
    fi
  done
  sleep 1
done

# Check the exit code of the process that finished
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
    echo "A component failed with exit code $EXIT_CODE. Stopping all other components."
    # The 'trap' will handle the cleanup automatically
    exit $EXIT_CODE
else
    echo "A component finished successfully. Shutting down."
fi

echo "All Airflow components have been stopped."