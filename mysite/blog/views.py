from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail
from django.db.models import Count
from django.views.decorators.http import require_POST
from django.contrib.postgres.search import TrigramSimilarity
from taggit.models import Tag
from .models import Post, Recipe
from .forms import CommentForm, EmailPostForm, SearchForm, RatingForm

# Blog Post Views

# List all published blog posts
def post_list(request, tag_slug=None):
    post_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])

    paginator = Paginator(post_list, 3)  # 3 posts per page
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request, 'blog/post/list.html', {'posts': posts, 'tag': tag})


# Blog post tag filtering
def post_list_by_tag(request, tag_slug=None):
    tag = get_object_or_404(Tag, slug=tag_slug)
    post_list = Post.published.filter(tags__in=[tag])

    paginator = Paginator(post_list, 3)  # Paginate with 3 posts per page
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request, 'blog/post/list.html', {'posts': posts, 'tag': tag})


# Blog post detail view
def post_detail(request, year, month, day, post):
    post = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,
        slug=post,
        publish__year=year,
        publish__month=month,
        publish__day=day,
    )
    comments = post.comments.filter(active=True)
    form = CommentForm()

    # Find similar posts based on tags
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]

    return render(
        request,
        'blog/post/detail.html',
        {
            'post': post,
            'comments': comments,
            'form': form,
            'similar_posts': similar_posts,
        }
    )


# Share blog post via email
def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent = False

    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} ({cd['email']}) recommends you read {post.title}"
            message = f"Read {post.title} at {post_url}\n\n{cd['name']}'s comments: {cd['comments']}"
            send_mail(subject, message, from_email=None, recipient_list=[cd['to']])
            sent = True
    else:
        form = EmailPostForm()

    return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})


# Handle blog post comments
@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None
    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
    return render(request, 'blog/post/comment.html', {'post': post, 'form': form, 'comment': comment})


# Blog post search using Trigram similarity
def post_search(request):
    form = SearchForm()
    query = None
    results = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = (
                Post.published.annotate(
                    similarity=TrigramSimilarity('title', query),
                )
                .filter(similarity__gt=0.1)
                .order_by('-similarity')
            )

    return render(request, 'blog/post/search.html', {'form': form, 'query': query, 'results': results})


# Recipe Views

# List all published recipes with debug statements
def recipe_list(request, tag_slug=None):
    recipe_list = Recipe.published.all()  # Use the custom manager to retrieve published recipes
    print(f"Retrieved recipes: {recipe_list}")  # Debug statement to print the retrieved recipes

    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        recipe_list = recipe_list.filter(tags__in=[tag])
        print(f"Recipes after tag filtering: {recipe_list}")  # Debug statement for tag filtering

    paginator = Paginator(recipe_list, 3)  # 3 recipes per page
    page_number = request.GET.get('page', 1)
    
    try:
        recipes = paginator.page(page_number)
    except PageNotAnInteger:
        recipes = paginator.page(1)
    except EmptyPage:
        recipes = paginator.page(paginator.num_pages)

    print(f"Recipes on page {page_number}: {recipes}")  # Debug statement for paginated results

    return render(request, 'blog/recipe/list.html', {'recipes': recipes, 'tag': tag})


# Recipe tag filtering
def recipe_list_by_tag(request, tag_slug=None):
    tag = get_object_or_404(Tag, slug=tag_slug)
    recipe_list = Recipe.published.filter(tags__in=[tag])

    paginator = Paginator(recipe_list, 3)  # 3 recipes per page
    page_number = request.GET.get('page', 1)
    try:
        recipes = paginator.page(page_number)
    except PageNotAnInteger:
        recipes = paginator.page(1)
    except EmptyPage:
        recipes = paginator.page(paginator.num_pages)

    return render(request, 'blog/recipe/list.html', {'recipes': recipes, 'tag': tag})


# Recipe detail view
def recipe_detail(request, slug):
    recipe = get_object_or_404(Recipe, slug=slug, status=Recipe.Status.PUBLISHED)

    if request.method == 'POST':
        rating_form = RatingForm(request.POST, instance=recipe)
        if rating_form.is_valid():
            rating_form.save()
    else:
        rating_form = RatingForm(instance=recipe)

    # Find similar recipes based on tags
    recipe_tags_ids = recipe.tags.values_list('id', flat=True)
    similar_recipes = Recipe.published.filter(tags__in=recipe_tags_ids).exclude(id=recipe.id)
    similar_recipes = similar_recipes.annotate(same_tags=Count('tags')).order_by('-same_tags', '-created')[:4]

    return render(request, 'blog/recipe/detail.html', {'recipe': recipe, 'rating_form': rating_form, 'similar_recipes': similar_recipes})


# Share a recipe via email
def recipe_share(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id, status=Recipe.Status.PUBLISHED)
    sent = False

    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            recipe_url = request.build_absolute_uri(recipe.get_absolute_url())
            subject = f"{cd['name']} ({cd['email']}) recommends you try {recipe.title}"
            message = f"Check out the recipe {recipe.title} at {recipe_url}\n\n{cd['name']}'s comments: {cd['comments']}"
            send_mail(subject, message, from_email=None, recipient_list=[cd['to']])
            sent = True
    else:
        form = EmailPostForm()

    return render(request, 'blog/recipe/share.html', {'recipe': recipe, 'form': form, 'sent': sent})


# Recipe cuisine filtering
def recipe_list_by_cuisine(request, tag_slug=None):
    tag = get_object_or_404(Tag, slug=tag_slug)
    recipe_list = Recipe.published.filter(tags__in=[tag])  # Customize if necessary
    return render(request, 'blog/recipe/list.html', {'recipes': recipe_list, 'tag': tag})


# Recipe search using Trigram similarity
def recipe_search(request):
    form = SearchForm()
    query = None
    results = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = (
                Recipe.published.annotate(
                    similarity=TrigramSimilarity('title', query),
                )
                .filter(similarity__gt=0.1)
                .order_by('-similarity')
            )

    return render(request, 'blog/recipe/search.html', {'form': form, 'query': query, 'results': results})