from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import timedelta
from django.utils import timezone

User = get_user_model()


class Job(models.Model):
    """Модель заказа с поддержкой видео, голоса, геолокации и AI генерации ТЗ"""
    
    STATUS_CHOICES = [
        ("draft", "Черновик"),
        ("published", "Опубликован"),
        ("assigned", "Назначен"),
        ("in_progress", "В процессе"),
        ("completed", "Завершен"),
        ("cancelled", "Отменён"),
    ]

    CATEGORY_CHOICES = [
        ("construction", "Строительство"),
        ("repair", "Ремонт"),
        ("cleaning", "Уборка"),
        ("transportation", "Транспортировка"),
        ("agricultural", "Сельхоз работы"),
        ("equipment_rental", "Аренда техники"),
        ("welding", "Сварочные работы"),
        ("other", "Прочее"),
    ]

    PRIORITY_CHOICES = [
        ("low", "Низкий"),
        ("normal", "Обычный"),
        ("high", "Высокий"),
        ("urgent", "Срочный"),
    ]

    # Основная информация
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="jobs_created",
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="jobs_assigned",
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default="normal")
    
    # Текстовая информация
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    budget = models.PositiveIntegerField()
    
    # Видео/голос
    video_file = models.FileField(upload_to="jobs/videos/", null=True, blank=True)
    voice_file = models.FileField(upload_to="jobs/voice/", null=True, blank=True)
    image_base64 = models.TextField(blank=True, null=True)
    
    # AI генерированное ТЗ
    ai_generated_description = models.TextField(blank=True, null=True, help_text="Автоматически сгенерированное ТЗ из видео/голоса")
    ai_confidence = models.DecimalField(max_digits=3, decimal_places=2, default=0.0, help_text="Уверенность AI в 0.0-1.0")
    
    # Геолокация
    location_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location_address = models.CharField(max_length=255, blank=True)
    
    # Время выполнения
    deadline = models.DateTimeField(default=lambda: timezone.now() + timedelta(days=7))
    estimated_duration_hours = models.PositiveIntegerField(default=1, help_text="Приблизительная длительность в часах")
    
    # Требования к исполнителю
    min_rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])
    required_equipment = models.ManyToManyField("Equipment", blank=True, related_name="jobs")
    
    # Финансы
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, help_text="Комиссия платформы (5%)")
    
    # Метаданные
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["owner", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"
    
    def calculate_commission(self):
        """Рассчитать комиссию платформы (5%)"""
        return self.budget * 0.05
    
    def save(self, *args, **kwargs):
        if self.budget:
            self.commission_amount = self.calculate_commission()
        super().save(*args, **kwargs)


class Equipment(models.Model):
    """Модель для спецтехники"""
    
    EQUIPMENT_CHOICES = [
        ("tractor", "Трактор"),
        ("excavator", "Экскаватор"),
        ("loader", "Погрузчик"),
        ("truck", "Грузовик"),
        ("crane", "Кран"),
        ("compressor", "Компрессор"),
        ("generator", "Генератор"),
        ("welding_machine", "Сварочный аппарат"),
        ("other", "Прочее"),
    ]
    
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="equipment")
    equipment_type = models.CharField(max_length=50, choices=EQUIPMENT_CHOICES)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    location_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    cost_per_hour = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=[("available", "Доступна"), ("rented", "В аренде"), ("maintenance", "На обслуживании")], default="available")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Equipment"
    
    def __str__(self):
        return f"{self.get_equipment_type_display()} - {self.owner.username}"


class Document(models.Model):
    """Документы исполнителя (удостоверение, лицензия и т.д.)"""
    
    DOC_TYPES = [
        ("id_card", "Удостоверение личности"),
        ("license", "Профессиональная лицензия"),
        ("certificate", "Сертификат"),
        ("insurance", "Страховка"),
        ("other", "Прочее"),
    ]
    
    executor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="documents")
    doc_type = models.CharField(max_length=50, choices=DOC_TYPES)
    document_file = models.FileField(upload_to="documents/")
    issue_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="verified_documents")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.executor.username} - {self.get_doc_type_display()}"


class Rating(models.Model):
    """Система рейтинга 5-звездочная"""
    
    CRITERIA_CHOICES = [
        ("quality", "Качество выполнения"),
        ("timeline", "Соблюдение сроков"),
        ("communication", "Коммуникация"),
    ]
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="ratings")
    rater = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ratings_given")
    rated_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ratings_received")
    
    score = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    criteria = models.CharField(max_length=50, choices=CRITERIA_CHOICES)
    comment = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ("job", "rater", "rated_user", "criteria")
        ordering = ["-created_at"]
    
    def __str__(self):
        return f"{self.rater.username} → {self.rated_user.username}: {self.score}⭐"


