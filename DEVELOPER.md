# 👨‍💻 Руководство для разработчиков VidJobs

## 📖 Введение

Этот документ содержит инструкции для разработчиков, желающих внести вклад в проект VidJobs или развернуть его локально для тестирования.

---

## 🛠️ Локальная установка и разработка

### Требования
- Git
- Python 3.10+
- Node.js 18+
- PostgreSQL 12+ (опционально, можно использовать SQLite)
- Redis 6+ (опционально, для асинхронных задач)

### Шаг 1: Клонирование и подготовка

```bash
# Клонировать репозиторий
git clone https://github.com/yourusername/vidjobs.git
cd vidjobs

# Создать ветку для разработки
git checkout -b develop

# Конфигурация Git
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

### Шаг 2: Backend настройка

```bash
cd backend

# Создать виртуальное окружение
python -m venv venv

# Активировать
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Установить зависимости
pip install -r requirements.txt

# Создать .env файл для переменных окружения
cat > .env << EOF
SECRET_KEY=your-secret-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
# DATABASE_URL=postgresql://user:password@localhost:5432/vidjobs
REDIS_URL=redis://localhost:6379/0
EOF

# Создать миграции и применить
python manage.py migrate

# Создать суперпользователя (администратор)
python manage.py createsuperuser
# Username: admin
# Email: admin@vidjobs.kz
# Password: ****

# Загрузить фикстуры (тестовые данные - опционально)
python manage.py loaddata fixtures/initial_data.json

# Запустить dev сервер
python manage.py runserver 0.0.0.0:8000
```

Backend будет доступен на: http://localhost:8000  
Admin панель: http://localhost:8000/admin
API: http://localhost:8000/api/

### Шаг 3: Frontend настройка

```bash
cd ../web

# Установить зависимости
npm install

# Создать .env.local
cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_APP_NAME=VidJobs
EOF

# Запустить dev сервер
npm run dev
```

Frontend будет доступен на: http://localhost:3000

---

## 📚 Файловая структура Backend

```
backend/
├── api/
│   ├── __init__.py
│   ├── admin.py              # Django admin конфигурация
│   ├── apps.py
│   ├── models.py             # Все модели данных здесь
│   ├── views.py              # API endpoints (ViewSets)
│   ├── serializers.py        # Сериализаторы JSON
│   ├── permissions.py        # Кастомные права доступа
│   ├── signals.py            # Django signals
│   ├── urls.py               # URL routing
│   ├── filters.py            # Фильтры для поиска
│   ├── tests.py              # Тесты
│   ├── migrations/           # Миграции БД
│   │   ├── 0001_initial.py
│   │   ├── 0002_*.py
│   │   └── __init__.py
│   └── management/           # Custom commands
│       └── commands/
│           └── generate_fixtures.py
│
├── config/
│   ├── __init__.py
│   ├── settings.py           # Конфигурация Django
│   ├── urls.py               # URL routing (корневой)
│   ├── asgi.py               # ASGI конфиг
│   └── wsgi.py               # WSGI конфиг
│
├── manage.py                 # Django CLI
├── requirements.txt          # Python зависимости
├── .env.example              # Пример переменных окружения
└── docker-compose.yml        # Docker конфигурация
```

---

## 📚 Файловая структура Frontend

```
web/
├── app/
│   ├── layout.tsx            # Root layout
│   ├── page.tsx              # Home page (/)
│   ├── globals.css           # Global styles
│   ├── role-selection/
│   │   └── page.tsx          # /role-selection
│   ├── register/
│   │   └── page.tsx          # /register
│   ├── login/
│   │   └── page.tsx          # /login
│   ├── create-job/
│   │   └── page.tsx          # /create-job
│   ├── jobs/
│   │   ├── page.tsx          # /jobs (листинг)
│   │   └── [id]/
│   │       └── page.tsx      # /jobs/[id] (детали)
│   ├── executor/
│   │   └── [id]/
│   │       └── page.tsx      # /executor/[id] (профиль)
│   └── dashboard/
│       └── page.tsx          # /dashboard
│
├── components/
│   ├── JobCard.tsx           # Карточка заказа
│   ├── JobModal.tsx          # Модальное окно заказа
│   ├── Header.tsx            # Заголовок приложения
│   ├── ChatWindow.tsx        # Компонент чата
│   ├── StatusBadge.tsx       # Бейдж статуса
│   └── NotificationsBell.tsx # Колокольчик уведомлений
│
├── lib/
│   ├── api.ts                # API клиент (Axios)
│   ├── auth.ts               # Функции аутентификации
│   └── utils.ts              # Утилиты
│
├── public/
│   ├── images/               # Изображения
│   └── icons/                # Иконки
│
├── package.json              # NPM конфиг
├── tsconfig.json             # TypeScript конфиг
├── next.config.ts            # Next.js конфиг
├── tailwind.config.ts        # Tailwind конфиг
└── .env.local                # Локальные переменные
```

---

## 🗄️ Работа с базой данных

### Создание миграции

Когда вы изменяете модели, нужно создать миграцию:

```bash
# Создать новую миграцию
python manage.py makemigrations

