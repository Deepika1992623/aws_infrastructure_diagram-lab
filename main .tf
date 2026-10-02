
# calling bash script to import all module
resource "null_resource" "import_resources" {
  provisioner "local-exec" {
    command    = "chmod u+x ./import_rds_wp_waf.sh && bash ./import_rds_wp_waf.sh"
    on_failure = continue
  }

  triggers = {
    script_hash = filemd5("./import_rds_wp_waf.sh")
  }
}

output "import_status" {
  description = "Status of resource imports"
  value       = "Run 'terraform state list' to verify imported resources"
}

