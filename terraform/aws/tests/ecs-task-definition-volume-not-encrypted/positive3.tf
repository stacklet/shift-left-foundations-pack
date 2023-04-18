resource "aws_ecs_task_definition" "service_3" {
  family                = "service"
  container_definitions = file("task-definitions/service.json")

  volume {
    name = "service-storage"

    efs_volume_configuration {
      file_system_id          = aws_efs_file_system.fs.id
      root_directory          = "/opt/data"
      transit_encryption_port = 2999
      transit_encryption      = "ENABLED"
      authorization_config {
        access_point_id = aws_efs_access_point.test.id
        iam             = "ENABLED"
      }
    }
  }

  volume {
    name = "service-storage2"

    efs_volume_configuration {
      file_system_id          = aws_efs_file_system.fs.id
      root_directory          = "/opt/data"
      transit_encryption_port = 2999
      transit_encryption      = "DISABLED"
      authorization_config {
        access_point_id = aws_efs_access_point.test.id
        iam             = "ENABLED"
      }
    }
  }
}
