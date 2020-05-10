from django.conf import settings
from django.shortcuts import render

from address.models import Address
from .forms import PersonForm


def home(request):
    success = False
    addresses = Address.objects.all()
    if settings.GOOGLE_API_KEY:
        google_api_key_set = True
    else:
        google_api_key_set = False

    if request.method == 'POST':
        form = PersonForm(request.POST)
        if form.is_valid():
            success = True
    else:
        form = PersonForm(initial={'address': Address.objects.last()})

    context = {'form': form,
               'google_api_key_set': google_api_key_set,
               'success': success,
               'addresses': addresses}

    return render(request, 'example/home.html', context)
