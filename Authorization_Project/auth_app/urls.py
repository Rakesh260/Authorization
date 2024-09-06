from django.contrib import admin
from django.urls import path, include

import auth_app
from auth_app.views import  Login, Register, VerifyEmail, About

urlpatterns = [
    path('', Login.as_view(), name='login'),
    path('register', Register.as_view(), name='register'),
    path('about', About.as_view(), name='about'),
    path('verify-email/<uidb64>/<token>/', VerifyEmail.as_view(), name='verify_email'),


]