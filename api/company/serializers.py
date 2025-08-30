from rest_framework import serializers

from company.models import CompanyInfo


class CompanyInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyInfo
        fields = ['id', 'name', 'address', 'phone', 'email', 'website', 'logo']
