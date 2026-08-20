from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

from apps.vendors.views import StorefrontDetailView
from apps.core import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('profile/', include('apps.accounts.urls')),
    path('vendors/', include('apps.vendors.urls')),
    path('products/', include('apps.products.urls')),
    path('cart/', include('apps.cart.urls')),
    path('orders/', include('apps.orders.urls')),
    path('payment/', include('apps.payments.urls')),
    path('reviews/', include('apps.reviews.urls')),
    path('store/<slug:slug>/', StorefrontDetailView.as_view(), name='storefront_detail'),
    path('', core_views.HomeView.as_view(), name='home'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom error handlers (Task 41)
handler404 = "apps.core.views.custom_404"
handler500 = "apps.core.views.custom_500"
