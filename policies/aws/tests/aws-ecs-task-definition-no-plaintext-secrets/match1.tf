resource "aws_ecs_task_definition" "plaintext_password" {
  family                = "service"
  container_definitions = <<CONTAINER_DEF
 [
   {
     "name": "my_service",
     "essential": true,
     "memory": 256,
     "environment": [
       { "name": "ENVIRONMENT", "value": "dev" },
       { "name": "API_TOKEN", "value": "ohsosecret123"}
     ]
   }
 ]
 CONTAINER_DEF
}
