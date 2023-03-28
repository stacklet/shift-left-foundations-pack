resource "aws_opensearch_domain" "https_explicitly_enforced" {
  domain_name    = "https-explicitly-enforced"
  engine_version = "7.10"

  cluster_config {
    instance_type = "r4.large.opensearch"
  }

  domain_endpoint_options {
    enforce_https = true
  }
}
