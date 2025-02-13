#!/bin/bash
echo "🚀 Starting bot..."
gunicorn --worker-tmp-dir /dev/shm -w 1 -b 0.0.0.0:$PORT bot:main
