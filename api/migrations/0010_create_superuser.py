# Generated manually to create initial superuser

from django.db import migrations
from api.models import CustomUser

def create_superuser(apps, schema_editor):
    """Create a superuser in the customer user model using CustomUserManager."""
    user_manager = CustomUser.objects
    user_manager.create_superuser(
        email='khadijahdarragi2003@gmail.com',
        password='edcsdf4321',
        name='Khadijah Darragi',
    )

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_populate_initial_data'),  
    ]

    operations = [
        migrations.RunPython(create_superuser),
    ]
 
