from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name=_('utilisateur'))
    bio = models.TextField(_('biographie'), blank=True, max_length=500)
    avatar = models.ImageField(_('avatar'), upload_to='avatars/', blank=True, null=True)
    cover_photo = models.ImageField(_('photo de couverture'), upload_to='covers/', blank=True, null=True)
    website = models.URLField(_('site web'), blank=True)
    location = models.CharField(_('localisation'), max_length=100, blank=True)
    birth_date = models.DateField(_('date de naissance'), null=True, blank=True)
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('mis à jour le'), auto_now=True)

    class Meta:
        verbose_name = _('profil')
        verbose_name_plural = _('profils')

    def __str__(self):
        return f"Profil de {self.user.username}"

    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return '/static/images/default_avatar.svg'

    def get_cover_url(self):
        if self.cover_photo:
            return self.cover_photo.url
        return '/static/images/default_cover.jpg'

    def followers_count(self):
        return Follow.objects.filter(following=self.user).count()

    def following_count(self):
        return Follow.objects.filter(follower=self.user).count()

    def posts_count(self):
        return self.user.posts.count()


class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_set', verbose_name=_('abonné'))
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers_set', verbose_name=_('abonnement'))
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')
        verbose_name = _('abonnement')
        verbose_name_plural = _('abonnements')

    def __str__(self):
        return f"{self.follower.username} → {self.following.username}"
