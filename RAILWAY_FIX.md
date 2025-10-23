# 🔧 Исправление проблем на Railway

## ❌ Проблема
Django показывает 404 ошибку для `/admin` - это означает, что база данных не инициализирована.

## ✅ Решение

### 1. Выполните команды в Railway Console:

```bash
# Применение миграций
python manage.py migrate

# Инициализация базы данных
python manage.py fix_railway

# Сбор статических файлов
python manage.py collectstatic --noinput
```

### 2. Альтернативный способ (если команда не работает):

```bash
# Применение миграций
python manage.py migrate

# Создание суперпользователя
python manage.py createsuperuser
# Введите: admin / admin@example.com / admin123

# Создание настроек MLM
python manage.py shell
```

В shell выполните:
```python
from mlm.models import MLMSettings
MLMSettings.objects.create(
    registration_fee=100.00,
    green_bonus_first=100.00,
    green_bonus_second=50.00,
    red_bonus=50.00,
    max_partners_per_level=3,
    is_active=True
)
exit()
```

### 3. Проверьте работу:

После выполнения команд проверьте:

- ✅ **Django Admin**: `https://web-production-48c0.up.railway.app/admin/`
- ✅ **Главная**: `https://web-production-48c0.up.railway.app/`
- ✅ **Регистрация**: `https://web-production-48c0.up.railway.app/register/`
- ✅ **Админ-панель**: `https://web-production-48c0.up.railway.app/admin-panel/`

### 4. Доступы:
- **Логин**: admin
- **Пароль**: admin123

## 🎯 Причина проблемы

Railway развернул код, но не применил миграции базы данных, поэтому Django не может найти таблицы и показывает 404 ошибку.

После выполнения команд система будет работать полностью! 🚀
