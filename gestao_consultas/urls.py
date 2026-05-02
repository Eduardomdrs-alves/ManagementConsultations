"""
URL configuration for gestao_consultas project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app .views import *

urlpatterns = [
    path('admin/', admin.site.urls),
        # auth
    path('', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),

    # register
    path('register/patient/', PatientRegisterView.as_view(), name='register_patient'),
    path('register/doctor/', DoctorRegisterView.as_view(), name='register_doctor'),

    # dashboards
    path('dashboard/patient/', PatientDashboardView.as_view(), name='patient_dashboard'),
    path('dashboard/doctor/', DoctorDashboardView.as_view(), name='doctor_dashboard'),

    # consultations
    path('consultations/', ConsultationListView.as_view(), name='consultation_list'),
    path('consultations/create/', ConsultationCreateView.as_view(), name='consultation_create'),
    path('consultations/<int:pk>/edit/', ConsultationUpdateView.as_view(), name='consultation_update'),
    path('consultations/<int:pk>/delete/', ConsultationDeleteView.as_view(), name='consultation_delete'),
]