class Profile(models.Model):
    """Профиль пользователя с расширенной информацией для исполнителей"""
    
    ROLE_CUSTOMER = "customer"
    ROLE_EXECUTOR = "executor"
    ROLE_BOTH = "both"

    ROLE_CHOICES = [
        (ROLE_CUSTOMER, "Заказчик"),
        (ROLE_EXECUTOR, "Исполнитель"),
        (ROLE_BOTH, "Обе роли"),
    ]
    
    VERIFICATION_STATUS = [
        ("unverified", "Не верифицирован"),
        ("pending", "На проверке"),
        ("verified", "Верифицирован"),
        ("rejected", "Отклонён"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    
    # Базовая информация
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_CUSTOMER)
    phone_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    phone_verified = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    bio = models.TextField(blank=True, max_length=500)
    
    # Верификация
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default="unverified")
    id_document = models.FileField(upload_to="verification/", null=True, blank=True)
    verified_on = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="+")
    
    # Для исполнителей
    executor_categories = models.CharField(
        max_length=500, 
        blank=True, 
        help_text="Категории услуг через запятую"
    )
    has_equipment = models.BooleanField(default=False, help_text="Есть ли спецтехника")
    geolocation_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    geolocation_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    geolocation_address = models.CharField(max_length=255, blank=True)
    service_radius = models.PositiveIntegerField(default=50, help_text="Радиус обслуживания в км")
    
    # Рейтинг и статистика
    rating = models.DecimalField(
        max_digits=3, 
        decimal_places=1, 
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )
    total_reviews = models.PositiveIntegerField(default=0)
    jobs_completed = models.PositiveIntegerField(default=0)
    
    # Финансовая информация
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    total_earned = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    
    # Время
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_seen = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Profiles"
        indexes = [
            models.Index(fields=["role", "-rating"]),
            models.Index(fields=["verification_status"]),
        ]

    @property
    def is_customer(self) -> bool:
        return self.role in [self.ROLE_CUSTOMER, self.ROLE_BOTH]

    @property
    def is_executor(self) -> bool:
        return self.role in [self.ROLE_EXECUTOR, self.ROLE_BOTH]
    
    @property
    def is_verified(self) -> bool:
        return self.verification_status == "verified"

    def can_post_job(self) -> bool:
        return self.is_customer

    def can_bid(self) -> bool:
        return self.is_executor and self.is_verified
    
    def update_rating(self):
        """Обновить средний рейтинг из всех оценок"""
        ratings = Rating.objects.filter(rated_user=self.user)
        if ratings.exists():
            avg_rating = ratings.aggregate(models.Avg('score'))['score__avg']
            self.rating = round(avg_rating, 1)
            self.total_reviews = ratings.count()
            self.save(update_fields=['rating', 'total_reviews'])

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"


class Message(models.Model):
    """Модель для чата между участниками"""
    
    job = models.ForeignKey(Job, related_name="messages", on_delete=models.CASCADE)
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_messages",
    )
    text = models.TextField()
    attachment = models.FileField(upload_to="messages/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["job", "-created_at"]),
            models.Index(fields=["sender", "-created_at"]),
        ]
    
    def __str__(self):
        return f"{self.sender.username} → Job {self.job.id}"


class Bid(models.Model):
    """Модель предложения от исполнителя"""
    
    STATUS_CHOICES = [
        ("submitted", "Отправлено"),
        ("accepted", "Принято"),
        ("rejected", "Отклонено"),
        ("cancelled", "Отменено"),
    ]
    
    job = models.ForeignKey(Job, related_name="bids", on_delete=models.CASCADE)
    performer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bids_made")
    price = models.PositiveIntegerField()
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="submitted")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("job", "performer")
        indexes = [
            models.Index(fields=["job", "-created_at"]),
            models.Index(fields=["performer", "status"]),
        ]
    
    def __str__(self):
        return f"{self.performer.username} - {self.job.title} - {self.price}"


class Notification(models.Model):
    """Модель уведомлений"""
    
    TYPE_CHOICES = [
        ("new_bid", "Новое предложение"),
        ("bid_accepted", "Предложение принято"),
        ("job_assigned", "Заказ назначен"),
        ("message", "Новое сообщение"),
        ("rating", "Новая оценка"),
        ("job_started", "Заказ начат"),
        ("job_completed", "Заказ завершен"),
        ("payment_received", "Платеж получен"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="notifications",
        null=True,
        blank=True,
    )
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200, default="Уведомление")
    description = models.TextField(blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at", "is_read"]),
            models.Index(fields=["user", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.user.username}: {self.get_type_display()}"


class PaymentTransaction(models.Model):
    """Модель для финансовых транзакций"""
    
    STATUS_CHOICES = [
        ("pending", "В ожидании"),
        ("completed", "Завершена"),
        ("failed", "Ошибка"),
        ("refunded", "Возвращена"),
    ]
    
    TRANSACTION_TYPE = [
        ("payment", "Платеж за заказ"),
        ("refund", "Возврат"),
        ("commission", "Комиссия платформы"),
        ("withdrawal", "Вывод средств"),
        ("deposit", "Пополнение"),
    ]
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="transactions", null=True, blank=True)
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payments_made")
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payments_received", null=True, blank=True)
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=50, choices=TRANSACTION_TYPE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    
    description = models.TextField(blank=True)
    reference_id = models.CharField(max_length=100, unique=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at", "status"]),
            models.Index(fields=["from_user", "-created_at"]),
            models.Index(fields=["to_user", "-created_at"]),
        ]
    
    def __str__(self):
        return f"{self.from_user.username} → {self.to_user.username}: {self.amount} ({self.get_status_display()})"


class VoiceProcessingLog(models.Model):
    """Лог обработки голоса/видео через AI"""
    
    STATUS_CHOICES = [
        ("pending", "Ожидание"),
        ("processing", "Обработка"),
        ("completed", "Завершено"),
        ("failed", "Ошибка"),
    ]
    
    job = models.OneToOneField(Job, on_delete=models.CASCADE, related_name="voice_processing_log")
    
    original_file = models.FileField(upload_to="voice_logs/original/")
    file_type = models.CharField(max_length=20, choices=[("video", "Видео"), ("audio", "Аудио")])
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    extracted_text = models.TextField(blank=True, help_text="Текст из голоса/видео")
    ai_processed_description = models.TextField(blank=True, help_text="Обработанное AI описание")
    confidence_score = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    
    processing_time_seconds = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "-created_at"]),
        ]
    
    def __str__(self):
        return f"Job {self.job.id} - {self.get_status_display()}"


@receiver(post_save, sender=User)
def create_profile_for_user(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)