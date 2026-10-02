#!/usr/bin/env bash

#exiting after execution failed.
set -euo pipefail

integarion_status() {
    echo "Verify Integrations  "

    if ! command -v aws &>/dev/null; then
        echo "AWS  not found. Install AWS first."
        exit 1
    fi
    echo "AWS  found"

    if ! command -v terraform &>/dev/null; then
        echo "Terraform is not installed in environment."
        exit 1
    fi
    echo "Terraform Exist"

    if ! aws sts get-caller-identity --region "us-east-1" &>/dev/null; then
        echo "Credential verification failed , check AWS credential ."
        exit 1
    fi
    echo "Credentials validation successfull"

    if [ ! -d .terraform ]; then
        echo "terraform not initialized. Run 'terraform init' first."
        exit 1
    fi
    echo "terraform initialized"

    ACCOUNT_ID=$(aws sts get-caller-identity --region "us-east-1" --query Account --output text)
    echo "AWS Account: $ACCOUNT_ID"
    echo
}

import_rds() {
    echo "RDS Resources"

    RDS_ID=$(aws rds describe-db-instances --region "us-east-1" \
        --query "DBInstances[?DBInstanceIdentifier=='my-mariadb-db'].DBInstanceIdentifier" \
        --output text 2>/dev/null || echo "")

    if [ -z "$RDS_ID" ]; then
        echo "No RDS instance found with ID 'my-mariadb-db'."
        return
    fi

    echo "Found RDS instance: $RDS_ID"
    echo "Importing DB subnet group..."
    terraform import aws_db_subnet_group.default wp-db-subnet-tf 2>/dev/null || true

    echo "Importing RDS instance..."
    terraform import aws_db_instance.db "$RDS_ID" 2>/dev/null || \
        echo "RDS instance already imported or not found"

    echo "RDS import complete"
    echo
}

import_ecs() {
    echo "Import WordPress --"
    RAW=$(aws ecs list-clusters \
        --region "us-east-1" \
        --query "clusterArns" \
        --output text 2>&1)
    if [[ $? -ne 0 ]]; then
        echo "AWS CLI error: $RAW"
        exit 1
    fi

    CLUSTER=$(echo "$RAW" | tr '\t' '\n' | grep -E "ecs-wordpress|wordpress" | head -n 1)

    if [[ -z "$CLUSTER" ]]; then
        echo "No ECS cluster found."
    else
        echo "Found cluster: $CLUSTER"
    fi

    CLUSTER_NAME=$(echo "$CLUSTER" | rev | cut -d'/' -f1 | rev)
    echo "Found ECS cluster: $CLUSTER_NAME"

    terraform import aws_ecs_cluster.default "$CLUSTER_NAME" 2>/dev/null || \
        echo "ECS cluster already imported"

    echo "ECS import complete"
    echo
}

import_waf() {
    echo "AWS WAF configurations -- : "
    terraform import aws_config_configuration_recorder.recorder default
    terraform import aws_config_delivery_channel.channel default
    terraform import aws_iam_role.config_role aws-config-role
    terraform import aws_s3_bucket.config_bucket config-logs-wordpres-001
    echo "WAF import complete"
    echo
}

verify_imports() {
    echo "----:: Import statistics ::-----"

    terraform state list 2>/dev/null || echo "No resources in state"
}

main() {
    echo
    echo "Importing module AWS RDS,WordPress,AWS WAF "
    echo

    integarion_status
    import_rds
    import_ecs
    verify_imports
    import_waf

    echo "Import workflow complete!"
    echo
}

#main function
main

