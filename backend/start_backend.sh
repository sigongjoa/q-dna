#!/bin/bash
export OLLAMA_TEXT_MODEL="qwen2.5:latest"
echo "Starting Backend with Model: $OLLAMA_TEXT_MODEL"
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > backend_start.log 2>&1 &
echo "Started."
