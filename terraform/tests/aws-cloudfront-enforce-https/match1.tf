locals {
  allow_all_s3_origin_id = "allow_all_origin"
}

resource "aws_cloudfront_distribution" "allow_all" {
  origin {
    domain_name              = "s3.amazonaws.com"
    origin_access_control_id = "my_access_control_id"
    origin_id                = local.allow_all_s3_origin_id
  }

  enabled             = true
  default_root_object = "index.html"

  default_cache_behavior {
    allowed_methods        = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = local.allow_all_s3_origin_id
    viewer_protocol_policy = "allow-all"
  }

  restrictions {
    geo_restriction {
      restriction_type = "whitelist"
      locations        = ["US", "CA", "GB", "DE"]
    }
  }
  viewer_certificate {
    cloudfront_default_certificate = true
  }
}
