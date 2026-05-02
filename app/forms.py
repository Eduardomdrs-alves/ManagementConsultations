from django import forms
from django.utils import timezone
from django.contrib.auth.models import User

from .models import Consultation, Doctor, Patient

class ConsultationForm(forms.ModelForm):
    class Meta:
        model = Consultation
        fields = ['doctor', 'date', 'description']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean_date(self):
        date = self.cleaned_data.get('date')

        if date and date < timezone.now():
            raise forms.ValidationError("Não é possível agendar no passado.")

        return date

    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get('doctor')
        date = cleaned_data.get('date')

        if doctor and date:
            exists = Consultation.objects.actives().filter(
                doctor=doctor,
                date=date
            ).exists()

            if exists:
                raise forms.ValidationError(
                    "Já existe uma consulta com este médico neste horário."
                )

        return cleaned_data

class PatientRegisterForm(forms.ModelForm):
    username = forms.CharField()
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Patient
        fields = ['nome', 'telefone', 'birth_date']

    def save(self, commit=True):
        # cria usuário
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password']
        )

        # adiciona ao grupo
        group = Group.objects.get(name='Patient')
        user.groups.add(group)

        # cria paciente
        patient = Patient.objects.create(
            user=user,
            nome=self.cleaned_data['nome'],
            email=self.cleaned_data['email'],
            telefone=self.cleaned_data['telefone'],
            birth_date=self.cleaned_data['birth_date']
        )

        return patient
    
class DoctorRegisterForm(forms.ModelForm):
    username = forms.CharField()
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Doctor
        fields = ['nome', 'telefone', 'birth_date', 'specialty', 'crm']

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password']
        )

        group = Group.objects.get(name='Doctor')
        user.groups.add(group)

        doctor = Doctor.objects.create(
            user=user,
            nome=self.cleaned_data['nome'],
            email=self.cleaned_data['email'],
            telefone=self.cleaned_data['telefone'],
            birth_date=self.cleaned_data['birth_date'],
            specialty=self.cleaned_data['specialty'],
            crm=self.cleaned_data['crm']
        )

        return doctor
    
