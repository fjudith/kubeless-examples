
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

## Publish number of replica to NATS periodically

Kubeless `cronjob` function is leveraged to publish amount of replica of Deployment and Statefulset resources on a scheduled basis.

Execute the following command to create a `function` that publish the amount of replica of Namespaces labeled `nightly-shutdown=true`.

> It is required to change the service account to get appropriate RBAC permssions on the Kubernetes API.
> But Kubeless does not support ServiceAccount in Functions currently
> It is then required to patch the generated resource. 

```bash
kubeless function deploy list-replicas --namespace kubeless --runtime python3.6 --handler publish-replicastonats.run --from-file functions/publish-replicastonats.py --dependencies functions/requirements.txt --env NATS_ADDRESS='nats://nats-cluster.nats-io:4222' && \
kubectl apply -n kubeless -f manifests/kubeless-replica-view-rbac.yaml && \
kubectl -n kubeless patch deployment list-replicas -p '{"spec":{"template":{"spec":{"serviceAccountName":"kubeless-replica-view"}}}}'
```

Execute the following command to create a `trigger` that run the `function` every 5 minutes.

```bash
kubeless trigger cronjob create pubk8sreplica --namespace kubeless --function list-replicas --schedule '*/5 * * * *'
```

## Scale down the number of replica on NAT publish event

Execute the following command to deploy the function that captures publish events to the Nats queue in order to reduce the number of replicas.

```bash
kubeless function deploy downscale-replicas --namespace kubeless --runtime python3.6 --handler downscale-replicas.run --from-file functions/downscale-replicas.py --dependencies functions/requirements.txt && \
kubectl apply -n kubeless -f manifests/kubeless-replica-manage-rbac.yaml && \
kubectl -n kubeless patch deployment downscale-replicas -p '{"spec":{"template":{"spec":{"serviceAccountName":"kubeless-replica-manage"}}}}'
```

Execute the following command to create a `trigger` that run the `function` on NATS events.

```bash
kubeless trigger nats create downscale-replicas  --namespace kubeless --function-selector created-by=kubeless,function=downscale-replicas --trigger-topic k8s_replicas
```

## Test environment

Scripts are validated on the using the following environment.

* [Kubernetes](https://github.com/kubernetes/kubernetes): `v1.16.3`
* [Nats operator](https://github.com/nats-io/nats-operator): `v0.6.0`
* [Nats cluster](https://github.com/nats-io/nats-server): `v2.1.2`
* [Kubefwd](https://github.com/txn2/kubefwd): `1.11.1`

## References

* **Kubernetes CoreV1Api** : <https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/CoreV1Api.md#list_namespace>
* **Kubernetes AppsV1Api** : <https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/AppsV1Api.md#list_namespaced_deployment>
* **Crontab Generator**: <https://crontab-generator.org>
* **Python running task concurently**: <https://docs.python.org/3/library/asyncio-task.html#running-tasks-concurrently>
