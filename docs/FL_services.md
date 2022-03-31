# Services
The services folder provides external services that can be used by the federated-learning repo. These services are used by the `docker-compose.yml` file to generate docker containers for use in federated-learning experiments. The `fl-client` & `fl-server` services are part of the repo itself, whereas the gql-interface and katsu are git submodules. If you wish to add an external service, add it as a git submodule.

## Services File Tree
```bash
services
|  README.md
|  katsu_entrypoint.sh
|__fl-client
   |  client.py
   |  Dockerfile
   |  entrypoint.sh
   |  requirements.txt
|__fl-server
   |  Dockerfile
   |  entrypoint.sh
   |  requirements.txt
   |  server.py
|__gql-interface
   |  ...
|__katsu
   |  ...
|__additional-submodules-here (add any new git submodules in this folder)
   |  ...
```

### Fl-Client
This service is used to create a client for a Flower Federated-Learning Experiment. The implementation of this directory should not need to change as it is built to be experiment-agnostic. Instead, experiment-specific code can be generated as described in the [`FL_experiments.md`](FL_experiments.md) file. Then, via docker volumes, each fl-client has a copy of the experiment code added to their docker containers.

### Fl-Server
This service is used to create a server for a Flower Federated-Learning Experiment. Like the Fl-Client, this directory is experiment-agnostic and gets experiment-specific code added to itself via docker volumes.

### Additional Services
Additional external services like `katsu` and `gql-interface` are added via git submodules. If you have any external code you wish to use in the experiment, add it as a git submodule.