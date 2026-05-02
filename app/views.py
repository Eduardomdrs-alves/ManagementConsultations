from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.shortcuts import redirect

from .models import Consultation
from .forms import ConsultationForm, PatientRegisterForm, DoctorRegisterForm

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

    def get_success_url(self):
        user = self.request.user

        if user.groups.filter(name='Doctor').exists():
            return reverse_lazy('doctor_dashboard')

        if user.groups.filter(name='Patient').exists():
            return reverse_lazy('patient_dashboard')

        return reverse_lazy('login')

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')

class DoctorDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/doctor.html'

class PatientDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/patient.html'

class DoctorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='Doctor').exists()

class PatientRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='Patient').exists()

class PatientRegisterView(CreateView):
    form_class = PatientRegisterForm
    template_name = 'registration/patient_register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Cadastro realizado com sucesso!")
        return super().form_valid(form)

class DoctorRegisterView(CreateView):
    form_class = DoctorRegisterForm
    template_name = 'registration/doctor_register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Cadastro realizado com sucesso!")
        return super().form_valid(form)


class ConsultationListView(LoginRequiredMixin, ListView):
    model = Consultation
    template_name = 'consultation/list.html'
    context_object_name = 'consultations'

    def get_queryset(self):
        user = self.request.user

        if user.groups.filter(name='Patient').exists():
            return Consultation.objects.actives().filter(patient=user.patient)

        if user.groups.filter(name='Doctor').exists():
            return Consultation.objects.actives().filter(doctor=user.doctor)

        return Consultation.objects.none()

class ConsultationCreateView(LoginRequiredMixin, PatientRequiredMixin, CreateView):
    model = Consultation
    form_class = ConsultationForm
    template_name = 'consultation/form.html'
    success_url = reverse_lazy('consultation_list')

    def form_valid(self, form):
        form.instance.patient = self.request.user.patient
        messages.success(self.request, "Consulta agendada com sucesso!")
        return super().form_valid(form)

class ConsultationUpdateView(LoginRequiredMixin, PatientRequiredMixin, UpdateView):
    model = Consultation
    form_class = ConsultationForm
    template_name = 'consultation/form.html'
    success_url = reverse_lazy('consultation_list')

    def get_queryset(self):
        return Consultation.objects.actives().filter(patient=self.request.user.patient)

    def form_valid(self, form):
        messages.success(self.request, "Consulta atualizada com sucesso!")
        return super().form_valid(form)

# DELETE (SOFT DELETE)

class ConsultationDeleteView(LoginRequiredMixin, PatientRequiredMixin, DeleteView):
    model = Consultation
    template_name = 'consultation/confirm_delete.html'
    success_url = reverse_lazy('consultation_list')

    def get_queryset(self):
        return Consultation.objects.actives().filter(patient=self.request.user.patient)

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.delete()  # soft delete
        messages.success(request, "Consulta removida com sucesso!")
        return redirect(self.success_url)