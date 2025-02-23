You can see the terminal output (i.e. the container’s stdout/stderr) by running the following command:

    docker logs logger

You can also add the -f flag to follow the logs in real time:

    docker logs -f logger

Once you have the live logs running, you can run some mock data
scripts inside the logger to simulate activity through the 
application.

For example: 

open a console to the logger:

    sudo docker exec -it logger /bin/bash
    cd bash

and then run post.sh to create a sample task
    ./post.sh http://task-server:5000/tasks create_task.json

You should then be able to verify that the task-created and 
estimate-complete kafka topics contain the required events.