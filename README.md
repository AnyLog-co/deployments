# Deploying AnyLog 

## Requirements 
* [docker-compose](https://github.com/AnyLog-co/documentation/blob/master/Docker%20Compose%20&%20Kubernetes.md)
* [kompose](https://kompose.io/installation/) - A conversion tool for Docker Compose to container orchestrators such as Kubernetes (or OpenShift).
* [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/) - Kubernetes command line tool
* [minikube](https://minikube.sigs.k8s.io/docs/start/) - local Kubernetes, focusing on making it easy to learn and develop for Kubernetes.

## Prepare Deployment 
1. Clone & cd into docker-compose dir 
```bash
cd $HOME
git clone https://github.com/AnyLog-co/docker-compose
cd $HOME/docker-compose 
```

## Docker Compose 
* Where to update deployment configurations [envs](envs/)
  * [AnyLog Network](envs/anylog_node.env) 
  * [AnyLog GUI](envs/anylog_gui.env)
  * [AnyLog REST Tool](envs/remote_cli.env) 
  * [Postgres](envs/postgres.env)
  * [Grafana](envs/grafana.env)
  
* How to start docker-compose
```bash
cp docker-compose-base.yml docker-compose.yml 
docker-compose up -d 
```

* cURL request against AnyLog-Network -- `anylog-node` service uses the `network_mode: host` rather than the network created by the network. As such, AnyLog uses the same IP(s) as the machine it seats on. 
```bash
curl -X GET ${YOUR_IP}:3481 -H "commnad: get status" -H "Usr-Agent: AnyLog/1.23"
```

* How to attach to AnyLog
```bash
docker attach --detach-keys="ctrl-d" anylog-node
```

* How to access Volume(s)
```bash
# Locate the Mountpoint 
docker volume inspect docker-compose_anylog-node-local-scripts 
[
    {
        "CreatedAt": "2022-02-08T22:46:36Z",
        "Driver": "local",
        "Labels": {
            "com.docker.compose.project": "docker-compose",
            "com.docker.compose.version": "1.25.0",
            "com.docker.compose.volume": "anylog-node-local-scripts"
        },
        "Mountpoint": "/var/lib/docker/volumes/docker-compose_anylog-node-local-scripts/_data",
        "Name": "docker-compose_anylog-node-local-scripts",
        "Options": null,
        "Scope": "local"
    }
]

# Use sudo command to access directory / files  
sudo ls /var/lib/docker/volumes/docker-compose_anylog-node-local-scripts/_data
hidden_node.al  local_script.al  master.al  mqtt.al  operator.al  publisher.al  query.al  rest_init.al  single_node.al  single_node_publisher.al
```

* How to stop docker-compose - when adding `-v` the the end of the command, user will also delete the volume(s)
```commandline
docker-compose down
```


## kubernetes
* Configure Credentials
```bash
bash $HOME/docker-compose/credentials.sh ${YOUR_IP}
```

* 