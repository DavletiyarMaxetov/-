# 🚀 Руководство по развертыванию VidJobs (Production)

## 📋 Содержание
1. [Предварительные требования](#требования)
2. [Развертывание с Docker](#docker)
3. [Развертывание на AWS](#aws)
4. [Развертывание на DigitalOcean](#digitalocean)
5. [CI/CD Pipeline](#cicd)
6. [Мониторинг и логирование](#мониторинг)
7. [Масштабирование](#масштабирование)

---

## 📌 Требования

### Для любого хостинга нужно:
- **VPS/Server** - минимум 2GB RAM, 10 GB SSD (для начала)
- **Домен** - например vidjobs.kz
- **SSL сертификат** - Let's Encrypt (бесплатно)
- **Почтовый сервис** - Mailgun, SendGrid (для отправки писем)
- **Платежная система** - Kaspi API, Stripe API
- **Storage** - AWS S3 или локальное хранилище
- **CDN** - CloudFlare (опционально, но рекомендуется)

---

## 🐳 Docker Development

### Структура docker-compose.yml

```yaml
version: '3.8'

services:
  # PostgreSQL БД
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: vidjobs_db
      POSTGRES_USER: vidjobs_user
      POSTGRES_PASSWORD: your_secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U vidjobs_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis для кэша и очередей
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Backend Django
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    command: sh -c "
      python manage.py migrate &&
      python manage.py collectstatic --noinput &&
      gunicorn config.wsgi:application --bind 0.0.0.0:8000
    "
    environment:
      DATABASE_URL: postgresql://vidjobs_user:your_secure_password@postgres:5432/vidjobs_db
      REDIS_URL: redis://redis:6379/0
      SECRET_KEY: ${SECRET_KEY}
      DEBUG: 0
      ALLOWED_HOSTS: localhost,127.0.0.1,vidjobs.kz
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./backend:/app
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    ports:
      - "8000:8000"
    networks:
      - vidjobs_network

  # Celery для асинхронных задач
  celery:
    build:
      context: ./backend
      dockerfile: Dockerfile
    command: celery -A config worker -l info
    environment:
      DATABASE_URL: postgresql://vidjobs_user:your_secure_password@postgres:5432/vidjobs_db
      REDIS_URL: redis://redis:6379/0
      SECRET_KEY: ${SECRET_KEY}
    depends_on:
      - postgres
      - redis
    volumes:
      - ./backend:/app
    networks:
      - vidjobs_network

  # Frontend Next.js
  frontend:
    build:
      context: ./web
      dockerfile: Dockerfile
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000/api
    ports:
      - "3000:3000"
    volumes:
      - ./web:/app
    networks:
      - vidjobs_network

  # Nginx reverse proxy
  nginx:
    image: nginx:latest
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - static_volume:/app/staticfiles:ro
      - media_volume:/app/media:ro
    depends_on:
      - backend
      - frontend
    networks:
      - vidjobs_network

volumes:
  postgres_data:
  redis_data:
  static_volume:
  media_volume:

networks:
  vidjobs_network:
    driver: bridge
```

### Запуск с Docker

```bash
# 1. Создать .env файл
cat > .env << EOF
SECRET_KEY=your-very-secure-secret-key-here
DEBUG=0
POSTGRES_PASSWORD=your_secure_password
EOF

# 2. Buildить images
docker-compose build

# 3. Запустить контейнеры
docker-compose up -d

# 4. Запустить миграции
docker-compose exec backend python manage.py migrate

# 5. Создать суперпользователя
docker-compose exec backend python manage.py createsuperuser

# 6. Загрузить фиксчеры (тестовые данные)
docker-compose exec backend python manage.py loaddata fixtures/initial_data.json

# 7. Проверить статус
docker-compose ps

# 8. Просмотреть логи
docker-compose logs -f backend
docker-compose logs -f frontend
```

---

## ☁️ AWS Deployment

### Шаг 1: EC2 инстанс

```bash
# Запустить Ubuntu 22.04 LTS инстанс
# Тип: t3.medium (для начала)
# Storage: 20GB gp3
# Security Group: открыть порты 22 (SSH), 80 (HTTP), 443 (HTTPS)

# Подключиться к инстансу
ssh -i your-key.pem ubuntu@your-instance-ip

# Обновить систему
sudo apt update && sudo apt upgrade -y

# Установить базовые пакеты
sudo apt install -y \
  curl wget git \
  python3.10 python3.10-venv python3-pip \
  postgresql postgresql-contrib \
  redis-server \
  nginx

# Установить Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

### Шаг 2: Развернуть приложение

```bash
# Клонировать репозиторий
git clone https://github.com/yourusername/vidjobs.git
cd vidjobs

# Создать .env с AWS переменными
cat > .env << EOF
SECRET_KEY=your-aws-secret-key
DEBUG=0
ALLOWED_HOSTS=your-domain.kz,www.your-domain.kz
DATABASE_URL=postgresql://vidjobs_user:password@localhost/vidjobs_db
REDIS_URL=redis://localhost:6379/0
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_STORAGE_BUCKET_NAME=vidjobs-media
AWS_S3_REGION_NAME=eu-central-1
EOF

# Запустить с Docker
sudo docker-compose up -d
```

### Шаг 3: SSL сертификат (Let's Encrypt)

```bash
# Установить Certbot
sudo apt install -y certbot python3-certbot-nginx

# Получить сертификат
sudo certbot certonly --standalone -d your-domain.kz -d www.your-domain.kz

# Сертификаты будут в: /etc/letsencrypt/live/your-domain.kz/

# Обновлять автоматически (добавить в cron)
sudo certbot renew --dry-run
```

### Шаг 4: Nginx конфигурация

```nginx
# /etc/nginx/conf.d/vidjobs.conf

upstream backend {
    server localhost:8000;
}

upstream frontend {
    server localhost:3000;
}

# Редирект с HTTP на HTTPS
server {
    listen 80;
    server_name your-domain.kz www.your-domain.kz;
    return 301 https://$server_name$request_uri;
}

# HTTPS конфигурация
server {
    listen 443 ssl http2;
    server_name your-domain.kz www.your-domain.kz;

    # SSL сертификаты
    ssl_certificate /etc/letsencrypt/live/your-domain.kz/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.kz/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Compression
    gzip on;
    gzip_types text/plain text/css text/javascript application/json;
    gzip_min_length 1000;

    # Backend API
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Static files
    location /static/ {
        alias /app/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /app/media/;
        expires 7d;
    }

    # Admin panel
    location /admin/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Шаг 5: Systemd Services

```bash
# /etc/systemd/system/docker-vidjobs.service
[Unit]
Description=VidJobs Docker Application
After=docker.service
Requires=docker.service

[Service]
WorkingDirectory=/home/ubuntu/vidjobs
ExecStart=/usr/bin/docker-compose up
ExecStop=/usr/bin/docker-compose down
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

---

## 🌊 DigitalOcean App Platform

### Шаг 1: Подготовка

```bash
# Создать рабочий .do/app.yaml
cat > .do/app.yaml << EOF
name: vidjobs
static_sites:
  - name: frontend
    source_dir: web
    build_command: npm install && npm run build
    envs:
      - key: NEXT_PUBLIC_API_URL
        value: https://api.your-domain.kz
      - key: NODE_ENV
        value: production

services:
  - name: backend
    source_dir: backend
    build_command: pip install -r requirements.txt
    run_command: gunicorn config.wsgi --bind 0.0.0.0:8080 --workers 4
    envs:
      - key: DEBUG
        value: 0
      - key: SECRET_KEY
        value: ${SECRET_KEY}
      - key: DATABASE_URL
        value: ${DB_CONNECTION_STRING}
      - key: REDIS_URL
        value: redis://redis:6379
    http_port: 8080

  - name: celery
    source_dir: backend
    build_command: pip install -r requirements.txt
    run_command: celery -A config worker -l info
    envs:
      - key: DEBUG
        value: 0
      - key: SECRET_KEY
        value: ${SECRET_KEY}

databases:
  - name: postgres
    engine: PG
    version: 14
    production: true

  - name: redis
    engine: REDIS
    version: 7
    production: true
EOF

# Деплоить через DigitalOcean CLI
doctl apps create --spec .do/app.yaml
```

---

## 🔄 CI/CD Pipeline (GitHub Actions)

### .github/workflows/deploy.yml

```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  tests:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install Backend Dependencies
      run: |
        cd backend
        pip install -r requirements.txt
    
    - name: Run Backend Tests
      run: |
        cd backend
        python manage.py test
    
    - name: Run Backend Linting
      run: |
        cd backend
        pip install flake8
        flake8 api --max-line-length=100
    
    - name: Set up Node
      uses: actions/setup-node@v3
      with:
        node-version: '18'
    
    - name: Install Frontend Dependencies
      run: |
        cd web
        npm install
    
    - name: Run Frontend Tests
      run: |
        cd web
        npm run test
    
    - name: Build Frontend
      run: |
        cd web
        npm run build

  deploy:
    needs: tests
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to AWS
      env:
        AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
        AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
      run: |
        # Скрипт развертывания
        ./scripts/deploy.sh
    
    - name: Notify Slack
      uses: slackapi/slack-github-action@v1
      with:
        payload: |
          {
            "text": "✅ VidJobs успешно развернут в Production"
          }
      env:
        SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

---

## 📊 Мониторинг и логирование

### Prometheus + Grafana

```bash
# Установить Prometheus
docker run -d \
  -p 9090:9090 \
  -v ./prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus

# Установить Grafana
docker run -d \
  -p 3001:3000 \
  grafana/grafana

# Установить Node Exporter (для системного мониторинга)
docker run -d \
  -p 9100:9100 \
  prom/node-exporter
```

### Logging (ELK Stack)

```bash
# Elasticsearch + Logstash + Kibana
docker-compose up -d elasticsearch logstash kibana

# Forwarding логов в ELK
# В settings.py Django:
LOGGING = {
    'version': 1,
    'handlers': {
        'logstash': {
            'level': 'INFO',
            'class': 'logstash_formatter.LogstashFormatterHandler',
            # ...
        },
    },
}
```

---

## 📈 Масштабирование

### Горизонтальное масштабирование

```bash
# Запустить несколько инстансов Backend за Load Balancer
# AWS Load Balancer / Nginx upstream

upstream backend_pool {
    server backend1.internal:8000;
    server backend2.internal:8000;
    server backend3.internal:8000;
    least_conn;  # Least connections балансирование
}
```

### Кэширование с Redis

```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Использование
from django.core.cache import cache
cache.set('jobs_list', jobs, timeout=300)  # 5 минут кэша
```

### Database оптимизация

```sql
-- Индексы для быстрого поиска
CREATE INDEX idx_job_status ON api_job(status);
CREATE INDEX idx_job_created_at ON api_job(-created_at);
CREATE INDEX idx_profile_rating ON api_profile(rating DESC);
CREATE INDEX idx_message_job_id ON api_message(job_id);

-- Connection pooling с PgBouncer
# pgbouncer.ini
[databases]
vidjobs_db = host=localhost port=5432 dbname=vidjobs_db

[pgbouncer]
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 20
```

---

## ✅ Чеклист при запуске

- [ ] Домен куплен и указывает на сервер
- [ ] SSL сертификат установлен
- [ ] БД создана и миграции применены
- [ ] Суперпользователь создан
- [ ] Статические файлы собраны (collectstatic)
- [ ] Переменные окружения установлены
- [ ] Backup стратегия установлена
- [ ] Monitoring настроен
- [ ] Логирование работает
- [ ] Tests проходят
- [ ] CI/CD pipeline работает
- [ ] Email отправка работает
- [ ] Платежная система интегрирована
- [ ] S3/Storage настроено
- [ ] Rate limiting установлен
- [ ] Backup БД работает автоматически

---

**Успешного развертывания! 🚀**

*Last Updated: April 15, 2024*
