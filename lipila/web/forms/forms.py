from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from django import forms
from api.models import LipilaDisbursement
from web.models import LipilaUser, Product


class DisburseForm(forms.ModelForm):
    class Meta:
        model = LipilaDisbursement
        fields = '__all__'


class LoginForm(forms.ModelForm):
    class Meta:
        model = LipilaUser
        fields = ('username', 'password')


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
            'bio',
            'city',
            'address',
            'company',
            'user_category',
            'facebook_url',
            'twitter_url',
            'instagram_url',
            'linkedin_url',
            ]
        widgets = {
            # Restrict file types
            'profile_image': forms.FileInput(attrs={'accept': 'image/*'}),
        }


class AddProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ('name', 'description', 'price', 'quantity',)