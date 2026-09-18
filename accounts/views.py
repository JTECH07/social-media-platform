from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from django.db.models import Q
from .forms import RegisterForm, LoginForm, ProfileUpdateForm, UserUpdateForm
from .models import Profile, Follow
from posts.models import Post, Notification


def register_view(request):
    if request.user.is_authenticated:
        return redirect('core:feed')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, _('Bienvenue sur SocialNet ! 🎉'))
            return redirect('core:feed')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:feed')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, _(f'Bon retour, {user.first_name or user.username} !'))
            return redirect(request.GET.get('next', 'core:feed'))
        else:
            messages.error(request, _('Identifiants incorrects. Veuillez réessayer.'))
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, _('Vous avez été déconnecté.'))
    return redirect('accounts:login')


@login_required
def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=profile_user)
    posts = Post.objects.filter(author=profile_user).order_by('-created_at')
    is_following = False
    if request.user.is_authenticated and request.user != profile_user:
        is_following = Follow.objects.filter(follower=request.user, following=profile_user).exists()
    followers = Follow.objects.filter(following=profile_user).select_related('follower__profile')
    following = Follow.objects.filter(follower=profile_user).select_related('following__profile')
    context = {
        'profile_user': profile_user,
        'profile': profile,
        'posts': posts,
        'is_following': is_following,
        'followers': followers,
        'following': following,
        'followers_count': followers.count(),
        'following_count': following.count(),
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def edit_profile_view(request, username=None):
    profile = request.user.profile
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, _('Profil mis à jour avec succès !'))
            return redirect('accounts:profile', username=request.user.username)
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=profile)
    return render(request, 'accounts/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })


@login_required
def follow_toggle(request, username):
    target_user = get_object_or_404(User, username=username)
    if request.user == target_user:
        return JsonResponse({'error': 'Cannot follow yourself'}, status=400)

    follow_obj, created = Follow.objects.get_or_create(follower=request.user, following=target_user)
    if not created:
        follow_obj.delete()
        is_following = False
        # Remove notification
        Notification.objects.filter(
            recipient=target_user, sender=request.user, notification_type='follow'
        ).delete()
    else:
        is_following = True
        # Create notification
        Notification.objects.get_or_create(
            recipient=target_user, sender=request.user, notification_type='follow'
        )

    followers_count = Follow.objects.filter(following=target_user).count()
    return JsonResponse({'is_following': is_following, 'followers_count': followers_count})


@login_required
def search_users(request):
    query = request.GET.get('q', '')
    users = []
    if query:
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        ).exclude(id=request.user.id).select_related('profile')[:10]
    return render(request, 'accounts/search.html', {'users': users, 'query': query})


@login_required
def notifications_view(request):
    notifications = list(Notification.objects.filter(recipient=request.user).select_related('sender__profile', 'post')[:50])
    # Mark all as read
    if notifications:
        Notification.objects.filter(id__in=[n.id for n in notifications]).update(is_read=True)
    return render(request, 'accounts/notifications.html', {'notifications': notifications})


def followers_list(request, username):
    profile_user = get_object_or_404(User, username=username)
    followers = Follow.objects.filter(following=profile_user).select_related('follower__profile')
    return render(request, 'accounts/followers_list.html', {
        'profile_user': profile_user,
        'follows': followers,
        'list_type': 'followers'
    })


def following_list(request, username):
    profile_user = get_object_or_404(User, username=username)
    following = Follow.objects.filter(follower=profile_user).select_related('following__profile')
    return render(request, 'accounts/followers_list.html', {
        'profile_user': profile_user,
        'follows': following,
        'list_type': 'following'
    })
