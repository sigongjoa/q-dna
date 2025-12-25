#!/bin/bash
echo "=== Re-initializing Database ==="
sudo -u postgres psql -c "DROP DATABASE IF EXISTS q_dna_db;"
sudo -u postgres psql -c "CREATE DATABASE q_dna_db;"
export PYTHONPATH=./backend
python3 backend/scripts/init_db.py
