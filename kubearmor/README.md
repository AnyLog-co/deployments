# KubeArmor 

* [Kuberarmor Documentation](https://docs.kubearmor.io/kubearmor/)
 
## Steps 
1. Declare repo in _Helm_
```shell
helm repo add kubearmor https://kubearmor.github.io/charts

helm repo update kubearmor

helm upgrade --install kubearmor-operator kubearmor/kubearmor-operator -n kubearmor --create-namespace
```

2. Install _karmor_ CLI
```shell
curl -sfL http://get.kubearmor.io/ | sudo sh -s -- -b /usr/local/bin
```

3. Deploy KubeArmor 
```shell
kubectl apply -f kubearmor.yaml
```

4. Start karmor gRPC client
```shell
#  Observe Logs from KubeArmor
karmor logs --json [--namespace default]

# Collect system dump information for troubleshooting and error report
karmor sysdump --json
```
**Sample Output**: 
```shell
POD=$(kubectl get pod -l app=nginx -o name)
kubectl exec -it ${POD} -- bash -c "apt-get -y update && apt-get -y upgrade"

<< COMMENT
# output 
orishadmon@Oris-Mac-mini ~ % karmor logs --json 
local port to be used for port forwarding kubearmor-relay-848df88d96-z6c4h: 32797 
Created a gRPC client (localhost:32797)
Checked the liveness of the gRPC server
Started to watch alerts
{"Timestamp":1703125199,"UpdatedTime":"2023-12-21T02:19:59.038465Z","ClusterName":"default","HostName":"minikube","NamespaceName":"default","Owner":{"Ref":"Deployment","Name":"nginx","Namespace":"default"},"PodName":"nginx-7c5ddbdf54-pzwbr","Labels":"app=nginx","ContainerID":"0fa8eafa5f8d6aed126cf31676ea7e60c18482f12500cf70464013cb7e330a3a","ContainerName":"nginx","ContainerImage":"nginx:latest@sha256:bd30b8d47b230de52431cc71c5cce149b8d5d4c87c204902acf2504435d4b4c9","HostPPID":347993,"HostPID":347999,"PPID":37,"PID":43,"UID":0,"ParentProcessName":"/usr/bin/bash","ProcessName":"/usr/bin/apt-get","PolicyName":"block-pkg-mgmt-tools-exec","Severity":"1","Type":"MatchedPolicy","Source":"/usr/bin/bash","Operation":"Process","Resource":"/usr/bin/apt-get -y update","Data":"syscall=SYS_EXECVE","Enforcer":"eBPF Monitor","Action":"Audit (Block)","Result":"Passed"}
{"Timestamp":1703125200,"UpdatedTime":"2023-12-21T02:20:00.470294Z","ClusterName":"default","HostName":"minikube","NamespaceName":"default","Owner":{"Ref":"Deployment","Name":"nginx","Namespace":"default"},"PodName":"nginx-7c5ddbdf54-pzwbr","Labels":"app=nginx","ContainerID":"0fa8eafa5f8d6aed126cf31676ea7e60c18482f12500cf70464013cb7e330a3a","ContainerName":"nginx","ContainerImage":"nginx:latest@sha256:bd30b8d47b230de52431cc71c5cce149b8d5d4c87c204902acf2504435d4b4c9","HostPPID":345442,"HostPID":347993,"PPID":338564,"PID":37,"UID":0,"ProcessName":"/usr/bin/apt-get","PolicyName":"block-pkg-mgmt-tools-exec","Severity":"1","Type":"MatchedPolicy","Operation":"Process","Resource":"/usr/bin/apt-get -y upgrade","Data":"syscall=SYS_EXECVE","Enforcer":"eBPF Monitor","Action":"Audit (Block)","Result":"Passed"}
<< COMMENT 
```

[kubearmor.json]( Kubearmor/kubearmor.json) provides a clear output of the sample data. 

## Current Issues 
1. _Karmor_ is using a different port each time we run it -- is there a way to make it static?
2. We configured _nginx_ service to NodePort, is it possible to do the same with karmar in order to send the data to our gRPC client?
3. any other approach to connect and receive the logs (to a third party app)?
4. Anything else that we need to consider?


