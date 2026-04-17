from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .models import Job, Message, Bid, Profile, Notification
from .serializers import (
    JobSerializer,
    MessageSerializer,
    BidSerializer,
    ProfileSerializer,
    NotificationSerializer,
)


def get_profile(user):
    if not user or not user.is_authenticated:
        return None
    return getattr(user, "profile", None)


def require_profile(user):
    profile = get_profile(user)
    if not profile:
        raise PermissionDenied("Profile жоқ. Қайта кіріп көр немесе profile жаса.")
    return profile


def can_bid(user) -> bool:
    profile = get_profile(user)
    return bool(profile and profile.can_bid())


def can_post_job(user) -> bool:
    profile = get_profile(user)
    return bool(profile and profile.can_post_job())


class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all().order_by("-created_at")
    serializer_class = JobSerializer

    # Қай action-ға қандай рұқсат
    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    # Job жасағанда owner автомат қойылады + role тексеру
    def perform_create(self, serializer):
        if not can_post_job(self.request.user):
            raise PermissionDenied("Тек customer/both job жариялай алады.")
        serializer.save(owner=self.request.user)

    # Тек өз job-ын ғана өшіре алады
    def perform_destroy(self, instance):
        if instance.owner_id != self.request.user.id:
            raise PermissionDenied("Сіз бұл тапсырысты өшіре алмайсыз.")
        instance.delete()

    # =======================
    # Messages: GET/POST (чат)
    # =======================
    @action(detail=True, methods=["get", "post"], url_path="messages", permission_classes=[IsAuthenticated])
    def messages(self, request, pk=None):
        job = self.get_object()

        is_owner = (job.owner_id == request.user.id)
        is_assigned = (job.assigned_to_id == request.user.id)
        is_bidder = Bid.objects.filter(job=job, performer=request.user).exists()

        if not (is_owner or is_assigned or is_bidder):
            return Response(
                {"detail": "Чатқа тек тапсырыс иесі/тағайындалған орындаушы/ұсыныс бергендер ғана жаза алады."},
                status=403
            )

        if request.method == "GET":
            qs = Message.objects.filter(job=job).order_by("created_at")
            return Response(MessageSerializer(qs, many=True).data)

        # POST
        text = request.data.get("text", "")
        serializer = MessageSerializer(data={"text": text}, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save(job=job, sender=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # =======================
    # Bids: GET/POST (ұсыныстар)
    # =======================
    @action(detail=True, methods=["get", "post"], url_path="bids", permission_classes=[IsAuthenticated])
    def bids(self, request, pk=None):
        job = self.get_object()

        if request.method == "GET":
            # Owner бәрін көреді, басқалар тек өз bid-ін
            if job.owner_id == request.user.id:
                qs = Bid.objects.filter(job=job).order_by("-created_at")
            else:
                qs = Bid.objects.filter(job=job, performer=request.user).order_by("-created_at")
            return Response(BidSerializer(qs, many=True).data)

        # POST
        require_profile(request.user)

        if not can_bid(request.user):
            return Response({"detail": "Тек орындаушы (executor/both) ғана ұсыныс бере алады."}, status=403)

        if job.owner_id == request.user.id:
            return Response({"detail": "Өз тапсырысыңызға ұсыныс бере алмайсыз."}, status=400)

        if job.status != "published":
            return Response({"detail": "Бұл тапсырысқа енді ұсыныс бере алмайсыз (status != published)."}, status=400)

        serializer = BidSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        bid = serializer.save(job=job, performer=request.user)

        # notify owner: new bid
        if job.owner_id and job.owner_id != request.user.id:
            Notification.objects.create(
                user_id=job.owner_id,
                job=job,
                type=Notification.TYPE_BID,
                text=f"Жаңа ұсыныс түсті: {request.user.username}",
            )

        return Response(BidSerializer(bid).data, status=status.HTTP_201_CREATED)

    # =======================
    # Assign: owner ғана орындаушы таңдай алады
    # =======================
    @action(detail=True, methods=["post"], url_path="assign", permission_classes=[IsAuthenticated])
    def assign(self, request, pk=None):
        job = self.get_object()

        # тек owner assign жасай алады
        if job.owner_id != request.user.id:
            return Response({"detail": "Only owner can assign."}, status=403)

        # job published болуы керек
        if job.status != "published":
            return Response({"detail": "Job must be in 'published' status."}, status=400)

        performer_id = request.data.get("performer_id")
        if not performer_id:
            return Response({"detail": "performer_id required"}, status=400)

        # performer профилін табу
        try:
            performer_profile = Profile.objects.select_related("user").get(user_id=performer_id)
        except Profile.DoesNotExist:
            return Response({"detail": "Performer profile not found."}, status=400)

        # performer executor немесе both болуы керек
        if performer_profile.role not in [Profile.ROLE_EXECUTOR, Profile.ROLE_BOTH]:
            return Response({"detail": "User is not executor."}, status=400)

        # performer осы job-қа bid берген бе
        if not Bid.objects.filter(job=job, performer_id=performer_id).exists():
            return Response({"detail": "User has no bid for this job."}, status=400)

        job.assigned_to_id = performer_id
        job.status = "assigned"
        job.save(update_fields=["assigned_to", "status"])

        # notify performer: assigned
        Notification.objects.create(
            user_id=performer_id,
            job=job,
            type=Notification.TYPE_ASSIGNED,
            text=f"Сіз тапсырмаға тағайындалдыңыз: {job.title}",
        )

        return Response({"status": "assigned", "assigned_to": performer_id})

    # =======================
    # Mark done: owner немесе assigned performer
    # =======================
    @action(detail=True, methods=["post"], url_path="mark-done", permission_classes=[IsAuthenticated])
    def mark_done(self, request, pk=None):
        job = self.get_object()

        is_owner = (job.owner_id == request.user.id)
        is_assigned = (job.assigned_to_id == request.user.id)

        if not (is_owner or is_assigned):
            return Response(
                {"detail": "Тек owner немесе орындаушы ғана жұмысты аяқтай алады."},
                status=403
            )

        if job.status != "assigned":
            return Response(
                {"detail": "Job must be 'assigned' to mark done."},
                status=400
            )

        job.status = "done"
        job.save(update_fields=["status"])

        # notify both sides: done
        if job.owner_id:
            Notification.objects.create(
                user_id=job.owner_id,
                job=job,
                type=Notification.TYPE_DONE,
                text=f"Тапсырыс аяқталды: {job.title}",
            )

        if job.assigned_to_id:
            Notification.objects.create(
                user_id=job.assigned_to_id,
                job=job,
                type=Notification.TYPE_DONE,
                text=f"Тапсырыс аяқталды: {job.title}",
            )

        return Response({"status": "done"})

    # =======================
    # My Jobs / My Assigned Jobs / My Bids
    # =======================
    @action(detail=False, methods=["get"], url_path="my-jobs", permission_classes=[IsAuthenticated])
    def my_jobs(self, request):
        qs = Job.objects.filter(owner=request.user).order_by("-created_at")
        return Response(JobSerializer(qs, many=True).data)

    @action(detail=False, methods=["get"], url_path="my-assigned-jobs", permission_classes=[IsAuthenticated])
    def my_assigned_jobs(self, request):
        qs = Job.objects.filter(assigned_to=request.user).order_by("-created_at")
        return Response(JobSerializer(qs, many=True).data)

    @action(detail=False, methods=["get"], url_path="my-bids", permission_classes=[IsAuthenticated])
    def my_bids(self, request):
        qs = Bid.objects.filter(performer=request.user).order_by("-created_at")
        return Response(BidSerializer(qs, many=True).data)


class MyProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        return Response(ProfileSerializer(profile).data)

    def post(self, request):
        """
        POST body:
        { "role": "customer" | "executor" | "both" }
        """
        role = request.data.get("role")
        if role not in [Profile.ROLE_CUSTOMER, Profile.ROLE_EXECUTOR, Profile.ROLE_BOTH]:
            return Response({"detail": "Invalid role"}, status=400)

        profile, _ = Profile.objects.get_or_create(user=request.user)
        profile.role = role
        profile.save(update_fields=["role"])
        return Response(ProfileSerializer(profile).data)


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Notification.objects.filter(user=self.request.user).order_by("-created_at")
        is_read = self.request.query_params.get("is_read")
        if is_read in ["true", "false"]:
            qs = qs.filter(is_read=(is_read == "true"))
        return qs

    @action(detail=True, methods=["post"], url_path="read")
    def mark_read(self, request, pk=None):
        n = self.get_object()
        if n.user_id != request.user.id:
            return Response({"detail": "Forbidden"}, status=403)
        n.is_read = True
        n.save(update_fields=["is_read"])
        return Response({"status": "ok", "id": n.id, "is_read": n.is_read})

    @action(detail=False, methods=["get"], url_path="unread-count")
    def unread_count(self, request):
        cnt = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({"unread": cnt})

    @action(detail=False, methods=["post"], url_path="read-all")
    def read_all(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({"status": "ok"})