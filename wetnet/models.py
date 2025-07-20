from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    phone_number = models.CharField(
        max_length=15, 
        blank=True, 
        null=True, 
        unique=True,
        error_messages={
            'unique': 'A user with this phone number already exists.',
        }
    )
    address = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        
    def __str__(self):
        return self.username

    # Override the related_name for groups and permissions
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='wetnet_users',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='wetnet_user_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )