from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.shortcuts import render, redirect
import random
from .forms import RegistrationForm


def check_data(password1, password2):
    try:
        validate_password(password1)
    except ValidationError as e:
        error_message = ', '.join(e.messages)
        return error_message

    if password1 != password2:
        error_message = 'The passwords are not the same.'
        return error_message

    return ''


def registration(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        username = request.POST.get('username')
        request.session['username'] = username
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        error_message = check_data(password1, password2)

        if error_message:
            return render(request, 'registration/error_registration.html', {'error_message': error_message})

        activation_code = random.randint(1000, 9999)
        request.session['activation_code'] = activation_code

        send_mail(
            "Confirm your registration",
            f"Please confirm your email address to get full access to DjangoGram.\n {activation_code}",
            'viktor.zakora@gmail.com',
            [email],
            fail_silently=False
        )

        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            form.save()

        return render(request, 'registration/welcome.html', {'username': username, 'email': email})

    else:
        form = RegistrationForm()

    return render(request, 'registration/registration.html', {'form': form})


def activate_account(request):
    if request.method == 'POST':
        user_entered_code = int(request.POST.get('user_entered_code'))
        activation_code = request.session.get('activation_code')

        if user_entered_code == activation_code:
            user = User.objects.get(username=request.session.get('username'))
            user.is_active = True
            user.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            return redirect('home')

        else:
            error_message = 'Invalid activation code. Please try again.'
            return render(request, 'registration/error_registration.html', {'error_message': error_message})

