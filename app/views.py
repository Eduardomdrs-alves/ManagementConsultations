from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Count
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, ListView, TemplateView, UpdateView

from .forms import ConsultationForm, DoctorRegisterForm, PatientRegisterForm
from .models import Consultation


class CustomLoginView(LoginView):
    template_name = "registration/login.html"
    redirect_authenticated_user = False

    def get_success_url(self):
        user = self.request.user

        if user.groups.filter(name="Doctor").exists():
            return reverse_lazy("doctor_dashboard")

        if user.groups.filter(name="Patient").exists():
            return reverse_lazy("patient_dashboard")

        return reverse_lazy("login")


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("login")


class DoctorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name="Doctor").exists()


class PatientRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name="Patient").exists()


class RegisterChoiceView(TemplateView):
    template_name = "registration/register_choice.html"


class DoctorDashboardView(LoginRequiredMixin, DoctorRequiredMixin, TemplateView):
    template_name = "dashboard/doctor.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        consultations = Consultation.objects.actives().filter(
            doctor=self.request.user.doctor
        ).select_related("patient", "doctor")
        now = timezone.now()
        upcoming = consultations.filter(date__gte=now).order_by("date")

        context["next_consultation"] = upcoming.first()
        context["recent_consultations"] = upcoming[:5]
        context["consultation_count"] = consultations.count()
        context["patient_count"] = (
            consultations.aggregate(total=Count("patient", distinct=True))["total"] or 0
        )
        context["page_name"] = "dashboard"
        context["user_role"] = "doctor"
        return context


class PatientDashboardView(LoginRequiredMixin, PatientRequiredMixin, TemplateView):
    template_name = "dashboard/patient.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        consultations = Consultation.objects.actives().filter(
            patient=self.request.user.patient
        ).select_related("doctor")
        now = timezone.now()
        upcoming = consultations.filter(date__gte=now).order_by("date")
        total = consultations.count()
        finished = consultations.filter(date__lt=now).count()
        progress = int((finished / total) * 100) if total else 0

        context["next_consultation"] = upcoming.first()
        context["recent_consultations"] = consultations.order_by("-date")[:5]
        context["consultation_count"] = total
        context["progress_percent"] = progress
        context["page_name"] = "dashboard"
        context["user_role"] = "patient"
        context["now"] = now
        return context


class PatientRegisterView(CreateView):
    form_class = PatientRegisterForm
    template_name = "registration/patient_register.html"
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, "Cadastro realizado com sucesso!")
        return redirect(self.get_success_url())


class DoctorRegisterView(CreateView):
    form_class = DoctorRegisterForm
    template_name = "registration/doctor_register.html"
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, "Cadastro realizado com sucesso!")
        return redirect(self.get_success_url())


class ConsultationListView(LoginRequiredMixin, ListView):
    model = Consultation
    template_name = "consultation/list.html"
    context_object_name = "consultations"

    def get_queryset(self):
        user = self.request.user
        queryset = Consultation.objects.actives().select_related("doctor", "patient")

        if user.groups.filter(name="Patient").exists():
            return queryset.filter(patient=user.patient).order_by("date")

        if user.groups.filter(name="Doctor").exists():
            return queryset.filter(doctor=user.doctor).order_by("date")

        return Consultation.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        consultations = context["consultations"]
        now = timezone.now()

        context["is_patient"] = self.request.user.groups.filter(name="Patient").exists()
        context["upcoming_count"] = consultations.filter(date__gte=now).count()
        context["finished_count"] = consultations.filter(date__lt=now).count()
        context["page_name"] = "consultations"
        context["user_role"] = "patient" if context["is_patient"] else "doctor"
        context["now"] = now
        return context


class ConsultationCreateView(LoginRequiredMixin, PatientRequiredMixin, CreateView):
    model = Consultation
    form_class = ConsultationForm
    template_name = "consultation/form.html"
    success_url = reverse_lazy("consultation_list")

    def form_valid(self, form):
        form.instance.patient = self.request.user.patient
        messages.success(self.request, "Consulta agendada com sucesso!")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_name"] = "agendar"
        context["form_title"] = "Agendar Consulta"
        context["form_subtitle"] = "Escolha o profissional e o melhor horário para você."
        context["submit_label"] = "Confirmar agendamento"
        context["cancel_url"] = reverse_lazy("consultation_list")
        context["user_role"] = "patient"
        return context


class ConsultationUpdateView(LoginRequiredMixin, PatientRequiredMixin, UpdateView):
    model = Consultation
    form_class = ConsultationForm
    template_name = "consultation/form.html"
    success_url = reverse_lazy("consultation_list")

    def get_queryset(self):
        return Consultation.objects.actives().filter(
            patient=self.request.user.patient
        ).select_related("doctor")

    def form_valid(self, form):
        messages.success(self.request, "Consulta atualizada com sucesso!")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_name"] = "consultations"
        context["form_title"] = "Editar Consulta"
        context["form_subtitle"] = "Atualize a data, médico e motivo do agendamento."
        context["submit_label"] = "Salvar alteracoes"
        context["cancel_url"] = reverse_lazy("consultation_list")
        context["user_role"] = "patient"
        return context


class ConsultationDeleteView(LoginRequiredMixin, PatientRequiredMixin, DeleteView):
    model = Consultation
    template_name = "consultation/confirm_delete.html"
    success_url = reverse_lazy("consultation_list")

    def get_queryset(self):
        return Consultation.objects.actives().filter(
            patient=self.request.user.patient
        ).select_related("doctor")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        messages.success(request, "Consulta removida com sucesso!")
        return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_name"] = "consultations"
        context["user_role"] = "patient"
        return context
