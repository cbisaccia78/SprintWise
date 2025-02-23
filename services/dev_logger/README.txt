You can see the terminal output (i.e. the container’s stdout/stderr) by running the following command:

    docker logs logger

You can also add the -f flag to follow the logs in real time:

    docker logs -f logger