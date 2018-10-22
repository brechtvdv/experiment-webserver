from kubernetes import client, config


try:
    config.load_kube_config()
except IOError:
    print('no kube conf found')


def start_job(experiment):
    batch_api_instance = client.BatchV1Api()
    api_response = batch_api_instance.create_namespaced_job(namespace='default', body=experiment.kube_job)
    return api_response


def stop_job(experiment):
    batch_api_instance = client.BatchV1Api()
    batch_api_instance.delete_namespaced_job(name=experiment.kube_name, namespace='default', body=client.V1DeleteOptions(propagation_policy="Foreground", grace_period_seconds=0))


def scale_job(experiment):
    batch_api_instance = client.BatchV1Api()
    batch_api_instance.patch_namespaced_job(name=experiment.kube_name, namespace='default', body=experiment.kube_job)
