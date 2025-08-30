# orders/models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ArebiaMejlis(models.Model):
    # ─── Choice constants ────────────────────────────────────────────
    STATUS_PENDING   = "PENDING"
    STATUS_COMPLETED = "COMPLETED"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_COMPLETED, "Completed"),
    ]

    # ─── Primary & timestamps ────────────────────────────────────────
    id          = models.BigAutoField(primary_key=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    # ─── Customer & order meta ───────────────────────────────────────
    customer_name     = models.CharField(max_length=120)  # ⇦ snake_case
    phone             = models.CharField(max_length=30,  blank=True)
    address           = models.CharField(max_length=255, blank=True)
    order_code        = models.CharField(               # ⇦ snake_case
        max_length=30,
        unique=True,
        default="TEMP",
        help_text="Unique order reference",
    )

    receive_order_at  = models.CharField(max_length=120, blank=True)
    completed_order_at= models.CharField(max_length=120, blank=True)

    # ─── Design / pricing ────────────────────────────────────────────
    material_type      = models.CharField(max_length=60, blank=True)
    design_type       = models.CharField(max_length=60, blank=True)

    no_of_mekeda      = models.PositiveIntegerField(default=0)
    no_of_pillow      = models.PositiveIntegerField(default=0)
    uplift_or_height  = models.CharField(max_length=30, blank=True)

    room_size         = models.FloatField()          # m² or your unit
    room_shape        = models.CharField(            # “L”/“U”/“Straight”
        max_length=10,
        default="U",
    )

    price_per_meter   = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    total_price       = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    app_front         = models.CharField(max_length=50, blank=True)
    remaining_payment = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )

    # ─── Geometry ────────────────────────────────────────────────────
    sides    = models.JSONField()  # e.g. [5,4,3]
    segments = models.JSONField()  # e.g. {"side1":[2,3], …}

    # ─── Generated files ─────────────────────────────────────────────
   # …other fields…
    svg_file = models.FileField(upload_to="arebiamejlis/svg/", blank=True, null=True)  # ✅
    pdf_file = models.FileField(upload_to="arebiamejlis/pdf/", blank=True, null=True)  # ✅


    # ─── Status & audit ──────────────────────────────────────────────
    status      = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    created_by  = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="orders_created",
        null=True, blank=True,            # allow anonymous create if needed
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"ArebiaMejlis {self.order_code} – {self.customer_name}"
