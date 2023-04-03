resource "aws_ecs_task_definition" "plaintext_password" {
  family                = "service"
  container_definitions = <<EOF
 [
   {
     "name": "my_service",
     "essential": true,
     "memory": 256,
     "environment": [
       { "name": "ENVIRONMENT", "value": "development" },
       { "name": "DATABASE_PASSWORD", "value": "ohsosecret123"}
     ]
   }
 ]
 EOF
}
