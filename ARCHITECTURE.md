# Architecture Diagram Generator

## Overview

This guide provides step-by-step instructions to:

1. **Import existing AWS infrastructure** (RDS, ECS, ALB, VPC) into Terraform management
2. **Generate visual architecture diagrams** from your Terraform configuration
3. **Create two diagram types:**
   - Simple visual diagram with AWS icons (for management presentations)
   - Detailed technical diagram with attributes and dependencies (for documentation)

**Tools Used:**
- `generate_architecture_diagram.py` - Combines diagrams library and Graphviz to render architecture PNGs from Terraform state
- `setup_diagram_tools.sh` - Installs Python, Graphviz and other system/Python dependencies
- `import_rds_wp_waf.sh` - Imports existing AWS resources into Terraform state
- `main.tf` - Terraform configuration that orchestrates resources and invokes import scripts as part of apply

**Output:**
- `management_diagram.png`  - Business-friendly visualization
- `technical_detailed.png` - Technical reference diagram

## Quick Start

### Prerequisites
- Must exist WordPress Project (aws-wp-tf-v5) and do AWS user credentail in terraform.tfvars
- Download `agnihotri-deepika_aws_lab.zip` 
- Terraform installed
- Python 3 available

### Step-by-Step Instructions

#### a) Download and Extract
```bash
# Download to your workspace 
cd /home/cloudshell-user
Download agnihotri-deepika_aws_lab.zip 
unzip agnihotri-deepika_aws_lab.zip
```

#### b) Move Files to WordPress Project
```bash
# Copy all content to aws-wp-tf-v5
mv agnihotri-deepika_aws_lab/* aws-wp-tf-v5/
cd aws-wp-tf-v5
```

#### c) Import All Infrastructure

Assuming Terraform is installed. Inside `aws-wp-tf-v5`, run:

```bash
terraform init
terraform plan
terraform apply
```

**Note:** `main.tf` will invoke `import_rds_wp_waf.sh` script which will import existing resources.

---

## Diagram Generation Steps

### Step 1: Install Tools to Create Diagram

```bash
chmod +x setup_diagram_tools.sh
bash ./setup_diagram_tools.sh
```

### Step 2: Generate Terraform State

```bash
terraform show -json > tfstate.json
```

### Step 3: Create Diagrams

```bash
python3 generate_architecture_diagram.py tfstate.json
```

### Step 4: View Results

Two PNG files will be created:

- **`management_diagram.png`** - Simple visual for Management
- **`technical_diagram.png`** - Detailed technical diagram for engineers