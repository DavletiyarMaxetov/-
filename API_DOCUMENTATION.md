# VidJobs API Документация

## 📚 Введение

API следует REST принципам и использует JSON для обмена данными. Все endpoints требуют аутентификации через JWT токены (кроме публичных).

### Base URL
```
http://localhost:8000/api/
```

### Аутентификация
```
Header: Authorization: Bearer <access_token>
```

---

## 🔐 Аутентификация

### POST /auth/register/
Регистрация нового пользователя

**Request:**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "secure_password",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response (201):**
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### POST /auth/login/
Вход в систему

**Request:**
```json
{
  "username": "johndoe",
  "password": "secure_password"
}
```

**Response (200):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com"
  }
}
```

### POST /auth/refresh/
Обновление access token

**Request:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

## 👤 Профили

### GET /profile/
Получить профиль текущего пользователя

**Response (200):**
```json
{
  "id": 1,
  "user_id": 1,
  "role": "customer",
  "phone_number": "+7-777-123-45-67",
  "phone_verified": true,
  "bio": "Меня зовут Иван",
  "avatar": "https://...",
  "verification_status": "verified",
  "rating": 4.5,
  "total_reviews": 12,
  "jobs_completed": 8,
  "executor_categories": "Строительство, Ремонт",
  "has_equipment": true,
  "wallet_balance": 125000,
  "total_earned": 500000
}
```

### PUT /profile/
Обновить профиль

**Request:**
```json
{
  "bio": "Обновленное описание",
  "executor_categories": "Сварка, Электросварка",
  "service_radius": 100
}
```

**Response (200):**
```json
{
  "id": 1,
  "bio": "Обновленное описание",
  ...
}
```

### GET /executors/?category=construction&search=сварка
Получить список исполнителей с фильтрацией

**Query Parameters:**
- `category` - категория услуг
- `search` - поиск по имени/описанию
- `min_rating` - минимальный рейтинг (1-5)
- `page` - номер страницы (пагинация)

**Response (200):**
```json
{
  "count": 245,
  "next": "http://localhost:8000/api/executors/?page=2",
  "previous": null,
  "results": [
    {
      "id": 2,
      "username": "ivan_welder",
      "rating": 4.8,
      "total_reviews": 45,
      "jobs_completed": 120,
      "executor_categories": "Сварка, Электросварка",
      "avatar": "https://..."
    }
  ]
}
```

---

## 📋 Заказы (Jobs)

### GET /jobs/?status=published
Получить список заказов

**Query Parameters:**
- `status` - статус (published, assigned, done и т.д.)
- `category` - категория
- `search` - поиск
- `budget_min` / `budget_max` - диапазон бюджета
- `page` - пагинация

**Response (200):**
```json
{
  "count": 523,
  "next": "http://localhost:8000/api/jobs/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Переносина стены",
      "description": "Нужно перенести стену в квартире...",
      "category": "construction",
      "budget": 150000,
      "status": "published",
      "priority": "normal",
      "owner_username": "customer1",
      "created_at": "2024-04-15T10:30:00Z",
      "deadline": "2024-04-22T23:59:59Z",
      "location_address": "Алматы, мкр. Жетысу",
      "bids_count": 5,
      "commission_amount": 7500
    }
  ]
}
```

### POST /jobs/
Создать новый заказ

**Request:**
```json
{
  "title": "Переносина стены",
  "description": "Нужно перенести стену в квартире",
  "category": "construction",
  "budget": 150000,
  "estimated_duration_hours": 8,
  "deadline": "2024-04-22T23:59:59Z",
  "location_address": "Алматы, мкр. Жетысу",
  "location_latitude": 43.2215,
  "location_longitude": 76.9463,
  "priority": "normal"
}
```

**Response (201):**
```json
{
  "id": 123,
  "title": "Переносина стены",
  "description": "Нужно перенести стену в квартире",
  "category": "construction",
  "budget": 150000,
  "status": "published",
  "priority": "normal",
  "owner": 1,
  "created_at": "2024-04-15T10:30:00Z",
  "commission_amount": 7500
}
```

### GET /jobs/{id}/
Получить информацию о конкретном заказе

**Response (200):**
```json
{
  "id": 1,
  "title": "Переносина стены",
  "description": "Нужно перенести стену в квартире",
  "category": "construction",
  "budget": 150000,
  "status": "published",
  "priority": "normal",
  "owner": {
    "id": 1,
    "username": "customer1",
    "rating": 4.7
  },
  "assigned_to": null,
  "ai_generated_description": "Требуется выполнение строительных работ: перенос внутренней стены...",
  "ai_confidence": 0.92,
  "deadline": "2024-04-22T23:59:59Z",
  "location_address": "Алматы, мкр. Жетысу",
  "bids": [
    {
      "id": 1,
      "performer": "ivan_welder",
      "price": 140000,
      "status": "submitted",
      "created_at": "2024-04-15T11:00:00Z"
    }
  ],
  "messages_count": 12,
  "updated_at": "2024-04-15T12:00:00Z"
}
```

### PUT /jobs/{id}/
Обновить заказ (только владелец)

**Request:**
```json
{
  "status": "assigned",
  "assigned_to": 2
}
```

**Response (200):**
```json
{
  "id": 1,
  "status": "assigned",
  "assigned_to": 2,
  ...
}
```

---

## 💬 Сообщения (Чат)

### GET /jobs/{job_id}/messages/
Получить сообщения по заказу

**Response (200):**
```json
[
  {
    "id": 1,
    "job": 1,
    "sender": {
      "id": 1,
      "username": "customer1"
    },
    "text": "Когда вы сможете начать?",
    "created_at": "2024-04-15T11:00:00Z",
    "is_read": true
  },
  {
    "id": 2,
    "job": 1,
    "sender": {
      "id": 2,
      "username": "ivan_welder"
    },
    "text": "Могу начать завтра с 8 утра",
    "created_at": "2024-04-15T11:30:00Z",
    "is_read": false
  }
]
```

### POST /jobs/{job_id}/messages/
Отправить сообщение

**Request:**
```json
{
  "text": "Отлично, жду вас завтра"
}
```

**Response (201):**
```json
{
  "id": 3,
  "job": 1,
  "sender": 1,
  "text": "Отлично, жду вас завтра",
  "created_at": "2024-04-15T11:45:00Z",
  "is_read": false
}
```

---

## 💰 Предложения (Bids)

### GET /jobs/{job_id}/bids/
Получить предложения по заказу

**Response (200):**
```json
[
  {
    "id": 1,
    "job": 1,
    "performer": {
      "id": 2,
      "username": "ivan_welder",
      "rating": 4.8,
      "jobs_completed": 120
    },
    "price": 140000,
    "message": "Могу сделать качественно",
    "status": "submitted",
    "created_at": "2024-04-15T11:00:00Z"
  }
]
```

### POST /jobs/{job_id}/bids/
Подать предложение

**Request:**
```json
{
  "price": 140000,
  "message": "Я специализируюсь на перестройке стен, опыт 10 лет"
}
```

**Response (201):**
```json
{
  "id": 5,
  "job": 1,
  "performer": 2,
  "price": 140000,
  "message": "Я специализируюсь на перестройке стен, опыт 10 лет",
  "status": "submitted",
  "created_at": "2024-04-15T11:50:00Z"
}
```

### PUT /bids/{id}/
Обновить статус предложения (принять/отклонить)

**Request:**
```json
{
  "status": "accepted"
}
```

**Response (200):**
```json
{
  "id": 5,
  "status": "accepted",
  "job": 1,
  "performer": 2
}
```

---

## ⭐ Оценки (Ratings)

### GET /jobs/{job_id}/ratings/
Получить оценки по заказу

**Response (200):**
```json
[
  {
    "id": 1,
    "rater": "customer1",
    "rated_user": "ivan_welder",
    "score": 5,
    "criteria": "quality",
    "comment": "Отличная работа, рекомендую!",
    "created_at": "2024-04-22T16:00:00Z"
  }
]
```

### POST /jobs/{job_id}/ratings/
Оставить оценку

**Request:**
```json
{
  "rated_user": 2,
  "score": 5,
  "criteria": "quality",
  "comment": "Отличная работа, рекомендую!"
}
```

**Response (201):**
```json
{
  "id": 1,
  "rater": 1,
  "rated_user": 2,
  "score": 5,
  "criteria": "quality",
  "comment": "Отличная работа, рекомендую!",
  "created_at": "2024-04-22T16:00:00Z"
}
```

---

## 💳 Финансы (Transactions)

### GET /wallet/
Получить информацию кошелька

**Response (200):**
```json
{
  "balance": 275000,
  "total_earned": 500000,
  "pending": 0,
  "transactions": [
    {
      "id": 1,
      "type": "payment",
      "amount": 142500,
      "status": "completed",
      "job_id": 1,
      "created_at": "2024-04-22T18:00:00Z",
      "description": "Платеж за заказ #1"
    }
  ]
}
```

### POST /wallet/withdraw/
Вывести средства

**Request:**
```json
{
  "amount": 100000,
  "payment_method": "bank_transfer"
}
```

**Response (201):**
```json
{
  "id": 2,
  "type": "withdrawal",
  "amount": 100000,
  "status": "pending",
  "created_at": "2024-04-23T10:00:00Z"
}
```

---

## 🔔 Уведомления

### GET /notifications/
Получить уведомления

**Query Parameters:**
- `is_read` - фильтр по прочитанным (true/false)
- `type` - тип уведомления
- `page` - пагинация

**Response (200):**
```json
{
  "count": 25,
  "results": [
    {
      "id": 1,
      "type": "new_bid",
      "title": "Новое предложение",
      "description": "ivan_welder подал предложение на ваш заказ",
      "job": 1,
      "is_read": false,
      "created_at": "2024-04-15T11:00:00Z"
    }
  ]
}
```

### PATCH /notifications/{id}/
Отметить уведомление как прочитанное

**Request:**
```json
{
  "is_read": true
}
```

**Response (200):**
```json
{
  "id": 1,
  "is_read": true
}
```

---

## 🚨 Коды ошибок

| Код | Описание |
|-----|---------|
| 200 | OK - Успешно |
| 201 | Created - Создано |
| 400 | Bad Request - Неверные данные |
| 401 | Unauthorized - Требуется аутентификация |
| 403 | Forbidden - Доступ запрещен |
| 404 | Not Found - Ресурс не найден |
| 429 | Too Many Requests - Слишком много запросов |
| 500 | Server Error - Ошибка сервера |

---

## 📖 Примеры использования

### JavaScript/TypeScript (Axios)
```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/',
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

