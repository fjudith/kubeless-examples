# Kubernetes list deployments

List all deployments of a given cluster.
Return a JSON containing the full-configuration of each deployments.

## List Deployments

Expose the NATS cluster locally.

```bash
kubectl -n nats-io port-forward nats-cluster:4222
```

Execute the following command to list Deployment objects.

```bash
NATS_ADDRESS=localhost:4222

python3 list-deployments.py
```

```text
...
'kind': 'DeploymentList',
 'metadata': {'_continue': None,
              'resource_version': '6244278',
              'self_link': '/apis/apps/v1/deployments'}}
```

## Publish Deployments

Expose the NATS cluster locally.

```bash
kubectl -n nats-io port-forward nats-cluster:4222
```

Execute the following command to list Deployment objects.

```bash
NATS_ADDRESS=localhost:4222

python3 publish-deployments.py
```

```text
...
2020-01-15 00:30:58,969 - script - INFO - Deployment: kubeless kubeless-controller-manager Replicas:1
2020-01-15 00:30:59,072 - script - INFO - Deployment: harbor harbor-harbor-registry Replicas:1
2020-01-15 00:30:59,174 - script - INFO - Deployment: bookinfo reviews-v1 Replicas:1
2020-01-15 00:30:59,278 - script - INFO - Deployment: rook-ceph rook-ceph-osd-1 Replicas:1
```

## Test environment

Scripts are validated on the using the following environment.

* [Kubernetes](https://github.com/kubernetes/kubernetes): `v1.16.3`
* [Nats operator](https://github.com/nats-io/nats-operator): `v0.6.0`
* [Nats cluster](https://github.com/nats-io/nats-server): `v2.1.2`
