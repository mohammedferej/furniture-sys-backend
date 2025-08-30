from django.contrib import admin



from company.models import CompanyInfo
@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "email", "website","logo")
