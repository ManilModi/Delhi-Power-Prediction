import random
import string
from django import forms
from django.core.mail import send_mail
from .models import Userstable,Roles,UserRole
from django.conf import settings

class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=50)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

class UserRegistrationForm(forms.ModelForm):
    role = forms.ModelChoiceField(
        queryset=Roles.objects.exclude(role_names__in=['Admin', 'Government Engineer']),
        required=True,
        label="Select Role"
    )

    class Meta:
        model = Userstable
        fields = ['username', 'password']
        widgets = {
            'password': forms.PasswordInput(),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            role = self.cleaned_data['role']
            UserRole.objects.create(user=user, role=role)  # Link user to role
        return user

# Function to Generate Random Password
def generate_random_password(length=8):
    characters = string.ascii_letters + string.digits  # Letters + Numbers
    return ''.join(random.choice(characters) for _ in range(length))

# Admin-Only Form to Create Admin/Govt. Engineers
class AdminUserCreationForm(forms.ModelForm):
    role = forms.ModelChoiceField(
        queryset=Roles.objects.filter(role_names__in=['Admin', 'Government Engineer']),
        required=True,
        label="Select Role"
    )

    class Meta:
        model = Userstable
        fields = ['username']  # No password field since we generate it

    def save(self, commit=True):
        user = super().save(commit=False)
        password = generate_random_password()  # Generate random password
        user.password = password  # Hash and store password

        if commit:
            user.save()
            role = self.cleaned_data['role']
            UserRole.objects.create(user=user, role=role)  # Assign role

            # Send email with credentials
            send_mail(
                subject="Your Account Credentials",
                message=f"Hello {user.username},\n\nYour account has been created.\nUsername: {user.username}\nPassword: {password}\n\n",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.username],  # Assuming username is the email
                fail_silently=False,
            )

        return user  

class PasswordChangeForm(forms.Form):
    username = forms.CharField(max_length=50, label='User Email (Username)', widget=forms.TextInput(attrs={'class': 'form-control'}))

# class NormalUserForm(forms.Form):
#     USER_TYPE_CHOICES = [
#         ('Journlaist', 'Journalist'),
#         ('Student', 'Student'),
#     ]

#     username = forms.CharField(label='Username', max_length=50)
#     password = forms.CharField(label='Password', widget=forms.PasswordInput)
#     user_type = forms.ChoiceField(label='User Type', choices=USER_TYPE_CHOICES)

# class EntrepreneurForm(forms.Form):
#     username = forms.CharField(label='Username', max_length=50)
#     password = forms.CharField(label='Password', widget=forms.PasswordInput)
#     company_name = forms.CharField(label='Company Name', max_length=255, required=False)


# class GovernmentEngineerForm(forms.Form):
#     username = forms.CharField(label='Username', max_length=50)
#     password = forms.CharField(label='Password', widget=forms.PasswordInput)
#     department = forms.CharField(label='Department', max_length=255, required=False)


# class ResearcherForm(forms.Form):
#     username = forms.CharField(label='Username', max_length=50)
#     password = forms.CharField(label='Password', widget=forms.PasswordInput)
#     institution = forms.CharField(label='Institution', max_length=255, required=False)


# class AdminForm(forms.Form):
#     username = forms.CharField(label='Username', max_length=50)
#     password = forms.CharField(label='Password', widget=forms.PasswordInput)


