from django.urls import path

from api.company.views import CompanyDetailView, CompanyListCreateView


urlpatterns = [
    path('company/', CompanyListCreateView.as_view(), name='company-list-create'),
    path('company/<int:pk>/', CompanyDetailView.as_view(), name='company-detail'),
]
