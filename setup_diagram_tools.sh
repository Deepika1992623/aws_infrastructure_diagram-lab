#!/bin/bash
# setup_diagram_tools.sh
# Installs required Python packages for architecture diagram generation


echo "Installing system dependencies..."
sudo yum install graphviz -y
pip install diagrams graphviz

echo "Setup complete!"
echo ""
echo "To generate diagrams:"
echo "  a. terraform show -json > tfstate.json"
echo "  b. python3 generate_architecture_diagram.py tfstate.json"
