# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
import os

from django.db import models
from django.db.models.signals import post_save
from django.urls import reverse
from django.dispatch import receiver
from django.conf import settings

from kubernetes import client

from .dockerbuild import build_and_push


def c_filename(instance, name):
    dir_name, file_name = os.path.split(name)
    file_root, file_ext = os.path.splitext(file_name)
    name = os.path.join(dir_name, instance.tag, "%s%s" % (file_root, file_ext))
    return name


class Image(models.Model):
    tarfile = models.FileField(upload_to=c_filename)
    tag = models.CharField(unique=True, max_length=128)
    build_started = models.BooleanField(default=False)
    builded = models.BooleanField(default=False)

    def __str__(self):
        return 'Image %d - %s' % (self.id, self.tag)

    @property
    def full_tag_local(self):
        return settings.REGISTRY_LOCAL + self.tag

    @property
    def full_tag_external(self):
        return settings.REGISTRY_EXTERNAL + self.tag

    def build(self):
        self.build_started = True
        self.save()
        build_and_push(self)
        self.builded = True
        self.save()


@receiver(post_save, sender=Image)
def image_post_save(sender, instance, created, *args, **kwargs):
    if created:
        instance.build()


class Experiment(models.Model):
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    parallel = models.PositiveIntegerField()
    parameters = models.CharField(max_length=500)
    hostnetwork = models.BooleanField(default=False)
    image = models.ForeignKey(Image)

    def set_parameters(self, parameters):
        self.parameters = json.dumps(parameters)

    def get_parameters(self):
        return json.loads(self.parameters)

    @property
    def started(self):
        return self.start_date is not None

    @property
    def stopped(self):
        return self.end_date is not None

    @property
    def running(self):
        return self.started and not self.stopped

    def format_arguments(self):
        return self.parameters.split(', ')

    @property
    def environment(self):
        return {
            'INFLUX_HOST': settings.INFLUX_HOST,
            'INFLUX_DATABASE': settings.INFLUX_DATABASE,
            'EXPERIMENT_ID': str(self.id),
        }

    @property
    def kube_name(self):
        return 'experiment-%d' % (self.id)

    @property
    def kube_env(self):
        kube_env = []
        for key, value in self.environment.items():
            kube_env.append(client.V1EnvVar(name=key, value=value))
        pod_name_value = client.V1EnvVarSource(field_ref=client.V1ObjectFieldSelector(field_path='metadata.name'))
        kube_env.append(client.V1EnvVar(name='POD_NAME', value_from=pod_name_value))
        return kube_env

    @property
    def kube_podspec(self):
        return client.V1PodSpec(
            containers=[
                client.V1Container(
                    name='experiment',
                    image=self.image.full_tag_external,
                    env=self.kube_env,
                    args=self.format_arguments(),
                    image_pull_policy='IfNotPresent'
                )
            ],
            host_network=self.hostnetwork,
            restart_policy='OnFailure'
        )

    @property
    def kube_pod(self):
        return client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(labels={'name': 'curl'}),
            spec=self.kube_podspec
        )

    @property
    def kube_jobspec(self):
        return client.V1JobSpec(
            parallelism=self.parallel,
            template=self.kube_pod
        )

    @property
    def kube_job(self):
        return client.V1Job(
            api_version='batch/v1',
            kind='Job',
            metadata=client.V1ObjectMeta(name=self.kube_name),
            spec=self.kube_jobspec
        )

    def get_absolute_url(self):
        return reverse('experiment-detail', kwargs={'pk': self.id})

    def __str__(self):
        return 'Experiment %d' % self.id
