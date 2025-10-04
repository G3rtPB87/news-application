from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction

from .forms import CustomUserCreationForm, ArticleForm, NewsletterForm
from .models import Article, CustomUser, Publisher, Newsletter
from .serializers import ArticleSerializer, NewsletterSerializer


def home(request):
    """Renders the home page with a list of approved articles and newsletters.
    
    Displays publicly available content to all users including approved articles,
    newsletters, publishers, and journalists.
    
    :param request: HTTP request object
    :returns: Rendered home page with content context
    :rtype: HttpResponse
    """
    approved_articles = (
        Article.objects.filter(approved=True)
        .order_by('-created_at')
    )
    approved_newsletters = (
        Newsletter.objects.filter(approved=True)
        .order_by('-created_at')
    )
    publishers = Publisher.objects.all()
    journalists = CustomUser.objects.filter(role='journalist')
    context = {
        'articles': approved_articles,
        'newsletters': approved_newsletters,
        'publishers': publishers,
        'journalists': journalists,
    }
    return render(request, 'news/home.html', context)


def register(request):
    """Handles user registration and assigns roles and permissions.
    
    Processes user registration form, saves the user, assigns them to publishers
    based on their role, and logs them in upon successful registration.
    
    :param request: HTTP request object
    :returns: Registration form or redirect to dashboard
    :rtype: HttpResponse
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            publishers = form.cleaned_data.get('publishers')
            if user.role == 'editor':
                user.publishers_editor.set(publishers)
            elif user.role == 'journalist':
                user.publishers_journalist.set(publishers)

            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'news/register.html', {'form': form})


def login_view(request):
    """Handles user login and redirects to the appropriate dashboard.
    
    Authenticates user credentials and redirects to role-specific dashboard
    upon successful login.
    
    :param request: HTTP request object
    :returns: Login form or redirect to appropriate dashboard
    :rtype: HttpResponse
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if user.role.lower() == 'editor':
                    return redirect('editor_dashboard')
                elif user.role.lower() == 'journalist':
                    return redirect('journalist_dashboard')
                else:
                    return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'news/login.html', {'form': form})


def logout_view(request):
    """Logs the user out and redirects to the home page.
    
    :param request: HTTP request object
    :returns: Redirect to home page
    :rtype: HttpResponse
    """
    logout(request)
    return redirect('home')


@login_required
def dashboard(request):
    """Renders the personalized dashboard for a logged-in reader.
    
    Shows subscribed content from publishers and journalists that the reader follows.
    Redirects editors and journalists to their respective dashboards.
    
    :param request: HTTP request object
    :returns: Reader dashboard or redirect to role-specific dashboard
    :rtype: HttpResponse
    """
    user = request.user
    if user.role.lower() == 'reader':
        subscribed_publishers = user.subscriptions_publishers.all()
        subscribed_journalists = user.subscriptions_journalists.all()

        publisher_articles = Article.objects.filter(
            approved=True,
            publisher__in=subscribed_publishers
        ).order_by('-created_at')

        journalist_articles = Article.objects.filter(
            approved=True,
            author__in=subscribed_journalists
        ).order_by('-created_at')

        subscribed_articles = (
            publisher_articles | journalist_articles
        ).distinct()

        publisher_newsletters = Newsletter.objects.filter(
            approved=True,
            publisher__in=subscribed_publishers
        ).order_by('-created_at')

        journalist_newsletters = Newsletter.objects.filter(
            approved=True,
            author__in=subscribed_journalists
        ).order_by('-created_at')

        subscribed_newsletters = (
            publisher_newsletters | journalist_newsletters
        ).distinct()

        context = {
            'articles': subscribed_articles,
            'newsletters': subscribed_newsletters,
        }
        return render(request, 'news/dashboard.html', context)
    else:
        if user.role.lower() == 'editor':
            return redirect('editor_dashboard')
        elif user.role.lower() == 'journalist':
            return redirect('journalist_dashboard')
        else:
            return redirect('home')


