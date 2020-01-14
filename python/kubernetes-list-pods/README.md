# Kubernetes list pods

List all pods of a given cluster.
Return a JSON containing the full-configuration of each pods.

## List Pods

Expose the NATS cluster locally.

```bash
kubectl -n nats-io port-forward nats-cluster:4222
```

Execute the following command to list Pod objects.

```bash
NATS_ADDRESS=localhost:4222

python3 list-pods.py
```

```text
...
'kind': 'PodList',
 'metadata': {'_continue': None,
              'resource_version': '6246061',
              'self_link': '/api/v1/pods'}}
```

## Publish Pods

Expose the NATS cluster locally.

```bash
kubectl -n nats-io port-forward nats-cluster:4222
```

Execute the following command to list Pod objects.

```bash
NATS_ADDRESS=localhost:4222

python3 publish-pods.py
```

```text
...
2020-01-15 00:36:59,272 - script - INFO - Pod: harbor Pod harbor-harbor-jobservice-79867685f8-h2bcl IP: 10.244.196.154
2020-01-15 00:36:59,376 - script - INFO - Pod: sock-shop Pod orders-dd6cddc99-2sbh6 IP: 10.244.248.207
2020-01-15 00:36:59,480 - script - INFO - Pod: kubeless Pod kubeless-nats-events-85c5bdb7cb-ddwt8 IP: 10.244.216.80
2020-01-15 00:36:59,586 - script - INFO - Pod: spinnaker Pod spin-orca-6864456d59-2k9pr IP: 10.244.114.41
```

## Test environment

Scripts are validated on the using the following environment.

* [Kubernetes](https://github.com/kubernetes/kubernetes): `v1.16.3`
* [Nats operator](https://github.com/nats-io/nats-operator): `v0.6.0`
* [Nats cluster](https://github.com/nats-io/nats-server): `v2.1.2`
