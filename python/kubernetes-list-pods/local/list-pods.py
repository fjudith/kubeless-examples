from kubernetes import client, config, watch
import argparse
import json
import logging
import os
from kubernetes.client.rest import ApiException
from pprint import pprint

parser = argparse.ArgumentParser()
parser.add_argument('--in-cluster', help="use in cluster kubernetes config", action="store_true")
parser.add_argument('-d', '--debug', help="enable debug logging", action="store_true")
parser.add_argument('-t', '--timeout', help="timout seconds", default='30')
parser.add_argument('-p', '--pretty', help="pretty printed output", action="store_true")
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

if args.in_cluster:
    config.load_incluster_config()
else:
    try:
        config.load_kube_config()
    except Exception as e:
        logger.critical("Error creating Kubernetes configuration: %s", e)
        exit(2)

v1 = client.CoreV1Api()
w = watch.Watch()

try:
    api_response = v1.list_pod_for_all_namespaces()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CoreV1Api->list_pod_for_all_namespaces: %s\n" % e)
