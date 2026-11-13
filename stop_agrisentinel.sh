#!/usr/bin/env bash

echo "Stopping AgriSentinel services..."
for port in 8000 3000 8501; do
    pid=$(lsof -ti :${port} 2>/dev/null || true)
    if [ -n "$pid" ]; then
        kill -9 $pid 2>/dev/null || true
        echo "Terminated process on port ${port}"
    fi
done
echo "All services stopped."
