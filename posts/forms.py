from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'image']
        labels = {
            'content': '',
            'image': _('Ajouter un fichier (image/vidéo)'),
        }
        widgets = {
            'content': forms.Textarea(attrs={
                'placeholder': _('Quoi de neuf ? Partagez quelque chose...'),
                'rows': 3,
                'class': 'post-textarea',
                'id': 'post-content',
            }),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        labels = {'content': ''}
        widgets = {
            'content': forms.TextInput(attrs={
                'placeholder': _('Écrire un commentaire...'),
                'class': 'comment-input',
            }),
        }
