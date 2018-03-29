from django.shortcuts import render
from address.models import Address

from .forms import PersonForm


def home(request):
    if request.method == 'POST':
        form = PersonForm(request.POST)
        if form.is_valid():
            pass
    else:
        form = PersonForm(initial={'address': Address.objects.first()})

    return render(request, 'example/home.html', {'form': form})
