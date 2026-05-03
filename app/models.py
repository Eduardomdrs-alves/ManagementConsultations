from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


class DoctorQuerySet(models.QuerySet):
    def actives(self):
        return self.filter(is_deleted=False)


class PatientQuerySet(models.QuerySet):
    def actives(self):
        return self.filter(is_deleted=False)


class ConsultationQuerySet(models.QuerySet):
    def actives(self):
        return self.filter(is_deleted=False)


class DoctorManager(models.Manager):
    def get_queryset(self):
        return DoctorQuerySet(self.model, using=self._db)

    def actives(self):
        return self.get_queryset().actives()


class PatientManager(models.Manager):
    def get_queryset(self):
        return PatientQuerySet(self.model, using=self._db)

    def actives(self):
        return self.get_queryset().actives()


class ConsultationManager(models.Manager):
    def get_queryset(self):
        return ConsultationQuerySet(self.model, using=self._db)

    def actives(self):
        return self.get_queryset().actives()


class Person(BaseModel):
    nome = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20, blank=True)
    birth_date = models.DateField()

    class Meta:
        abstract = True


class Doctor(Person):
    SPECIALTIES = [
        ("CARDIO", "Cardiologia"),
        ("DERMA", "Dermatologia"),
        ("PED", "Pediatria"),
        ("ORTO", "Ortopedia"),
        ("GERAL", "Clinico Geral"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialty = models.CharField(max_length=20, choices=SPECIALTIES)
    crm = models.CharField(max_length=20, unique=True)

    objects = DoctorManager()

    def delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save()

    def __str__(self):
        return f"{self.nome} ({self.crm})"


class Patient(Person):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    objects = PatientManager()

    def delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save()

    def __str__(self):
        return f"{self.nome} ({self.email})"


class Consultation(BaseModel):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateTimeField()
    description = models.TextField(blank=True)

    objects = ConsultationManager()

    def delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save()

    def __str__(self):
        return f"{self.date.strftime('%d/%m/%Y %H:%M')} - {self.patient.nome} / {self.doctor.nome}"
