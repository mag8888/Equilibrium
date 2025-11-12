from django.db import migrations


def seed_tariffs(apps, schema_editor):
    Tariff = apps.get_model('mlm', 'Tariff')
    defaults = [
        {
            'code': 'starter-20',
            'name': 'Starter $20',
            'entry_amount': 20,
        },
        {
            'code': 'starter-50',
            'name': 'Starter $50',
            'entry_amount': 50,
        },
        {
            'code': 'starter-100',
            'name': 'Starter $100',
            'entry_amount': 100,
        },
    ]
    for item in defaults:
        Tariff.objects.get_or_create(code=item['code'], defaults=item)


def unseed_tariffs(apps, schema_editor):
    Tariff = apps.get_model('mlm', 'Tariff')
    Tariff.objects.filter(code__in=['starter-20', 'starter-50', 'starter-100']).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('mlm', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_tariffs, unseed_tariffs),
    ]
