from django.contrib.auth.models import User
from django import forms
from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.utils.safestring import mark_safe

class UpdateProfile(forms.ModelForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    username = forms.CharField(required=False, disabled=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')

        if User.objects.filter(email=email).exclude(username=self.username).exists():
            raise forms.ValidationError('This email address is already in use. Please supply a different email address.')

    def save(self, user, commit=True):
        self.full_clean()

        user.email = self.cleaned_data.get('email')
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')

        if commit:
            user.save()

        return user

def update_profile(request):
    if request.method == 'POST':
        form = UpdateProfile(request.POST)
        form.username = request.user.username
        if form.is_valid():
            try:
                form.save(request.user)
                messages.success(request, mark_safe(f"<strong>Thanks {request.user.first_name}!</strong> That's all saved for you."))
                return redirect('/booking')
            except ValidationError as e:
                form.errors.update(e)
                return render(request, 'www/booking/profile.html', {'form': form})
        else:
            return render(request, 'www/booking/profile.html', {'form': form})
    else:
        form = UpdateProfile(instance=request.user)
        return render(request, 'www/booking/profile.html', {'form': form})
