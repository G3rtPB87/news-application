from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver


# Create your models here.


class CustomUser(AbstractUser):
    """A custom user model extending Django's AbstractUser for role-based access control.
    
    This model provides extended user functionality including roles, subscriptions,
    and content management capabilities for a news application.
    
    :param AbstractUser: Django's built-in AbstractUser model
    :field role: User's role in the system (reader, editor, or journalist)
    :field subscriptions_publishers: Publishers the user subscribes to
    :field subscriptions_journalists: Journalists the user follows
    :field articles: Articles authored by the user (journalists only)
    :field newsletters: Newsletters authored by the user (journalists only)
    """
    # A custom user model to allow for future expansion.
    # We will use this to assign roles and manage subscriptions.

    # User roles
    ROLE_CHOICES = (
        ('reader', 'Reader'),
        ('editor', 'Editor'),
        ('journalist', 'Journalist'),
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='reader'
    )

    # Subscriptions for readers
    subscriptions_publishers = models.ManyToManyField(
        'Publisher',
        related_name='subscribers_to_publisher',
        blank=True
    )
    subscriptions_journalists = models.ManyToManyField(
        'self',
        related_name='followers',
        symmetrical=False,
        blank=True
    )

    # Articles and newsletters for journalists
    articles = models.ManyToManyField(
        'Article',
        related_name='author_articles',
        blank=True
    )
    newsletters = models.ManyToManyField(
        'Newsletter',
        related_name='author_newsletters',
        blank=True
    )

    def __str__(self):
        return self.username

    class Meta:
        # A simple Meta class to add a more descriptive
        # name in the admin panel.
        verbose_name_plural = "Custom Users"


class Publisher(models.Model):
    """Represents a publishing entity in the news application.
    
    Publishers can have editors and journalists associated with them,
    and they publish articles and newsletters.
    
    :field name: The name of the publisher
    :field editors: Editors associated with this publisher
    :field journalists: Journalists associated with this publisher
    :field description: Optional description of the publisher
    """
    name = models.CharField(max_length=100)
    editors = models.ManyToManyField(
        CustomUser,
        related_name='publishers_editor',
        blank=True
    )
    journalists = models.ManyToManyField(
        CustomUser,
        related_name='publishers_journalist',
        blank=True
    )
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Article(models.Model):
    """Represents a news article in the system.
    
    Articles are created by journalists and can be approved by editors
    for publication.
    
    :field title: The title of the article
    :field content: The main content of the article
    :field author: The journalist who wrote the article
    :field publisher: The publisher associated with the article
    :field approved: Whether the article has been approved for publication
    :field created_at: Timestamp of when the article was created
    """
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='articles_written'
    )
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.CASCADE,
        related_name='articles_published',
        null=True,
        blank=True
    )
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    # This is a flag to check the previous value of the 'approved' field
    _original_approved = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.pk is not None:
            self._original_approved = self.approved
        else:
            self._original_approved = None


class Newsletter(models.Model):
    """Represents a newsletter in the system.
    
    Newsletters are periodic publications sent to subscribers
    containing multiple articles or updates.
    
    :field title: The title of the newsletter
    :field content: The main content of the newsletter
    :field author: The journalist who created the newsletter
    :field publisher: The publisher associated with the newsletter
    :field approved: Whether the newsletter has been approved for sending
    :field created_at: Timestamp of when the newsletter was created
    """
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='newsletters_written'
    )
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.CASCADE,
        related_name='newsletters_published',
        null=True,
        blank=True
    )
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    # This is a flag to check the previous value of the 'approved' field
    _original_approved = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.pk is not None:
            self._original_approved = self.approved
        else:
            self._original_approved = None


@receiver(post_save, sender=CustomUser)
def assign_permissions_to_groups(sender, instance, created, **kwargs):
    """Signal receiver to assign permissions when a new user is created.
    
    Automatically assigns users to appropriate groups and permissions
    based on their selected role.
    
    :param sender: The model class (CustomUser)
    :param instance: The actual instance being saved
    :param created: Boolean indicating if this is a new instance
    """
    if created:
        try:
            reader_group, created = Group.objects.get_or_create(name='Readers')
            editor_group, created = Group.objects.get_or_create(name='Editors')
            journalist_group, created = Group.objects.get_or_create(
                name='Journalists'
            )

            if instance.role == 'reader':
                instance.groups.add(reader_group)
                # Assign permissions
                reader_permissions = Permission.objects.filter(
                    codename__in=['view_article', 'view_newsletter']
                )
                reader_group.permissions.add(*reader_permissions)
            elif instance.role == 'editor':
                instance.groups.add(editor_group)
                # Assign permissions
                editor_permissions = Permission.objects.filter(
                    codename__in=[
                        'view_article', 'change_article', 'delete_article',
                        'view_newsletter',
                        'change_newsletter',
                        'delete_newsletter'
                    ]
                )
                editor_group.permissions.add(*editor_permissions)
            elif instance.role == 'journalist':
                instance.groups.add(journalist_group)
                # Assign permissions
                journalist_permissions = Permission.objects.filter(
                    codename__in=[
                        'add_article', 'view_article', 'change_article',
                        'delete_article', 'add_newsletter', 'view_newsletter',
                        'change_newsletter', 'delete_newsletter'
                    ]
                )
                journalist_group.permissions.add(*journalist_permissions)
        except (Group.DoesNotExist, Permission.DoesNotExist) as e:
            print(f"Error assigning permissions to groups: {e}")
        except ValueError as e:
            # For unexpected errors, optionally log or handle differently
            print(f"Unexpected error assigning permissions to groups: {e}")


@receiver(pre_save, sender=CustomUser)
def clear_unrelated_fields(sender, instance, **kwargs):
    """Signal receiver to clear role-specific fields when user role changes.
    
    Ensures that users don't retain permissions or data from previous roles
    when their role is updated.
    
    :param sender: The model class (CustomUser)
    :param instance: The actual instance being saved
    """
    # Check if this is an existing user being
    # updated and if the role has changed
    if instance.pk:
        try:
            old_instance = CustomUser.objects.get(pk=instance.pk)
            if old_instance.role != instance.role:
                # Role has changed, clear fields not relevant to the new role
                if instance.role in ['reader', 'editor']:
                    # Clear journalist-related fields
                    instance.articles.clear()
                    instance.newsletters.clear()

                if instance.role != 'reader':
                    # Clear reader-related fields
                    instance.subscriptions_publishers.clear()
                    instance.subscriptions_journalists.clear()

        except CustomUser.DoesNotExist:
            pass  # New user, no need to clear fields yet