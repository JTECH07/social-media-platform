document.addEventListener('DOMContentLoaded', () => {
    // CSRF Token setup for AJAX
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');

    // Toasts auto-hide
    const toasts = document.querySelectorAll('.toast[data-autohide="true"]');
    toasts.forEach(toast => {
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, 5000);
    });

    // File Upload Preview
    const fileInput = document.querySelector('#id_image');
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            const previewContainer = document.getElementById('file-preview-container');
            if (!previewContainer) return;
            
            previewContainer.innerHTML = '';
            
            if (this.files && this.files[0]) {
                const file = this.files[0];
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    if (file.type.startsWith('image/')) {
                        const img = document.createElement('img');
                        img.src = e.target.result;
                        img.style.maxHeight = '200px';
                        img.style.borderRadius = '12px';
                        img.style.marginTop = '1rem';
                        img.style.objectFit = 'cover';
                        img.style.width = '100%';
                        previewContainer.appendChild(img);
                    } else if (file.type.startsWith('video/')) {
                        const vid = document.createElement('video');
                        vid.src = e.target.result;
                        vid.controls = true;
                        vid.style.maxHeight = '300px';
                        vid.style.borderRadius = '12px';
                        vid.style.marginTop = '1rem';
                        vid.style.width = '100%';
                        previewContainer.appendChild(vid);
                    } else {
                        const div = document.createElement('div');
                        div.className = 'p-3 rounded mt-3';
                        div.style.backgroundColor = 'var(--primary-light)';
                        div.style.color = 'var(--primary)';
                        div.innerHTML = `<i class="fas fa-file"></i> ${file.name}`;
                        previewContainer.appendChild(div);
                    }
                }
                reader.readAsDataURL(file);
            }
        });
    }

    // User Dropdown
    const userMenuToggle = document.getElementById('user-menu-toggle');
    const userDropdown = document.getElementById('user-dropdown');
    
    if (userMenuToggle && userDropdown) {
        userMenuToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            userDropdown.classList.toggle('show');
        });

        document.addEventListener('click', (e) => {
            if (!userDropdown.contains(e.target) && !userMenuToggle.contains(e.target)) {
                userDropdown.classList.remove('show');
            }
        });
    }

    // Like functionality
    const likeBtns = document.querySelectorAll('.like-btn');
    likeBtns.forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            if (!document.body.contains(userMenuToggle)) {
                window.location.href = '/accounts/login/';
                return;
            }

            const postId = btn.dataset.post;
            try {
                const response = await fetch(`/posts/${postId}/like/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrftoken,
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });
                
                if (response.ok) {
                    const data = await response.json();
                    const icon = btn.querySelector('i');
                    const countSpan = btn.querySelector('.like-count');
                    
                    if (data.liked) {
                        btn.classList.add('liked');
                        icon.classList.remove('far');
                        icon.classList.add('fas');
                    } else {
                        btn.classList.remove('liked');
                        icon.classList.remove('fas');
                        icon.classList.add('far');
                    }
                    
                    if (countSpan) countSpan.textContent = data.likes_count;
                }
            } catch (error) {
                console.error('Error liking post:', error);
            }
        });
    });

    // Follow functionality
    const followBtns = document.querySelectorAll('.follow-btn');
    followBtns.forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            const username = btn.dataset.user;
            try {
                const response = await fetch(`/accounts/profile/${username}/follow/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrftoken,
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });
                
                if (response.ok) {
                    const data = await response.json();
                    
                    if (data.is_following) {
                        btn.classList.remove('btn-primary');
                        btn.classList.add('btn-outline');
                        btn.innerHTML = '<i class="fas fa-check"></i> Abonné';
                    } else {
                        btn.classList.remove('btn-outline');
                        btn.classList.add('btn-primary');
                        btn.innerHTML = '<i class="fas fa-user-plus"></i> Suivre';
                    }
                    
                    // Update count if on profile page
                    const followersCountEl = document.getElementById('followers-count');
                    if (followersCountEl) {
                        followersCountEl.textContent = data.followers_count;
                    }
                }
            } catch (error) {
                console.error('Error following user:', error);
            }
        });
    });

    // Delete comment functionality
    const deleteCommentBtns = document.querySelectorAll('.delete-comment-btn');
    deleteCommentBtns.forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            if(!confirm("Supprimer ce commentaire ?")) return;

            const commentId = btn.dataset.comment;
            try {
                const response = await fetch(`/posts/comment/${commentId}/delete/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrftoken,
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });
                if(response.ok) {
                    document.getElementById(`comment-${commentId}`).remove();
                }
            } catch(e) {
                console.error(e);
            }
        });
    });
});
