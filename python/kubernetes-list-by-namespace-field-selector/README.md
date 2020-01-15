
# Kubernetes list replica on given namespace label selector

List all deployments and statefulsets replicas of namespaces containing the label `nightly-shutdown=true`.
Return a message containing number replica of both resources.

## List replicas

Expose the NATS cluster locally.

```bash
kubectl -n nats-io port-forward nats-cluster:4222
```

Create a namespace and create the deployment and the statefulset for testing purposes

```bash
kubectl create namespace demo

kubectl label namespace demo nightly-shutdown=true
kubectl -n demo apply -f manifests/deployment.yaml
kubectl -n demo apply -f manifests/statefulset.yaml
```

Execute the following command to list the replicas of `Deployment` and `StatefulSet` resources.

```bash
NATS_ADDRESS=localhost:4222

python3 list-replicabynamespacelabelselector.py
```

```text
...
2020-01-15 15:00:31,035 - script - INFO - Namespace: demo Deployment: web Replica: 3
2020-01-15 15:00:31,067 - script - INFO - Namespace: demo StatefulSet: web Replica: 3
```

## Test environment

Scripts are validated on the using the following environment.

* [Kubernetes](https://github.com/kubernetes/kubernetes): `v1.16.3`
* [Nats operator](https://github.com/nats-io/nats-operator): `v0.6.0`
* [Nats cluster](https://github.com/nats-io/nats-server): `v2.1.2`
* [Kubefwd](https://github.com/txn2/kubefwd): `1.11.1`

## References

* <https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/CoreV1Api.md#list_namespace>
* <https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/AppsV1Api.md#list_namespaced_deployment>
