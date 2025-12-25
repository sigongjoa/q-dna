#!/bin/bash

echo "=== Q-DNA Math Advanced Service Test Runner ==="
echo "[*] Checking Prerequisites..."

# Check Docker
if command -v docker &> /dev/null; then
    echo "[+] Docker found. Running with Docker Compose..."
    docker compose up -d --build
    echo "[*] Waiting for services to stabilize (10s)..."
    sleep 10
    echo "[*] Running Integration Tests..."
    docker compose exec backend pytest tests/integration/test_math_advanced_flow.py
    exit 0
fi

# Fallback to Local (Poetry)
if command -v poetry &> /dev/null; then
    echo "[+] Poetry found. Running locally..."
    cd backend
    poetry install
    # Ensure Ollama is running separately
    poetry run pytest tests/integration/test_math_advanced_flow.py
    exit 0
fi

echo "[-] Neither Docker nor Poetry found. Please install one of them to run tests."
exit 1
