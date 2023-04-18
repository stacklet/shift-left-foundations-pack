resource "aws_opensearch_domain" "https_not_enforced" {
  domain_name    = "https-not-enforced"
  engine_version = "7.10"

  cluster_config {
    instance_type = "r4.large.opensearch"
  }

  domain_endpoint_options {
    enforce_https = false
  }
}
