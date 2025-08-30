from rest_framework import generics

from company.models import CompanyInfo

from .serializers import CompanyInfoSerializer
from rest_framework.parsers import MultiPartParser, FormParser

# List + Create
class CompanyListCreateView(generics.ListCreateAPIView):
    queryset = CompanyInfo.objects.all()
    serializer_class = CompanyInfoSerializer
    parser_classes = [MultiPartParser, FormParser]  # required for file upload

# Retrieve + Update + Delete
class CompanyDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CompanyInfo.objects.all()
    serializer_class = CompanyInfoSerializer
    parser_classes = [MultiPartParser, FormParser]  # required for file upload
