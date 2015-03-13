from django.shortcuts import render
from .forms import ExampleForm

def home(request):
    form = ExampleForm()
    return render(request, 'example/home.html', {'form': form})
