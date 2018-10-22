# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView
from django.shortcuts import redirect
from django.core.urlresolvers import reverse_lazy
from django.utils import timezone

from .models import Experiment, Image
from .forms import ScaleForm
from .kube import start_job, stop_job, scale_job


class ExperimentListView(ListView):
    model = Experiment
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super(ExperimentListView, self).get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


class ExperimentCreateView(CreateView):
    model = Experiment
    template_name = 'create.html'
    fields = ['parallel', 'parameters', 'hostnetwork', 'image']


class ExperimentDetailView(DetailView):
    model = Experiment
    template_name = 'view.html'

    def get_context_data(self, **kwargs):
        context = super(ExperimentDetailView, self).get_context_data(**kwargs)
        context['scale_form'] = ScaleForm()
        return context


def start_experiment(request, pk):
    experiment = Experiment.objects.get(id=pk)
    if request.method == 'POST':
        experiment.start_date = timezone.now()
        experiment.save()
        start_job(experiment)
    return redirect(experiment.get_absolute_url())


def stop_experiment(request, pk):
    experiment = Experiment.objects.get(id=pk)
    if request.method == 'POST':
        experiment.end_date = timezone.now()
        experiment.save()
        stop_job(experiment)
    return redirect(experiment.get_absolute_url())


def scale_experiment(request, pk):
    experiment = Experiment.objects.get(id=pk)
    if request.method == 'POST':
        form = ScaleForm(request.POST, instance=experiment)
        if form.is_valid():
            form.save()
            scale_job(experiment)
    return redirect(experiment.get_absolute_url())


class ImageCreateView(CreateView):
    model = Image
    template_name = 'create_image.html'
    fields = ['tarfile', 'tag']
    success_url = reverse_lazy('image-index')


class ImageListView(ListView):
    model = Image
    template_name = 'index_image.html'
