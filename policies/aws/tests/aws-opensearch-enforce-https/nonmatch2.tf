resource "aws_opensearch_domain" "https_implicitly_enforced" {
  domain_name    = "https-implicitly-enforced"
  engine_version = "7.10"

  cluster_config {
    instance_type = "r4.large.opensearch"
  }
}
