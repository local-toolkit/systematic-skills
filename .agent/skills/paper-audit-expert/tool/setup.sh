#!/bin/bash
# Setup script for paper-audit-expert using relative paths

BASE_DIR="./paper_audit"

echo "Setting up Paper Audit directory at $BASE_DIR..."

mkdir -p "$BASE_DIR/inbox"
mkdir -p "$BASE_DIR/completed"
mkdir -p "$BASE_DIR/notes"

echo "Directories created:"
echo "- $BASE_DIR/inbox (Place PDFs here)"
echo "- $BASE_DIR/completed (Processed PDFs go here)"
echo "- $BASE_DIR/notes (Obsidian notes appear here)"

echo "Setup complete."
