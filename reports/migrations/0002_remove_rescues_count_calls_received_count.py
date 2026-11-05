from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("reports", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="dailyreport",
            name="rescues_count",
        ),
        migrations.RemoveField(
            model_name="dailyreport",
            name="calls_received_count",
        ),
    ]
