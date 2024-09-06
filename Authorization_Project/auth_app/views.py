from lib2to3.fixes.fix_input import context

from django.contrib.messages.context_processors import messages
from django.db.models import Q
from django.shortcuts import render
from django.urls import reverse
from rest_framework.permissions import AllowAny
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.mail import send_mail, EmailMessage
from django.shortcuts import render
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User


class Login(APIView):


    def get(self, request):
        request.session.flush()
        message = None
        context = {'message': message}
        return render(request, 'login_page.html', context)

    def post(self, request):
        try:

            data = request.data
            user_name = data.get('username')
            password = data.get('password')
            message = None
            try:
                user = User.objects.get(username=user_name,password=password)
                if user:
                    if user.is_active:
                        request.session['id'] = user.id
                        request.session['username'] = user_name
                        request.session['email'] = user.email
                        return redirect('about')
                    else:
                        message = 'The User is Inactive'

            except Exception as e:
                message = 'User Does not Exist'
            context = {'message': message,
                       'username': user_name,
                       'password': password}
            return render(request, 'login_page.html', context)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class Register(APIView):

    def post(self, request):
        data = request.data
        user_name = data.get('user_name')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        password = data.get('password')

        if not (first_name and password and email and user_name):
            return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)

        query = Q()
        query = Q(username = user_name) | Q(email= email)
        user_details = User.objects.filter(query)
        if user_details:
            context ={'message' : 'User with email/username already exists.'}
            return render(request, 'sign_up_page.html', context)

        user,created = User.objects.get_or_create(
            username = user_name,
            first_name = first_name,
            last_name = last_name,
            email = email,
            password=password,
            is_active = False

        )
        if created:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            verification_link = request.build_absolute_uri(
                reverse('verify_email', kwargs={'uidb64': uid, 'token': token})
            )

            subject = 'Email Verification'
            message = render_to_string('email_verification.html', {
                'user': user,
                'verification_link': verification_link,
            })
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [email]

            try:
                email = EmailMessage(subject, message, from_email, recipient_list)
                email.content_subtype = 'html'
                email.send()
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return render(request, 'email_verification_sent.html')

    def get(self, request):
        return render(request, 'sign_up_page.html')


class VerifyEmail(APIView):

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            User = get_user_model()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return render(request, 'email_verification_success.html')
        else:
            return render(request, 'verification_failed.html')


class About(APIView):

    def get(self,request):
        user_id = request.session.get('id')
        user_details = User.objects.get(id=user_id)
        context = {'user': user_details}
        return render(request, 'about_page.html', context)