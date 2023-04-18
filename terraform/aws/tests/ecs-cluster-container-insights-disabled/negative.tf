resource "aws_ecs_cluster" "foo" {
  name = "white-hart"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

resource "aws_ecs_cluster" "bar" {
  name = "white-hart"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  setting {
    name  = "otherSetting"
    value = "enabled"
  }
}
