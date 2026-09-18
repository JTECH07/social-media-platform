from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts', verbose_name=_('auteur'))
    content = models.TextField(_('contenu'), max_length=2000)
    image = models.FileField(_('fichier'), upload_to='posts/', blank=True, null=True)
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('mis à jour le'), auto_now=True)

    class Meta:
        verbose_name = _('publication')
        verbose_name_plural = _('publications')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.author.username}: {self.content[:50]}"

    def likes_count(self):
        return self.likes.count()

    def comments_count(self):
        return self.comments.filter(parent=None).count()

    def is_liked_by(self, user):
        if user.is_authenticated:
            return self.likes.filter(user=user).exists()
        return False


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name=_('publication'))
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', verbose_name=_('auteur'))
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='replies', null=True, blank=True, verbose_name=_('commentaire parent'))
    content = models.TextField(_('contenu'), max_length=500)
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('mis à jour le'), auto_now=True)

    class Meta:
        verbose_name = _('commentaire')
        verbose_name_plural = _('commentaires')
        ordering = ['created_at']

    def __str__(self):
        return f"{self.author.username} → Post #{self.post.id}"


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes', verbose_name=_('utilisateur'))
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes', verbose_name=_('publication'))
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')
        verbose_name = _('j\'aime')
        verbose_name_plural = _('j\'aime')

    def __str__(self):
        return f"{self.user.username} ♥ Post #{self.post.id}"


class Notification(models.Model):
    TYPE_CHOICES = [
        ('like', _('J\'aime')),
        ('comment', _('Commentaire')),
        ('follow', _('Abonnement')),
        ('reply', _('Réponse')),
    ]
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name=_('destinataire'))
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications', verbose_name=_('expéditeur'))
    notification_type = models.CharField(_('type'), max_length=20, choices=TYPE_CHOICES)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_('publication'))
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_('commentaire'))
    is_read = models.BooleanField(_('lu'), default=False)
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)

    class Meta:
        verbose_name = _('notification')
        verbose_name_plural = _('notifications')
        ordering = ['-created_at']

    def __str__(self):
        return f"Notif {self.notification_type} → {self.recipient.username}"
