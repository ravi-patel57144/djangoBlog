from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.core.paginator import Paginator
from .models import Post, Author, Comment
from .forms import PostForm, CommentForm, AuthorForm

# Create your views here.

def get_or_create_author(user):
    """Helper function to get or create an author for a user"""
    author, created = Author.objects.get_or_create(user=user)
    return author

def post_list(request):
    """Display a list of all published posts"""
    posts = Post.objects.filter(published=True)
    paginator = Paginator(posts, 5)  # Show 5 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'posts': page_obj,
    }
    return render(request, 'blog/post_list.html', context)

def post_detail(request, pk):
    """Display a single post with its comments"""
    post = get_object_or_404(Post, pk=pk, published=True)
    comments = post.comments.filter(approved=True)
    
    if request.method == 'POST':
        if request.user.is_authenticated:
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.post = post
                comment.author = get_or_create_author(request.user)
                comment.save()
                messages.success(request, 'Your comment has been added!')
                return redirect('post_detail', pk=post.pk)
        else:
            messages.error(request, 'You need to be logged in to comment.')
    else:
        form = CommentForm()
    
    context = {
        'post': post,
        'comments': comments,
        'form': form,
    }
    return render(request, 'blog/post_detail.html', context)

@login_required
def post_create(request):
    """Create a new post"""
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = get_or_create_author(request.user)
            post.save()
            messages.success(request, 'Post created successfully!')
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    
    context = {
        'form': form,
        'title': 'Create New Post'
    }
    return render(request, 'blog/post_form.html', context)

@login_required
def post_edit(request, pk):
    """Edit an existing post"""
    post = get_object_or_404(Post, pk=pk)
    
    # Check if the user is the author of the post
    if post.author.user != request.user:
        return HttpResponseForbidden("You don't have permission to edit this post.")
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post updated successfully!')
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    
    context = {
        'form': form,
        'post': post,
        'title': 'Edit Post'
    }
    return render(request, 'blog/post_form.html', context)

@login_required
def post_delete(request, pk):
    """Delete a post"""
    post = get_object_or_404(Post, pk=pk)
    
    # Check if the user is the author of the post
    if post.author.user != request.user:
        return HttpResponseForbidden("You don't have permission to delete this post.")
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted successfully!')
        return redirect('post_list')
    
    context = {
        'post': post,
    }
    return render(request, 'blog/post_confirm_delete.html', context)

@login_required
def my_posts(request):
    """Display posts created by the current user"""
    author = get_or_create_author(request.user)
    posts = author.posts.all()
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'posts': page_obj,
    }
    return render(request, 'blog/my_posts.html', context)

@login_required
def profile(request):
    """Display and edit user profile"""
    author = get_or_create_author(request.user)
    
    if request.method == 'POST':
        form = AuthorForm(request.POST, request.FILES, instance=author)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = AuthorForm(instance=author)
    
    context = {
        'author': author,
        'form': form,
    }
    return render(request, 'blog/profile.html', context)
