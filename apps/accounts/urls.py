from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("addresses/", views.AddressListView.as_view(), name="addresses"),
    path("addresses/add/", views.AddressCreateView.as_view(), name="address_add"),
    path("addresses/<uuid:public_id>/edit/", views.AddressEditView.as_view(), name="address_edit"),
    path("addresses/<uuid:public_id>/delete/", views.AddressDeleteView.as_view(), name="address_delete"),
    path("addresses/<uuid:public_id>/set-default/", views.AddressSetDefaultView.as_view(), name="address_set_default"),
]
