resource "aws_ecs_task_definition" "no_secrets_here" {
  family                = "service"
  container_definitions = <<EOF
 [
   {
     "name": "my_service",
     "essential": true,
     "memory": 256,
     "environment": [
       { "name": "ENVIRONMENT", "value": "development" }
     ]
   }
 ]
 EOF
}
