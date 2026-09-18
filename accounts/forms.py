from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from .models import Profile


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label=_('Adresse email'), widget=forms.EmailInput(attrs={'placeholder': 'exemple@mail.com'}))
    first_name = forms.CharField(max_length=50, label=_('Prénom'), widget=forms.TextInput(attrs={'placeholder': _('Votre prénom')}))
    last_name = forms.CharField(max_length=50, label=_('Nom'), widget=forms.TextInput(attrs={'placeholder': _('Votre nom')}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        labels = {
            'username': _('Nom d\'utilisateur'),
        }
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': _('Choisissez un pseudo')}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('Cet email est déjà utilisé.'))
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(label=_('Nom d\'utilisateur'), widget=forms.TextInput(attrs={'placeholder': _('Votre pseudo')}))
    password = forms.CharField(label=_('Mot de passe'), widget=forms.PasswordInput(attrs={'placeholder': '••••••••'}))


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'avatar', 'cover_photo', 'website', 'location', 'birth_date']
        labels = {
            'bio': _('Biographie'),
            'avatar': _('Photo de profil'),
            'cover_photo': _('Photo de couverture'),
            'website': _('Site web'),
            'location': _('Localisation'),
            'birth_date': _('Date de naissance'),
        }
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3, 'placeholder': _('Parlez-nous de vous...')}),
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'website': forms.URLInput(attrs={'placeholder': 'https://...'}),
            'location': forms.TextInput(attrs={'placeholder': _('Ville, Pays')}),
        }


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': _('Prénom'),
            'last_name': _('Nom'),
            'email': _('Email'),
        }
