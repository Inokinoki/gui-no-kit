#!/bin/bash
# Quick start script for gui-no-kit

set -e

echo "======================================"
echo "Xpra GUI Test Framework - Quick Start"
echo "======================================"
echo

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Check if uv is available
if command -v uv &> /dev/null; then
    echo "✓ uv found"
    INSTALL_CMD="uv pip install"
    RUN_CMD="uv run"
else
    echo "⚠ uv not found, using pip"
    INSTALL_CMD="pip install"
    RUN_CMD="python"
fi

# Install package
echo
echo "Installing gui-no-kit..."
$INSTALL_CMD -e .

# Install Playwright browsers
echo
echo "Installing Playwright Chromium..."
playwright install chromium

# Run tests
echo
echo "Running import tests..."
$RUN_CMD pytest tests/test_imports.py -v

echo
echo "======================================"
echo "Installation complete!"
echo "======================================"
echo
echo "Next steps:"
echo "1. Ensure Xpra is installed:"
echo "   - Ubuntu/Debian: sudo apt install xpra xvfb"
echo "   - macOS: brew install xpra"
echo "   - Windows: Download from https://xpra.org/"
echo
echo "2. Run example tests:"
echo "   $RUN_CMD pytest src/gui_no_kit/examples/example_tests.py -v"
echo
echo "3. Create your first test:"
echo "   See README.md for documentation"
echo
