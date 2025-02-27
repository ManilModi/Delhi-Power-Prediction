import random
import string
from django import forms
from django.core.mail import send_mail
from .models import Userstable,Roles,UserRole
from django.conf import settings
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

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
import socket
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

class AdminUserCreationForm(forms.ModelForm):
    role = forms.ModelChoiceField(
        queryset=Roles.objects.filter(role_names__in=['Admin', 'Government Engineer']),
        required=True,
        label="Select Role"
    )

    class Meta:
        model = Userstable
        fields = ['username']  # Only Username Field

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if username:
            # Step 1: Check Email Pattern
            try:
                validate_email(username)
            except ValidationError:
                raise forms.ValidationError("Please enter a valid email address as username for Admin or Government Engineer.")

            # Step 2: Check if Email Already Exists
            if Userstable.objects.filter(username=username).exists():
                raise forms.ValidationError("This email is already taken. Please choose a different one.")

            # Step 3: Check if Domain Exists (DNS Lookup)
            domain = username.split('@')[-1]
            try:
                socket.gethostbyname(domain)  # Check if domain exists
            except socket.gaierror:
                raise forms.ValidationError("Invalid email domain. Please enter a valid email address.")

        return username
    
    def save(self, commit=True):
        user = super().save(commit=False)
        password = generate_random_password()
        user.password = password

        if commit:
            user.save()
            role = self.cleaned_data['role']
            UserRole.objects.create(user=user, role=role)
            
            send_mail(
                subject="Your Account Credentials",
                message=f"Hello {user.username},\n\nYour account has been created.\nUsername: {user.username}\nPassword: {password}\n\n",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.username],
                fail_silently=False,
            )

        return user

class PasswordChangeForm(forms.Form):
    username = forms.CharField(max_length=50, label='User Email (Username)', widget=forms.TextInput(attrs={'class': 'form-control'}))

class DeleteCredentialForm(forms.Form):
    username = forms.CharField(
        label="Enter Username (Admin or Government Engineer)",
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            user = Userstable.objects.get(username=username)

            # Fetch user's role
            try:
                user_role = UserRole.objects.get(user=user).role.role_names
            except UserRole.DoesNotExist:
                raise forms.ValidationError("This user has no assigned role and cannot be deleted.")

            # Ensure only Admin or Government Engineer can be deleted
            if user_role not in ['Admin', 'Government Engineer']:
                raise forms.ValidationError("You can only delete Admin or Government Engineer accounts.")

        except Userstable.DoesNotExist:
            raise forms.ValidationError("User does not exist.")
        
        return username

class NormalUserCredentialUpdateForm(forms.ModelForm):
    new_username = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'New Username'})
    )
    new_password = forms.CharField(
        max_length=128,
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New Password'})
    )

    class Meta:
        model = Userstable
        fields = []  # No default fields from model

    def clean(self):
        cleaned_data = super().clean()
        new_username = cleaned_data.get('new_username')
        new_password = cleaned_data.get('new_password')

        if not new_username or not new_password:
            raise forms.ValidationError("Both username and password must be provided.")

        if Userstable.objects.filter(username=new_username).exists():
            self.add_error('new_username', "Username already exists. Please choose a different one.")

        return cleaned_data    
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


