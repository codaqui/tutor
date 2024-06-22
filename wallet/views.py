from django.shortcuts import render
from .models import Activities
from django.contrib.auth.decorators import login_required

@login_required
def history_profile(request):
    data = Activities.objects.filter(user=request.user).order_by('-date')
    return render(request, 'wallet/wallet_profile.html', {'activities': data})

