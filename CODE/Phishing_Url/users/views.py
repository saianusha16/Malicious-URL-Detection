# views.py
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import numpy as np
import pickle
import os
from django.conf import settings
from users.app.feature import FeatureExtraction


def UserHome(request):
    return render(request, 'users/userhome.html')

#==================================================================

def ModelMetrics(request):
    return render(request, 'users/metrics.html')

#==================================================================

def Model_Training(request):
    '''
        if you are here looking for the ML code,
        please go and check the 
        1.Phishing URL Detection.ipynb file.
        2. inside users/app/main_code.py.
    '''
    return render(request, 'users/Model_Training.html')


#=====================================================================================================

# Load the model
model_path = os.path.join(settings.MEDIA_ROOT,'model.pkl')
with open(model_path, "rb") as file:
    gbc = pickle.load(file)

@csrf_exempt
def index(request):
    if request.method == "POST":
        url = request.POST.get("url")
        obj = FeatureExtraction(url)
        x = np.array(obj.getFeaturesList()).reshape(1, 30)

        y_pred = gbc.predict(x)[0]
        y_pro_phishing = gbc.predict_proba(x)[0, 0]
        y_pro_non_phishing = gbc.predict_proba(x)[0, 1]

        pred = "It is {0:.2f} % safe to go ".format(y_pro_phishing * 100)
        context = {
            'xx': round(y_pro_non_phishing, 2),
            'url': url,
        }
        return render(request, 'users/urlcheck.html', context)
    
    return render(request, 'users/urlcheck.html', {'xx': -1})

#=====================================================================================================

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from .models import UserRegisterModel

def forgot_password(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        
        try:
            user = UserRegisterModel.objects.get(username=username)
            request.session['reset_username'] = username  # Store username in session
            return redirect('reset_password')  # Redirect to the reset password page
        except UserRegisterModel.DoesNotExist:
            messages.error(request, 'User does not exist.')

    return render(request, 'users/forgot_password.html')  # Render forgot password page


def reset_password(request):
    username = request.session.get('reset_username')  # Retrieve username from session
    if not username:
        messages.error(request, 'Invalid session. Please try again.')
        return redirect('forgot_password')

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password == confirm_password:
            try:
                user = UserRegisterModel.objects.get(username=username)
                user.password = new_password # Hash the password before saving
                user.save()
                messages.success(request, 'Password updated successfully! Please login.')
                del request.session['reset_username']  # Clear session data
                return redirect('login')  # Redirect back to login page
            except UserRegisterModel.DoesNotExist:
                messages.error(request, 'User does not exist.')
        else:
            messages.error(request, 'Passwords do not match.')
    
    return render(request, 'users/reset_password.html', {'username': username})
