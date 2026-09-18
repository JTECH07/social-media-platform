from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Post, Comment, Like, Notification
from .forms import PostForm, CommentForm


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'redirect': '/'})
            messages.success(request, _('Publication créée avec succès !'))
            return redirect('core:feed')
        else:
            messages.error(request, _("Erreur lors de la création de la publication."))
            return redirect('core:feed')
    return redirect('core:feed')


@login_required
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.filter(parent=None).select_related('author__profile').prefetch_related('replies__author__profile')
    comment_form = CommentForm()
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.author = request.user
            parent_id = request.POST.get('parent_id')
            if parent_id:
                comment.parent = get_object_or_404(Comment, pk=parent_id)
            comment.save()
            # Notification
            if post.author != request.user:
                Notification.objects.create(
                    recipient=post.author,
                    sender=request.user,
                    notification_type='comment',
                    post=post,
                    comment=comment
                )
            messages.success(request, _('Commentaire ajouté !'))
            return redirect('posts:detail', pk=pk)
    return render(request, 'posts/post_detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
    })


@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    if request.method == 'POST':
        post.delete()
        messages.success(request, _('Publication supprimée.'))
        return redirect('core:feed')
    return render(request, 'posts/post_confirm_delete.html', {'post': post})


@login_required
@require_POST
def like_toggle(request, pk):
    post = get_object_or_404(Post, pk=pk)
    like_obj, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like_obj.delete()
        liked = False
        Notification.objects.filter(recipient=post.author, sender=request.user, notification_type='like', post=post).delete()
    else:
        liked = True
        if post.author != request.user:
            Notification.objects.get_or_create(
                recipient=post.author,
                sender=request.user,
                notification_type='like',
                post=post
            )
    likes_count = post.likes.count()
    return JsonResponse({'liked': liked, 'likes_count': likes_count})


@login_required
@require_POST
def comment_delete(request, pk):
    comment = get_object_or_404(Comment, pk=pk, author=request.user)
    post_pk = comment.post.pk
    comment.delete()
    return JsonResponse({'success': True})


@login_required
def explore_view(request):
    posts = Post.objects.all().order_by('-created_at').select_related('author__profile')[:50]
    return render(request, 'posts/explore.html', {'posts': posts})
