from django.shortcuts import render
from address.models import Address

from .forms import ExampleForm


def home(request):
    if request.method == 'POST':
        form = ExampleForm(request.POST)
        if form.is_valid():
            pass
    else:
        addresses = Address.objects.all()
        if addresses.exists():
            inst = {
                'address': addresses[0],
            }
        else:
            inst = None
        form = ExampleForm(initial=inst)
    return render(request, 'example/home.html', {'form': form})
