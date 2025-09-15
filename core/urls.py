
from django.conf import settings
from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.urls import path

from api.mejlis.views import CreateOrderView
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('api/', include('users.urls')),
    path('api/', include('company.urls')),
    #path('api/mejlis-material/create', CreateOrderView.as_view(), name='create-order'),
    path('api/', include('materials.urls')),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
