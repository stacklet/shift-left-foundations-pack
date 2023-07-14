resource "aws_alb_listener" "requires_tls_1.2" {
  ssl_policy = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  protocol   = "HTTPS"
}