// Получить список заказов
const jobs = await api.get('/jobs/?status=published');

// Создать заказ
const newJob = await api.post('/jobs/', {
  title: 'Переносина стены',
  description: 'Нужно перенести стену в квартире',
  category: 'construction',
  budget: 150000
});

// Подать предложение
const bid = await api.post(`/jobs/${jobId}/bids/`, {
  price: 140000,
  message: 'Я могу это сделать'
});
```

### Python (Requests)
```python
import requests

headers = {'Authorization': f'Bearer {token}'}
api_url = 'http://localhost:8000/api'

# Получить заказы
response = requests.get(f'{api_url}/jobs/?status=published', headers=headers)
jobs = response.json()

# Создать заказ
job_data = {
    'title': 'Переносина стены',
    'description': 'Нужно перенести стену в квартире',
    'category': 'construction',
    'budget': 150000
}
response = requests.post(f'{api_url}/jobs/', json=job_data, headers=headers)
```

---

## 🏃 Rate Limiting

- **Лимит**: 100 запросов в минуту
- **Headers**: 
  - `X-RateLimit-Limit`: 100
  - `X-RateLimit-Remaining`: количество оставшихся
  - `X-RateLimit-Reset`: время сброса

---

**API Version**: 1.0  
**Last Updated**: 2024-04-15  
**Status**: Production Ready ✅
