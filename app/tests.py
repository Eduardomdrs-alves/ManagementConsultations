from datetime import date, timedelta

from django.contrib.auth.models import Group, User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from .forms import ConsultationForm, DoctorRegisterForm, PatientRegisterForm
from .models import Consultation, Doctor, Patient


class RegistrationFormsTests(TestCase):
    def test_patient_register_form_creates_user_group_and_patient(self):
        form = PatientRegisterForm(
            data={
                "nome": "Paciente Teste",
                "username": "paciente",
                "email": "paciente@example.com",
                "telefone": "11999999999",
                "birth_date": "2000-01-20",
                "password": "senha-super-segura-123",
                "password_confirm": "senha-super-segura-123",
            }
        )

        self.assertTrue(form.is_valid(), form.errors)
        patient = form.save()

        self.assertEqual(patient.user.username, "paciente")
        self.assertTrue(patient.user.groups.filter(name="Patient").exists())
        self.assertEqual(Patient.objects.count(), 1)

    def test_doctor_register_form_creates_user_group_and_doctor(self):
        form = DoctorRegisterForm(
            data={
                "nome": "Médico Teste",
                "username": "medico",
                "email": "medico@example.com",
                "telefone": "11988888888",
                "birth_date": "1990-02-15",
                "specialty": "CARDIO",
                "crm": "CRM-123",
                "password": "senha-super-segura-123",
                "password_confirm": "senha-super-segura-123",
            }
        )

        self.assertTrue(form.is_valid(), form.errors)
        doctor = form.save()

        self.assertEqual(doctor.user.username, "medico")
        self.assertTrue(doctor.user.groups.filter(name="Doctor").exists())
        self.assertEqual(Doctor.objects.count(), 1)


class ConsultationFlowTests(TestCase):
    def setUp(self):
        self.client = Client()
        patient_group, _ = Group.objects.get_or_create(name="Patient")
        doctor_group, _ = Group.objects.get_or_create(name="Doctor")

        self.patient_user = User.objects.create_user(
            username="paciente",
            password="senha-super-segura-123",
        )
        self.patient_user.groups.add(patient_group)
        self.patient = Patient.objects.create(
            user=self.patient_user,
            nome="Paciente Teste",
            email="paciente@example.com",
            telefone="11999999999",
            birth_date=date(2000, 1, 20),
        )

        self.doctor_user = User.objects.create_user(
            username="medico",
            password="senha-super-segura-123",
        )
        self.doctor_user.groups.add(doctor_group)
        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            nome="Médico Teste",
            email="medico@example.com",
            telefone="11988888888",
            birth_date=date(1990, 2, 15),
            specialty="CARDIO",
            crm="CRM-123",
        )

    def test_consultation_form_allows_updating_same_slot(self):
        consultation = Consultation.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            date=timezone.now() + timedelta(days=5),
            description="Retorno",
        )

        form = ConsultationForm(
            instance=consultation,
            data={
                "doctor": self.doctor.pk,
                "date": consultation.date.strftime("%Y-%m-%dT%H:%M"),
                "description": "Descrição atualizada",
            },
        )

        self.assertTrue(form.is_valid(), form.errors)

    def test_delete_view_executes_soft_delete(self):
        consultation = Consultation.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            date=timezone.now() + timedelta(days=2),
            description="Consulta a excluir",
        )

        self.client.login(username="paciente", password="senha-super-segura-123")
        response = self.client.post(reverse("consultation_delete", args=[consultation.pk]))

        self.assertRedirects(response, reverse("consultation_list"))
        consultation.refresh_from_db()
        self.assertTrue(consultation.is_deleted)
