from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from posts.models import Post, Notification
from posts.forms import PostForm
from accounts.models import Follow


@login_required
def feed_view(request):
    # Get posts from followed users + own posts
    following_users = Follow.objects.filter(follower=request.user).values_list('following', flat=True)
    posts = Post.objects.filter(
        author__in=list(following_users) + [request.user.id]
    ).select_related('author__profile').prefetch_related('likes', 'comments').order_by('-created_at')

    # Suggested users to follow
    already_following = list(following_users)
    suggested = User.objects.exclude(
        id__in=already_following + [request.user.id]
    ).select_related('profile').order_by('?')[:5]

    post_form = PostForm()
    unread_notif_count = Notification.objects.filter(recipient=request.user, is_read=False).count()

    context = {
        'posts': posts,
        'post_form': post_form,
        'suggested_users': suggested,
        'unread_notif_count': unread_notif_count,
    }
    return render(request, 'core/feed.html', context)


def landing_view(request):
    if request.user.is_authenticated:
        return redirect('core:feed')
    return render(request, 'core/landing.html')
