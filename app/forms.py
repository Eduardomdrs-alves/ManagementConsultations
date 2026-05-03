from django import forms
from django.contrib.auth.models import Group, User
from django.utils import timezone

from .models import Consultation, Doctor, Patient


class ConsultationForm(forms.ModelForm):
    class Meta:
        model = Consultation
        fields = ["doctor", "date", "description"]
        widgets = {
            "date": forms.DateTimeInput(
                attrs={"type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
            "description": forms.Textarea(attrs={"rows": 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["doctor"].queryset = Doctor.objects.actives().order_by("nome")
        self.fields["date"].input_formats = ["%Y-%m-%dT%H:%M"]

        if self.instance.pk and self.instance.date:
            self.initial["date"] = self.instance.date.strftime("%Y-%m-%dT%H:%M")

    def clean_date(self):
        date = self.cleaned_data.get("date")

        if date and date < timezone.now():
            raise forms.ValidationError("Não é possível agendar no passado.")

        return date

    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get("doctor")
        date = cleaned_data.get("date")

        if doctor and date:
            queryset = Consultation.objects.actives().filter(
                doctor=doctor,
                date=date,
            )

            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)

            if queryset.exists():
                raise forms.ValidationError(
                    "Já existe uma consulta com este médico neste horário."
                )

        return cleaned_data


class PatientRegisterForm(forms.ModelForm):
    username = forms.CharField()
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)
    birth_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))

    class Meta:
        model = Patient
        fields = ["nome", "telefone", "birth_date"]

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("As senhas informadas não coincidem.")

        return cleaned_data

    def save(self, commit=True):
        group, _ = Group.objects.get_or_create(name="Patient")
        user = User.objects.create_user(
            username=self.cleaned_data["username"],
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password"],
        )
        user.groups.add(group)

        patient = Patient.objects.create(
            user=user,
            nome=self.cleaned_data["nome"],
            email=self.cleaned_data["email"],
            telefone=self.cleaned_data["telefone"],
            birth_date=self.cleaned_data["birth_date"],
        )

        return patient


class DoctorRegisterForm(forms.ModelForm):
    username = forms.CharField()
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)
    birth_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))

    class Meta:
        model = Doctor
        fields = ["nome", "telefone", "birth_date", "specialty", "crm"]

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("As senhas informadas não coincidem.")

        return cleaned_data

    def save(self, commit=True):
        group, _ = Group.objects.get_or_create(name="Doctor")
        user = User.objects.create_user(
            username=self.cleaned_data["username"],
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password"],
        )
        user.groups.add(group)

        doctor = Doctor.objects.create(
            user=user,
            nome=self.cleaned_data["nome"],
            email=self.cleaned_data["email"],
            telefone=self.cleaned_data["telefone"],
            birth_date=self.cleaned_data["birth_date"],
            specialty=self.cleaned_data["specialty"],
            crm=self.cleaned_data["crm"],
        )

        return doctor
