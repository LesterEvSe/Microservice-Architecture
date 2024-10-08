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
    "group_id": ["id0", ...],
    "group_name": ["name0", ...],
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
    "group_id": ["id0", ...],
    "group_name": ["name0", ...],
    "jwt": "key"
}
```

### Add Group
``` shell
curl -X POST http://localhost:5001/ -H "Content-Type: application/json" -d '{
    "type": "add_group",
    "group": "name",
    "jwt": "key"
}'

return_type {
    "group_id": "id"
}
```

### Delete Group
``` shell
curl -X POST http://localhost:5001/ -H "Content-Type: application/json" -d '{
    "type": "delete_group",
    "group_id": "id",
    "jwt": "key"
}'
```

### Add member to group
``` shell
curl -X POST http://localhost:5001/ -H "Content-Type: application/json" -d '{
    "type": "add_member_to_group",
    "group_id": "id",
    "member": "name",
    "jwt": "key"
}'
```

### Delete member from group
``` shell
curl -X POST http://localhost:5001/ -H "Content-Type: application/json" -d '{
    "type": "delete_member_from_group",
    "group_id": "id",
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
    "member": ["first_member", "second", ...],
    "jwt": "key"
}'

return_type {
    "task_id": "id"
}
```

### Delete task (complete task have the same command)
``` shell
curl -X POST http://localhost:5001/ -H "Content-Type: application/json" -d '{
    "type": "delete_task",
    "group_id": "id",
    "task_id": "id",
    "jwt": "key"
}'
```

### Update task
``` shell
curl -X POST http://localhost:5001/ -H "Content-Type: application/json" -d '{
    "type": "update_task",
    "group_id": "id",
    "task_id": "id",
    "task" "task text with len [1; 100]",
    "description": "text",
    "deadline": "some datetime",
    "todo_task": "True/False",
    "member": ["first_member", "second", ...],
    "jwt": "key"
}'
```

### Get tasks for group
``` shell
curl -X POST http://localhost:5001/ -H "Content-Type: application/json" -d '{
    "type": "get_tasks_for_group",
    "group_id": "id",
    "jwt": "key"
}'

return_type {
    "task_id": ["id0", ...],
    "task_name": ["name0", ...],
    "description": ["desc0", ...],
    "deadline": ["deadline0", ...],
    "todo_task": ["todo_task0", ...]
}
```

### Google auth
I do not know yet.