# Просмотреть SQL для миграции
python manage.py sqlmigrate api 0008

# Применить миграции
python manage.py migrate

# Отменить миграцию
python manage.py migrate api 0007
```

### Работа с Shell

```bash
# Django shell для интерактивной работы
python manage.py shell

# В shell:
from api.models import Job, Profile, User

# Создать пользователя
user = User.objects.create_user('testuser', 'test@vidjobs.kz', 'password123')

# Создать профиль
profile = Profile.objects.create(user=user, role='executor', phone_number='+77771234567')

# Просмотреть все заказы
jobs = Job.objects.all()

# Фильтровать
jobs = Job.objects.filter(status='published', category='construction')

# Обновить
job = Job.objects.first()
job.status = 'assigned'
job.save()
```

### PostgreSQL (дополнительно)

Если используете PostgreSQL вместо SQLite:

```bash
# Установить PostgreSQL драйвер
pip install psycopg2-binary

# Обновить .env
DATABASE_URL=postgresql://user:password@localhost:5432/vidjobs_db

# Создать БД в PostgreSQL
createdb vidjobs_db

# Миграции
python manage.py migrate
```

---

## 🧪 Тестирование

### Backend тесты

```bash
# Запустить все тесты
python manage.py test

# Запустить тесты конкретного приложения
python manage.py test api

# Запустить конкретный тест
python manage.py test api.tests.JobTestCase

# С покрытием кода
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Создаст отчет в htmlcov/
```

### Frontend тесты

```bash
# Запустить Jest тесты
npm test

# С покрытием
npm test -- --coverage

# E2E тесты (Cypress/Playwright)
npm run test:e2e
```

### Пример теста (Backend)

```python
# api/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from api.models import Job, Profile

User = get_user_model()

class JobTestCase(TestCase):
    def setUp(self):
        # Подготовка данных для каждого теста
        self.user = User.objects.create_user('testuser', 'test@vidjobs.kz', 'pass123')
        self.profile = Profile.objects.create(user=self.user, role='customer')
        
    def test_job_creation(self):
        # Тест создания заказа
        job = Job.objects.create(
            owner=self.user,
            title='Test Job',
            description='Test Description',
            category='construction',
            budget=100000
        )
        self.assertEqual(job.title, 'Test Job')
        self.assertEqual(job.status, 'draft')
        
    def test_commission_calculation(self):
        # Тест расчета комиссии (5%)
        job = Job.objects.create(
            owner=self.user,
            title='Test Job',
            description='Test',
            category='construction',
            budget=100000
        )
        self.assertEqual(job.commission_amount, 5000)
```

---

## 🚀 API Development

### Создание новой endpoint

1. **Добавить модель** (если нужно) в `api/models.py`

2. **Создать сериализатор** в `api/serializers.py`:
```python
from rest_framework import serializers
from api.models import MyModel

class MyModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyModel
        fields = ['id', 'name', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']
```

3. **Создать ViewSet** в `api/views.py`:
```python
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from api.models import MyModel
from api.serializers import MyModelSerializer

class MyModelViewSet(viewsets.ModelViewSet):
    queryset = MyModel.objects.all()
    serializer_class = MyModelSerializer
    permission_classes = [IsAuthenticated]
```

4. **Зарегистрировать URL** в `api/urls.py`:
```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import MyModelViewSet

router = DefaultRouter()
router.register(r'mymodels', MyModelViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
```

---

## 📝 Коммиты и Git

### Git Flow

```
main (production)
  ↑
  └─ release (подготовка к релизу)
      ↑
      ├─ develop (основная разработка)
      │   ↑
      │   ├─ feature/название-фичи
      │   ├─ bugfix/название-баги
      │   └─ hotfix/критическая-ошибка
```

### Правила коммитов

```bash
# Формат: <тип>: <описание>
git commit -m "feat: добавить новый API endpoint для заказов"
git commit -m "fix: исправить ошибку в системе рейтинга"
git commit -m "docs: обновить документацию API"
git commit -m "style: переформатировать код"
git commit -m "refactor: переструктурировать компоненты"
git commit -m "test: добавить тесты для профиля"
git commit -m "chore: обновить зависимости"

# Типы коммитов:
# feat - новая фичь
# fix - исправление баги
# docs - документация
# style - форматирование кода
# refactor - переустройство без изменения функций
# test - добавление/изменение тестов
# chore - обновление конфига, зависимостей
```

---

## 🐛 Отладка

### Django Debug Toolbar

```python
# В settings.py
INSTALLED_APPS = [
    'django_extensions',
    'debug_toolbar',
    # ...
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    # ...
]

INTERNAL_IPS = ['127.0.0.1']
```

### Browser DevTools

```javascript
// В браузере (консоль)
// Просмотр API запросов
localStorage.getItem('authToken')

// Тестирование API
fetch('http://localhost:8000/api/jobs/', {
  headers: { 'Authorization': `Bearer ${token}` }
}).then(r => r.json()).then(d => console.log(d))
```

### Logs

```bash
# Backend логи
tail -f logs/django.log

# Frontend логи
npm run build-debug

# Docker логи
docker-compose logs -f backend
docker-compose logs -f frontend
```

---

## 📦 Развертывание (Production)

### Docker

```bash
# Buildить и запустить
docker-compose up -d

# Создать миграции и суперпользователя
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser

# Собрать статические файлы
docker-compose exec backend python manage.py collectstatic --noinput
```

### без Docker

```bash
# Backend
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic
gunicorn config.wsgi:application --bind 0.0.0.0:8000

# Frontend
npm install
npm run build
npm run start
```

---

## 🚨 Troubleshooting

### Backend не запускается

```bash
# 1. Проверить Python версию
python --version  # Должен быть 3.10+

# 2. Проверить зависимости
pip check

# 3. Удалить кэш и пересоздать
rm -rf __pycache__ .pytest_cache
python -m pip install --force-reinstall -r requirements.txt

# 4. Сбросить БД
rm db.sqlite3
python manage.py migrate
```

### Frontend не запускается

```bash
# 1. Удалить node_modules и переустановить
rm -rf node_modules package-lock.json
npm install

# 2. Очистить Next.js кэш
rm -rf .next

# 3. Проверить что backend доступен
curl http://localhost:8000/api/

# 4. Проверить .env файл
cat .env.local
```

### Ошибки в миграциях

```bash
# Посмотреть Applied миграции
python manage.py showmigrations

# Откатить до конкретной миграции
python manage.py migrate api 0007

# Удалить неприменённые миграции
python manage.py migrate api zero  # Откатить все
```

---

## 📚 Полезные ресурсы

- [Django Documentation](https://docs.djangoproject.com/)
- [DRF Documentation](https://www.django-rest-framework.org/)
- [Next.js Documentation](https://nextjs.org/docs)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

## 🤝 Помощь и поддержка

- **Issues**: https://github.com/yourusername/vidjobs/issues
- **Discussions**: https://github.com/yourusername/vidjobs/discussions
- **Slack**: [Join our Slack workspace]
- **Email**: dev@vidjobs.kz

---

**Happy Coding! 🎉**

*Last Updated: April 15, 2024*
