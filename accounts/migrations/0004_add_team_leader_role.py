from django.db import migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_passwordresetrequest"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="role",
            field=django.db.models.fields.CharField(
                choices=[
                    ("SUPERADMIN", "Super Administrateur"),
                    ("ADMIN", "Administrateur"),
                    ("TEAM_LEADER", "Chef de quart"),
                    ("OPERATOR", "Opérateur"),
                ],
                default="OPERATOR",
                max_length=20,
            ),
        ),
    ]
