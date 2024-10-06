## Additional info
An error of this type can be returned everywhere:
``` shell
return_type {
    "error": "error msg"
}
```
If there is no return type, then either status_ok 200 will be returned or the error described above


## Communication protocol
### Registration
``` shell
curl -X POST http://localhost:5001/ -H "Content-Type: application/json" -d '{
    "type": "registration",
    "username": "Test0",
    "password": "1111",
    "email": "test0@example.com"
}'

return_type {
    "groups": [["some_group_name", "id"], ["groups_name_another", "second_id"]]
    "jwt": "key"
}
```

### LogIn
``` shell
curl -X POST http://localhost:5001/ -H "Content-Type: application/json" -d '{
    "type": "login",
    "username": "Test0",
    "password": "1111"
}'

return_type {
    "groups": ["some", "groups"]
    "jwt": "key"
}
```

### Add Group
``` shell
curl -X POST http://localhost:5001/ -H "Content-Type: application/json" -d '{
    "type": "add_group",
    "jwt": "key"
}'
```

### Delete Group
``` shell
curl -X POST http://localhost:5001/ -H "Content-Type: application/json" -d '{
    "type": "delete_group",
    "jwt": "key"
}'
```

### Add member to group
``` shell
curl -X POST http://localhost:5001/ -H "Content-Type: application/json" -d '{
    "type": "add_member_to_group",
    "jwt": "key"
}'
```

### Delete member from group
``` shell
curl -X POST http://localhost:5001/ -H "Content-Type: application/json" -d '{
    "type": "delete_member_from_group",
    "member": "username",
    "jwt": "key"
}'
```

### Add task
``` shell
curl -X POST http://localhost:5001/ -H "Content-Type: application/json" -d '{
    "type": "add_task",
    "task" "task text with len [1; 100]",
    "description": "text",
    "deadline": "some datetime",
    "todo_task": "True/False",
    "jwt": "key"
}'

return_type {
    "task_id": "id"
}
```

### Delete task (complete task have the same command)
``` shell
curl -X POST http://localhost:5001/ -H "Content-Type: application/json" -d '{
    "type": "add_task",
    "task_id",
    "jwt": "key"
}'
```

### Update task
``` shell
curl -X POST http://localhost:5001/ -H "Content-Type: application/json" -d '{
    "type": "add_task",
    "task_id": "id"
    "task" "task text with len [1; 100]",
    "description": "text",
    "deadline": "some datetime",
    "todo_task": "True/False",
    "jwt": "key"
}'
```

### Get tasks for group
``` shell
curl -X POST http://localhost:5001/ -H "Content-Type: application/json" -d '{
    "type": "add_task",
    "task_id": "id"
    "task" "task text with len [1; 100]",
    "description": "text",
    "deadline": "some datetime",
    "todo_task": "True/False",
    "jwt": "key"
}'
```
