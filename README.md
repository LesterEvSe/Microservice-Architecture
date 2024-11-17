# Microservice Architecture

## Clone
To clone repo with all submodules  
`git clone --recurse-submodules https://github.com/LesterEvSe/Microservice-Architecture`  

To update submodules code  
`git submodule update --remote --merge`

For get k8s files use the command:
`kompose convert`

Connect to DB:
`docker exec -it <container-id> psql -U <username> -d <db-name>`
