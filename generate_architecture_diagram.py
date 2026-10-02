#!/usr/bin/env python3
"""
generate_architecture_diagram.py
"""

import json
import sys
from diagrams import Diagram, Cluster
from diagrams.aws.general import User
from diagrams.aws.network import VPC, ELB, ALB
from diagrams.aws.compute import ECS, EC2
from diagrams.aws.storage import S3
from diagrams.aws.database import RDS
from graphviz import Digraph


def load_state(path):
    with open(path, "r") as f:
        return json.load(f)


def collect_resources(state):
    resources = []
    
    if "values" in state and "root_module" in state["values"]:
        root = state["values"]["root_module"]
        
        def walk_modules(module):
            """Recursively walk through all modules."""
            if "resources" in module:
                resources.extend(module["resources"])
            if "child_modules" in module:
                for child in module["child_modules"]:
                    walk_modules(child)
        
        walk_modules(root)
    
    return resources


def create_management_diagram(resources):
    print("Creating management diagram...")
    
    # Sort resources by type
    elbs = [r for r in resources if r.get("type") in ("aws_elb", "aws_lb", "aws_alb")]
    ecs_clusters = [r for r in resources if r.get("type") == "aws_ecs_cluster"]
    instances = [r for r in resources if r.get("type") == "aws_instance"]
    s3s = [r for r in resources if r.get("type") == "aws_s3_bucket"]
    rds_instances = [r for r in resources if r.get("type") in ("aws_db_instance", "aws_rds_cluster")]
    vpcs = [r for r in resources if r.get("type") == "aws_vpc"]
    
    # Create diagram
    with Diagram("AWS Architecture", filename="management_diagram", show=False, direction="LR"):
        user = User("Users")
        
        with Cluster("AWS"):
            vpc_node = None
            if vpcs:
                vpc_node = VPC("VPC")

            elb_node = None
            if elbs:
                elb_name = elbs[0].get("address", "alb").split(".")[-1]
                elb_node = ALB(elb_name)

            ecs_node = None
            if ecs_clusters:
                cluster_name = ecs_clusters[0].get("address", "ecs_cluster").split(".")[-1]
                ecs_node = ECS(cluster_name)

            ec2_node = None
            if instances:
                ec2_node = EC2(instances[0].get("address", "ec2"))

            rds_node = None
            if rds_instances:
                db_name = rds_instances[0].get("address", "rds").split(".")[-1]
                rds_node = RDS(db_name)

            s3_node = None
            if s3s:
                s3_name = s3s[0].get("address", "s3").split(".")[-1]
                s3_node = S3(s3_name)

        # Create connections
        if elb_node:
            user >> elb_node
            if ecs_node:
                elb_node >> ecs_node
            elif ec2_node:
                elb_node >> ec2_node
        else:
            if ecs_node:
                user >> ecs_node
            elif ec2_node:
                user >> ec2_node

        # Connect compute to data services
        compute_node = ecs_node or ec2_node
        if compute_node:
            if rds_node:
                compute_node >> rds_node
            if s3_node:
                compute_node >> s3_node

    print("✓ Management diagram created: management_diagram.png")
    
def format_attributes(attr_dict):
    if not isinstance(attr_dict, dict):
        return ""

    keys_to_show = [
        "id", "arn", "public_ip", "private_ip", "bucket",
        "availability_zone", "cidr_block", "vpc_id", "subnet_id",
        "instance_type", "engine", "allocated_storage", "port"
    ]

    lines = []
    for key in keys_to_show:
        if key in attr_dict:
            value = attr_dict[key]
            if isinstance(value, (str, int, float)):
                lines.append(f"{key}: {value}")

    return "\n".join(lines)


def create_technical_diagram(resources):
    print("Creating technical diagram...")
    
    diagram = Digraph("Terraform_Architecture", filename="technical_diagram", format="png")
    diagram.attr(rankdir="LR")
    diagram.attr("node", shape="box", style="rounded,filled", fillcolor="lightgray")

    # Add nodes with rich info
    for r in resources:
        addr = r.get("address", "unknown")
        rtype = r.get("type", "unknown")
        attrs = r.get("values", {})

        attr_text = format_attributes(attrs)

        label = f"{addr}\n({rtype})"
        if attr_text:
            label += f"\n---\n{attr_text}"

        diagram.node(addr, label)

    # Add dependency edges
    for r in resources:
        addr = r.get("address", "unknown")
        deps = r.get("depends_on", [])
        for d in deps:
            diagram.edge(addr, d, label="depends_on")

    diagram.render(cleanup=True)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 generate_architecture_diagram.py tfstate.json")
        print("\nFirst, generate the state file:")
        print("    terraform show -json > tfstate.json")
        sys.exit(1)
    
    input_file = sys.argv[1]
    print(f"Loading Terraform state from: {input_file}")
    state = load_state(input_file)
    resources = collect_resources(state)
        
    if not resources:
        print("Error: No resources found in state file.")
        sys.exit(1)
        
    print(f"Found {len(resources)} resources\n")
        
    # Create both diagrams
    create_management_diagram(resources)
    create_technical_diagram(resources)
    print("\nOutput files:")
    print("  management_diagram.png created.")
    print("  technical_diagram.png created.")

if __name__ == "__main__":
    main()
