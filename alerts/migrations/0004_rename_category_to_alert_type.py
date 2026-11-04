from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("alerts", "0003_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="alert",
            old_name="category",
            new_name="alert_type",
        ),
    ]
