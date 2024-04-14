from django import forms
from LipilaInfo.models import Contact, LipilaUser
from django.contrib.auth.forms import UserChangeForm


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ('name', 'email', 'number', 'subject', 'message')
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Your name'}),
            'email': forms.TextInput(attrs={'placeholder': 'Your email'}),
            'number': forms.TextInput(attrs={'placeholder': 'Your WhatsApp number'}),
            'subject': forms.TextInput(attrs={'placeholder':'Subject'}),
            'message': forms.Textarea(attrs={'placeholder': 'Message'}),
        }


class SignupForm(forms.ModelForm):
    class Meta:
        model = LipilaUser
        fields = ('username', 'email', 'password')


class EditLipilaUserForm(UserChangeForm):
    class Meta:
        model = LipilaUser
        fields = [
            'profile_image',
            'first_name',
            'last_name',
            'phone_number',
            'city',
            'address',
            'company',
            ]
        widgets = {
            # Restrict file types
            'profile_image': forms.FileInput(attrs={'accept': 'image/*'}),
        }