def article_detail(request, article_id):
    """Renders the detail page for a single article.
    
    :param request: HTTP request object
    :param article_id: ID of the article to display
    :returns: Article detail page
    :rtype: HttpResponse
    """
    article = get_object_or_404(Article, pk=article_id)
    return render(request, 'news/article_detail.html', {'article': article})


@login_required
def subscribe(request, subscription_type, pk):
    """Handles the subscription/unsubscription logic for readers.
    
    Toggles subscription status for publishers or journalists.
    
    :param request: HTTP request object
    :param subscription_type: Type of subscription ('publisher' or 'journalist')
    :param pk: Primary key of the publisher or journalist
    :returns: Redirect to home page
    :rtype: HttpResponse
    """
    if request.method == 'POST':
        if request.user.role.lower() == 'reader':
            if subscription_type == 'publisher':
                publisher = get_object_or_404(Publisher, pk=pk)
                if (
                    request.user.subscriptions_publishers.filter(pk=pk).exists()
                ):
                    request.user.subscriptions_publishers.remove(publisher)
                else:
                    request.user.subscriptions_publishers.add(publisher)
            elif subscription_type == 'journalist':
                journalist = get_object_or_404(CustomUser, pk=pk)
                if (
                    request.user.subscriptions_journalists
                    .filter(pk=pk)
                    .exists()
                ):
                    request.user.subscriptions_journalists.remove(journalist)
                else:
                    request.user.subscriptions_journalists.add(journalist)
    return redirect('home')


@login_required
@user_passes_test(lambda u: u.role == 'journalist')
def create_article(request):
    """Allows journalists to create and submit new articles.
    
    :param request: HTTP request object
    :returns: Article creation form or redirect to journalist dashboard
    :rtype: HttpResponse
    """
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.approved = False
            article.save()
            return redirect('journalist_dashboard')
    else:
        form = ArticleForm()
    return render(request, 'news/create_article.html', {'form': form})


@login_required
@user_passes_test(lambda u: u.role.lower() == 'journalist')
def journalist_dashboard(request):
    """Renders the dashboard for journalists, showing their submitted content.
    
    :param request: HTTP request object
    :returns: Journalist dashboard with articles and newsletters
    :rtype: HttpResponse
    """
    articles = (
        Article.objects.filter(author=request.user)
        .order_by('-created_at')
    )
    newsletters = (
        Newsletter.objects.filter(author=request.user)
        .order_by('-created_at')
    )
    context = {
        'articles': articles,
        'newsletters': newsletters,
    }
    return render(request, 'news/journalist_dashboard.html', context)


@login_required
def edit_article(request, pk):
    """Allows authors and editors to edit existing articles.
    
    :param request: HTTP request object
    :param pk: Primary key of the article to edit
    :returns: Article edit form or redirect to appropriate dashboard
    :rtype: HttpResponse
    """
    article = get_object_or_404(Article, pk=pk)
    # Check if the user is the author or an editor
    is_author = request.user == article.author
    is_editor = request.user.role.lower() == 'editor'
    if not (is_author or is_editor):
        return redirect('home')

    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            form.save()
            # Redirect to the appropriate dashboard based on the user's role
            if request.user.role.lower() == 'editor':
                return redirect('editor_content_management')
            else:
                return redirect('journalist_dashboard')
    else:
        form = ArticleForm(instance=article)

    return render(
        request,
        'news/edit_article.html',
        {
            'form': form,
            'article': article
        }
    )


@login_required
def delete_article(request, pk):
    """Allows authors and editors to delete articles.
    
    :param request: HTTP request object
    :param pk: Primary key of the article to delete
    :returns: Delete confirmation page or redirect to appropriate dashboard
    :rtype: HttpResponse
    """
    article = get_object_or_404(Article, pk=pk)
    # Check if the user is the author or an editor
    is_author = request.user == article.author
    is_editor = request.user.role.lower() == 'editor'
    if not (is_author or is_editor):
        return redirect('home')

    if request.method == 'POST':
        article.delete()
        # Redirect to the appropriate dashboard based on the user's role
        if request.user.role.lower() == 'editor':
            return redirect('editor_content_management')
        else:
            return redirect('journalist_dashboard')

    return render(
        request,
        'news/delete_confirm.html',
        {
            'item': article,
            'type': 'article'
        }
    )


