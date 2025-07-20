from django.db import migrations


def clean_duplicate_phones(apps, schema_editor):
    """Clean up duplicate phone numbers by keeping the first user and nullifying others."""
    User = apps.get_model('wetnet', 'User')
    
    # Find all users with non-null, non-empty phone numbers
    users_with_phone = User.objects.exclude(phone_number__isnull=True).exclude(phone_number__exact='')
    
    # Group users by phone number
    phone_groups = {}
    for user in users_with_phone:
        if user.phone_number in phone_groups:
            phone_groups[user.phone_number].append(user)
        else:
            phone_groups[user.phone_number] = [user]
    
    # For each duplicate phone number, keep the first user and nullify others
    for phone, users in phone_groups.items():
        if len(users) > 1:
            # Keep the first user (by primary key) and nullify others
            first_user = min(users, key=lambda u: u.pk)
            print(f"Keeping phone {phone} for user {first_user.username}")
            
            # Nullify phone for other users
            for user in users:
                if user != first_user:
                    print(f"  - Removing phone from user {user.username}")
                    user.phone_number = ''
                    user.save()


def reverse_clean_duplicate_phones(apps, schema_editor):
    """No way to reverse this migration."""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('wetnet', '0004_alter_user_phone_number'),
    ]

    operations = [
        migrations.RunPython(clean_duplicate_phones, reverse_clean_duplicate_phones),
    ]
