#!/usr/bin/env python
import asyncio
import argparse
import json
import logging
import os

from kubernetes import client, config, watch

from nats.aio.client import Client as NATS
from nats.aio.errors import ErrConnectionClosed, ErrTimeout, ErrNoServers

parser = argparse.ArgumentParser()
parser.add_argument('--in-cluster', help="use in cluster kubernetes config", action="store_true")
parser.add_argument('-l', '--selector', help="Selector (label query) to filter on, supports '=', '==', and '!='.(e.g. -l key1=value1,key2=value2)", default='nightly-shutdown=true')
parser.add_argument('-a', '--nats-address', help="address of nats cluster", default=os.environ.get('NATS_ADDRESS', None))
parser.add_argument('-d', '--debug', help="enable debug logging", action="store_true")
parser.add_argument('--output-deployments', help="output all deployments to stdout", action="store_true", dest='enable_output')
parser.add_argument('--connect-timeout', help="NATS connect timeout (s)", type=int, default=10, dest='conn_timeout')
parser.add_argument('--max-reconnect-attempts', help="number of times to attempt reconnect", type=int, default=1, dest='conn_attempts')
parser.add_argument('--reconnect-time-wait', help="how long to wait between reconnect attempts", type=int, default=10, dest='conn_wait')
args = parser.parse_args()

logger = logging.getLogger('script')
ch = logging.StreamHandler()
if args.debug:
    logger.setLevel(logging.DEBUG)
    ch.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)
    ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

if not args.nats_address:
    logger.critical("No NATS cluster specified")
    exit(parser.print_usage())
else:
    logger.debug("Using nats address: %s", args.nats_address)

if args.in_cluster:
    config.load_incluster_config()
else:
    try:
        config.load_kube_config()
    except Exception as e:
        logger.critical("Error creating Kubernetes configuration: %s", e)
        exit(2)

# Client to list namespaces
CoreV1Api = client.CoreV1Api()

# Client to list Deployments and StatefulSets
AppsV1Api = client.AppsV1Api()


async def run(loop):
    nc = NATS()
    try:
        await nc.connect(args.nats_address, loop=loop, connect_timeout=args.conn_timeout, max_reconnect_attempts=args.conn_attempts, reconnect_time_wait=args.conn_wait)
    except Exception as e:
        exit(e)

    async def get_resources():
        w = watch.Watch()
        for ns in w.stream(CoreV1Api.list_namespace, label_selector=args.selector):
            logger.info("Namespace: %s Labels: %s" % (ns['object'].metadata.name, ns['object'].metadata.labels))
            msg = {'type':ns['type'],'object':ns['raw_object']}
            if args.enable_output:
                print(json.dumps(msg))
            
            for deploy in w.stream(AppsV1Api.list_namespaced_deployment, ns['object'].metadata.name):
                logger.info("Namespace: %s Deployment: %s Replica: %s" % (deploy['object'].metadata.namespace, deploy['object'].metadata.name, deploy['object'].spec.replicas))
                msg = {'type':deploy['type'],'object':deploy['raw_object']}
                if args.enable_output:
                    print(json.dumps(msg))
                
                await nc.publish("k8s_deployment_replicas", json.dumps(msg).encode('utf-8'))
                await asyncio.sleep(0.1)

                for sts in w.stream(AppsV1Api.list_namespaced_stateful_set, ns['object'].metadata.name):
                    logger.info("Namespace: %s StatefulSet: %s Replica: %s" % (sts['object'].metadata.namespace, sts['object'].metadata.name, sts['object'].spec.replicas))
                    msg = {'type':sts['type'],'object':sts['raw_object']}
                    if args.enable_output:
                        print(json.dumps(msg))
                    
                    await nc.publish("k8s_statefulset_replicas", json.dumps(msg).encode('utf-8'))
                    await asyncio.sleep(0.1)

    await get_resources()
    await nc.close()




if __name__ == '__main__':

    loop = asyncio.get_event_loop()
    loop.create_task(run(loop))
    try:
        loop.run_forever()
        logger.info("Namespace: %s Deployment: %s Replica: %s" % (deploy['object'].metadata.namespace, deploy['object'].metadata.name, deploy['object'].spec.replicas))
        logger.info("Namespace: %s StatefulSet: %s Replica: %s" % (sts['object'].metadata.namespace, sts['object'].metadata.name, sts['object'].spec.replicas))
    except KeyboardInterrupt:
        logger.info('keyboard shutdown')
        tasks = asyncio.gather(*asyncio.Task.all_tasks(loop=loop), loop=loop, return_exceptions=True)
        tasks.add_done_callback(lambda t: loop.stop())
        tasks.cancel()

        # Keep the event loop running until it is either destroyed or all
        # tasks have really terminated
        while not tasks.done() and not loop.is_closed():
            loop.run_forever()
    finally:
        logger.info('closing event loop')
        loop.close()