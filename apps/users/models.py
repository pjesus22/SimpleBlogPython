from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from ..utils.base_model import BaseModel


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin'
        AUTHOR = 'author'

    base_role = Role.ADMIN
    role = models.CharField(
        choices=Role.choices,
        max_length=50,
        default=base_role,
    )

    def save(self, *args, **kwargs):
        self.full_clean()
        if not self.pk:
            self.role = self.base_role
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.username} ({self.role})'


class AdminManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(role=User.Role.ADMIN)


class Admin(User):
    objects = AdminManager()
    is_superuser = True
    is_staff = True

    class Meta:
        proxy = True


class AuthorManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(role=User.Role.AUTHOR)


class Author(User):
    base_role = User.Role.AUTHOR
    objects = AuthorManager()

    class Meta:
        proxy = True


def get_user_profile_picture_upload_path(instance, filename):
    return f'{instance.user.id}/image/profile/{filename}'


class AuthorProfile(models.Model):
    user = models.OneToOneField(
        Author,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='profile',
    )
    profile_picture = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True,
    )
    bio = models.TextField()

    def __str__(self):
        return f'{self.user.username} ({self.user.role}) profile'


@receiver(post_save, sender=Author)
def create_author_profile(sender, instance, created, **kwargs):
    if created and instance.role == User.Role.AUTHOR:
        AuthorProfile.objects.create(user=instance)


class SocialAccount(BaseModel):
    provider = models.CharField(max_length=50)
    username = models.CharField(max_length=255)
    url = models.URLField(unique=True)
    profile = models.ForeignKey(
        AuthorProfile, on_delete=models.CASCADE, related_name='social_accounts'
    )

    def __str__(self):
        return f'{self.username} ({self.provider})'
