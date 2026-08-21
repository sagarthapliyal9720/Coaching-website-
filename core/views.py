from django.shortcuts import render

# Create your views here.
# core/views.py
from django.shortcuts import render

def home(request):
    """Renders the static homepage."""
    return render(request, 'core/index.html')