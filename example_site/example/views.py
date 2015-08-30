from django.shortcuts import render
from .forms import ExampleForm

def home(request):
    if request.method == 'POST':
        form = ExampleForm(request.POST)
        if form.is_valid():
            pass
    else:
        form = ExampleForm()
    return render(request, 'example/home.html', {'form': form})
