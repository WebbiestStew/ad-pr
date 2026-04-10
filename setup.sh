#!/bin/bash
set -e

PACKAGES=("git" "vim" "python3" "python3-pip" "curl" "unzip")

echo "[1/3] Updating package index..."
sudo apt update -y

echo "[2/3] Installing packages..."
for pkg in "${PACKAGES[@]}"; do
  if dpkg -s "$pkg" &>/dev/null; then
    echo "  ✓ $pkg already installed, skipping"
  else
    echo "  → Installing $pkg..."
    sudo apt install -y "$pkg"
  fi
done

echo "[3/3] Installing Python deps..."
if [ -f requirements.txt ]; then
  pip3 install -r requirements.txt
else
  echo "  No requirements.txt found, skipping"
fi

echo "Done!"
