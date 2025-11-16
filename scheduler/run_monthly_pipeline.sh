#!/bin/sh
# A simple script to run the demo monthly pipeline once (or ran by Docker).
set -e
echo "Scheduler container starting demo pipeline..."
python /app/app/infer.py --demo-run
echo "Demo pipeline finished."
# Keep container alive for debugging (optional)
sleep 5

