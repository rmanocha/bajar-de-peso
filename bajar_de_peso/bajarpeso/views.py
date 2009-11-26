# Create your views here.

from django.http import HttpResponse
from django.shortcuts import render_to_response

from bajar_de_peso.bajarpeso.models import WeightTracker

def main(request):
    if request.method == 'POST':
        print "here"
        return HttpResponse('Welcome!!')
    else:
        return HttpResponse('Thanks')
