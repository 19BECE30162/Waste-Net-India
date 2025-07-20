import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wetnetindia.settings')
django.setup()

from django.contrib.auth import get_user_model
from collections import defaultdict

User = get_user_model()

# Find all users with non-null, non-empty phone numbers
users_with_phone = User.objects.exclude(phone_number__isnull=True).exclude(phone_number__exact='')

# Group users by phone number
phone_groups = defaultdict(list)
for user in users_with_phone:
    phone_groups[user.phone_number].append(user)

# Process duplicates
for phone, users in phone_groups.items():
    if len(users) > 1:
        print(f"\nFound {len(users)} users with phone number: {phone}")
        # Sort users by primary key (oldest first)
        users_sorted = sorted(users, key=lambda u: u.pk)
        
        # Keep the first user (oldest)
        keeper = users_sorted[0]
        print(f"  - Keeping phone for user: {keeper.username} (ID: {keeper.id})")
        
        # Nullify phone for other users
        for user in users_sorted[1:]:
            print(f"  - Removing phone from user: {user.username} (ID: {user.id})")
            user.phone_number = ''
            user.save()

print("\nDuplicate phone numbers have been cleaned up.")
print("You can now run 'python manage.py migrate' to apply the unique constraint.")
