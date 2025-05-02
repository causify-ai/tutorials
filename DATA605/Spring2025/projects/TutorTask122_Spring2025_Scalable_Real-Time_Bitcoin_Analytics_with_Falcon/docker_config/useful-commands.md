### check all running containers 
docker ps
docker ps -a # includeds exited containers

### start a stopped container
docker start container_name

### clean up all containers
docker rm -f $(docker ps -aq)

### build container and run 
docker-compose up --build

### jump into container
docker exec -it falcon_container /bin/bash
cd /app 
ls 
python3 ___.p

### get interactive in containers
docker run -it <image_name_here> /bin/bash
docker run -it umd_data605/umd_data605_template /bin/bash
get interactive in containers with mounted directory
docker run -it -v "$(pwd)/../app":/app umd_data605/umd_data605_template /bin/bash

### get a secondary shell on a running container
docker exec -it <container id from docker ps> /bin/bash
