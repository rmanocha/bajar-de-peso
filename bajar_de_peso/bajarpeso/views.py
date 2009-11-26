# Create your views here.

from django.http import HttpResponse

from bajar_de_peso.bajarpeso.models import WeightTracker

def main(request):
    return HttpResponse('Thanks')