@login_required
def edit_newsletter(request, pk):
    """Allows authors and editors to edit existing newsletters.
    
    :param request: HTTP request object
    :param pk: Primary key of the newsletter to edit
    :returns: Newsletter edit form or redirect to appropriate dashboard
    :rtype: HttpResponse
    """
    newsletter = get_object_or_404(Newsletter, pk=pk)
    # Check if the user is the author or an editor
    is_author = request.user == newsletter.author
    is_editor = request.user.role.lower() == 'editor'
    if not (is_author or is_editor):
        return redirect('home')

    if request.method == 'POST':
        form = NewsletterForm(request.POST, instance=newsletter)
        if form.is_valid():
            form.save()
            # Redirect to the appropriate dashboard based on the user's role
            if request.user.role.lower() == 'editor':
                return redirect('editor_content_management')
            else:
                return redirect('journalist_dashboard')
    else:
        form = NewsletterForm(instance=newsletter)

    return render(
        request,
        'news/edit_newsletter.html',
        {
            'form': form,
            'newsletter': newsletter
        }
    )


@login_required
def delete_newsletter(request, pk):
    """Allows authors and editors to delete newsletters.
    
    :param request: HTTP request object
    :param pk: Primary key of the newsletter to delete
    :returns: Delete confirmation page or redirect to appropriate dashboard
    :rtype: HttpResponse
    """
    newsletter = get_object_or_404(Newsletter, pk=pk)
    # Check if the user is the author or an editor
    is_author = request.user == newsletter.author
    is_editor = request.user.role.lower() == 'editor'
    if not (is_author or is_editor):
        return redirect('home')

    if request.method == 'POST':
        newsletter.delete()
        # Redirect to the appropriate dashboard based on the user's role
        if request.user.role.lower() == 'editor':
            return redirect('editor_content_management')
        else:
            return redirect('journalist_dashboard')

    return render(
        request,
        'news/delete_confirm.html',
        {
            'item': newsletter,
            'type': 'newsletter'
        }
    )


@login_required
@user_passes_test(lambda u: u.role.lower() == 'editor')
def editor_dashboard(request):
    """Renders the editor's dashboard with unapproved articles and newsletters.
    
    :param request: HTTP request object
    :returns: Editor dashboard with pending content for approval
    :rtype: HttpResponse
    """
    unapproved_articles = (
        Article.objects.filter(approved=False)
        .order_by('-created_at')
    )
    unapproved_newsletters = (
        Newsletter.objects.filter(approved=False)
        .order_by('-created_at')
    )
    context = {
        'articles': unapproved_articles,
        'newsletters': unapproved_newsletters,
    }
    return render(request, 'news/editor_dashboard.html', context)


@login_required
@user_passes_test(lambda u: u.role.lower() == 'editor')
def editor_content_management(request):
    """Renders the content management page for editors, showing approved content.
    
    :param request: HTTP request object
    :returns: Editor content management page with approved content
    :rtype: HttpResponse
    """
    articles = Article.objects.filter(approved=True).order_by('-created_at')
    newsletters = (
        Newsletter.objects.filter(approved=True)
        .order_by('-created_at')
    )
    context = {
        'articles': articles,
        'newsletters': newsletters,
    }
    return render(request, 'news/editor_content_management.html', context)


@login_required
@user_passes_test(lambda u: u.role.lower() == 'journalist')
def create_newsletter(request):
    """Allows journalists to create and submit new newsletters.
    
    :param request: HTTP request object
    :returns: Newsletter creation form or redirect to journalist dashboard
    :rtype: HttpResponse
    """
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            newsletter = form.save(commit=False)
            newsletter.author = request.user
            newsletter.save()
            return redirect('journalist_dashboard')
    else:
        form = NewsletterForm()
    return render(request, 'news/create_newsletter.html', {'form': form})


