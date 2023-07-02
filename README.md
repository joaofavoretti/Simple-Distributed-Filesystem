# Simple-Distributed-Filesystem

This is a very simple example of how a Distributed Filesystem would work.

It has three components:

## Metadata Server

This application is used to keep track of an index of where each file is on the filesystem, and to check which Storage Node is available to be connected to.

## Storage Node

This application is the one that really stores the files. When it runs, it requests a connection to the Metadata Server to informe it that the node now exists.

## Client Application

That application is what the used interacts with. It deals with the problem of requesting the correct ip address of the Storage Nodes to request for file operations.

## Running

As it is an example of a distributed computer program, each part of the program is supposed to run in a different node of a cluster. In order to simulate that behavior locally in a single computer, it was used Docker Compose to spawn different containers, each of them with a single module of the software.

The Docker Compose creates a simple bridged network `11.56.1.0/24` and sets the Metadata Server at the address `11.56.1.21` arbitrarily. Besides that it spawns three Storage Nodes at the address `11.56.1.41`, `11.56.1.42`, `11.56.1.43`. As it is a Distributed Systems software, the number of Storage Nodes can be as high as you can think, it is 3 by default to avoid spending too much resources locally. Also, as each Storage Node would have its own filesystem to really store the files, the docker compose solution to this is to create a directory in the main operating system for each of the containers to use (they are called: `storage-node-1`, `storage-node-2` and `storage-node-3`).

It is easy to run it in a single command with Docker Compose. Assuming you have it installed (if you need any reference, take [this]([Title](https://www.youtube.com/watch?v%253DDM65_JyGxCo)) video), just run the command.

```
docker-compose up
```

With that up and running, just run the Client App in another terminal window by entering in the `client-app` directory, installing the required libraries placed on the `requirements.txt` file, and running it.

```
python3 client_app.py
```

You will be prompted with a `>` character supposed to be used as a prompt to your file system, just like you would with you were to use a linux terminal. With that, you can type commands to used any of the implemented features it has, like:

- Upload files that you have locally to your remote filesystem
- Download files that you have uploaded to your computer
- List all the files that are on the filesystem
- `cat` the content of a file
- Remove a file that is on the filesystem
