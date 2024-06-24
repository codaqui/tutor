from django.shortcuts import render
from wallet.models import Activities
from django.contrib.auth.decorators import login_required

@login_required
def history_profile(request):
    user_data = Activities.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'wallet/wallet_profile.html', {'user_data': user_data})

