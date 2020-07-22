from django.contrib.auth import logout
from django.urls import reverse
from django.http import HttpResponseRedirect

def signup(request):
    logout(request)
    return HttpResponseRedirect(reverse('account_signup'))


def login(request):
    logout(request)
    return HttpResponseRedirect(reverse('account_login'))
