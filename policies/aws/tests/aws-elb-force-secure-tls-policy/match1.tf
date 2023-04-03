resource "aws_alb_listener" "allows_tls_1.1" {
  ssl_policy = "ELBSecurityPolicy-TLS-1-1-2017-01"
  protocol   = "HTTPS"
}
