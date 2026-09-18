from posts.models import Notification


def global_context(request):
    context = {}
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(
            recipient=request.user, is_read=False
        ).count()
        context['unread_notif_count'] = unread_count
    return context
