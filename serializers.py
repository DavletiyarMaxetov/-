from rest_framework import serializers
from .models import Job, Message, Bid, Profile, Notification


class JobSerializer(serializers.ModelSerializer):
    # UI-ға ыңғайлы: автор username
    owner_username = serializers.CharField(source="owner.username", read_only=True)

    class Meta:
        model = Job
        fields = "__all__"
        # owner-ды сервер қояды, статус/assigned_to бөлек endpoint арқылы басқарылсын
        read_only_fields = ["owner", "status", "assigned_to", "created_at"]


class MessageSerializer(serializers.ModelSerializer):
    # sender nullable болғандықтан, CharField(source="sender.username") құлап қалуы мүмкін
    sender_username = serializers.SerializerMethodField()

    def get_sender_username(self, obj):
        return getattr(obj.sender, "username", None)

    class Meta:
        model = Message
        fields = "__all__"
        # sender және job-ты сервер өзі қояды
        read_only_fields = ["sender", "job"]


class BidSerializer(serializers.ModelSerializer):
    performer_username = serializers.CharField(source="performer.username", read_only=True)

    def validate(self, attrs):
        """
        Role rule:
        - Тек executor/both bid бере алады
        Business rule:
        - Bid тек published job-қа ғана (job attrs ішінде бар болса тексереміз)
        Ескерту: job көбіне views-та serializer.save(job=...) арқылы беріледі,
        сондықтан job.status тексеруді views-та да міндетті түрде қайталаймыз.
        """
        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            user = request.user

            if not hasattr(user, "profile"):
                raise serializers.ValidationError("Profile жоқ. Қайта кіріп көр.")

            if not user.profile.can_bid():
                raise serializers.ValidationError("Тек орындаушы (executor/both) bid бере алады.")

            job = attrs.get("job")
            if job and job.status != "published":
                raise serializers.ValidationError("Bid тек published job-қа ғана беріледі.")

        return attrs

    class Meta:
        model = Bid
        fields = "__all__"
        # performer/job-ты сервер өзі қояды
        read_only_fields = ["performer", "job"]


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Profile
        fields = ["id", "username", "role", "verified"]
        read_only_fields = ["id", "username", "verified"]


class NotificationSerializer(serializers.ModelSerializer):
    job_title = serializers.SerializerMethodField()

    def get_job_title(self, obj):
        return getattr(obj.job, "title", None)

    class Meta:
        model = Notification
        fields = ["id", "type", "text", "job", "job_title", "is_read", "created_at"]
        read_only_fields = ["id", "type", "text", "job", "job_title", "created_at"]