from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("alerts", "0004_rename_category_to_alert_type"),
    ]

    operations = [
        # Suppression de la table AlertPerson
        migrations.DeleteModel(
            name="AlertPerson",
        ),
        # Suppression des champs du modèle Alert
        migrations.RemoveField(
            model_name="alert",
            name="severity",
        ),
        migrations.RemoveField(
            model_name="alert",
            name="vessel",
        ),
        migrations.RemoveField(
            model_name="alert",
            name="position_text",
        ),
    ]