class SubscribedArticlesView(APIView):
    """API view to get a list of articles based on a reader's subscriptions.
    
    Returns articles from publishers and journalists that the reader follows.
    """
    def get(self, request, *args, **kwargs):
        """Handle GET requests for subscribed articles.
        
        :param request: HTTP request object
        :returns: JSON response with subscribed articles or error
        :rtype: Response
        """
        if (
            not request.user.is_authenticated or
            request.user.role.lower() != 'reader'
        ):
            return Response(
                {"error": "Authentication required or user is not a reader."},
                status=status.HTTP_403_FORBIDDEN
            )

        user = request.user
        subscribed_publishers = user.subscriptions_publishers.all()
        subscribed_journalists = user.subscriptions_journalists.all()

        publisher_articles = Article.objects.filter(
            approved=True,
            publisher__in=subscribed_publishers
        )

        journalist_articles = Article.objects.filter(
            approved=True,
            author__in=subscribed_journalists
        )

        subscribed_articles = (
            publisher_articles | journalist_articles
        ).distinct()

        serializer = ArticleSerializer(subscribed_articles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SubscribedNewslettersView(APIView):
    """API view to get a list of newsletters based on a reader's subscriptions.
    
    Returns newsletters from publishers and journalists that the reader follows.
    """
    def get(self, request, *args, **kwargs):
        """Handle GET requests for subscribed newsletters.
        
        :param request: HTTP request object
        :returns: JSON response with subscribed newsletters or error
        :rtype: Response
        """
        if (
            not request.user.is_authenticated or
            request.user.role.lower() != 'reader'
        ):
            return Response(
                {"error": "Authentication required or user is not a reader."},
                status=status.HTTP_403_FORBIDDEN
            )

        user = request.user
        subscribed_publishers = user.subscriptions_publishers.all()
        subscribed_journalists = user.subscriptions_journalists.all()

        publisher_newsletters = Newsletter.objects.filter(
            approved=True,
            publisher__in=subscribed_publishers
        )

        journalist_newsletters = Newsletter.objects.filter(
            approved=True,
            author__in=subscribed_journalists
        )

        subscribed_newsletters = (
            publisher_newsletters | journalist_newsletters
        ).distinct()

        serializer = NewsletterSerializer(subscribed_newsletters, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ArticleApprovalView(APIView):
    """API view for editors to approve articles."""
    def post(self, request, article_id, *args, **kwargs):
        """Handle POST requests to approve articles.
        
        :param request: HTTP request object
        :param article_id: ID of the article to approve
        :returns: JSON response with success or error message
        :rtype: Response
        """
        if request.user.role.lower() != 'editor':
            return Response(
                {"error": "You do not have permission to approve articles."},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            with transaction.atomic():
                article = get_object_or_404(Article, pk=article_id)
                if not article.approved:
                    article.approved = True
                    article.save()

            return Response(
                {"success": f"Article '{article.title}' has been approved."},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class NewsletterApprovalView(APIView):
    """API view for editors to approve newsletters."""
    def post(self, request, newsletter_id, *args, **kwargs):
        """Handle POST requests to approve newsletters.
        
        :param request: HTTP request object
        :param newsletter_id: ID of the newsletter to approve
        :returns: JSON response with success or error message
        :rtype: Response
        """
        if request.user.role.lower() != 'editor':
            return Response(
                {"error": "You don't have permission to approve newsletters."},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            with transaction.atomic():
                newsletter = get_object_or_404(Newsletter, pk=newsletter_id)
                if not newsletter.approved:
                    newsletter.approved = True
                    newsletter.save()

            return Response(
                {
                    "success": (
                        f"Newsletter '{newsletter.title}' has been "
                        "approved."
                    )
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )