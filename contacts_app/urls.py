from django.urls import path
from . import views

urlpatterns = [
    path('', views.ContactListView.as_view(), name='contact-list'),
    path('<int:contact_id>/', views.ContactDetailView.as_view(), name='contact-detail'),
    path('<int:contact_id>/bookmark/', views.ContactBookmarkView.as_view(), name='contact-bookmark'),
    path('<int:contact_id>/methods/', views.ContactMethodListView.as_view(), name='contact-method-list'),
    path('<int:contact_id>/methods/<int:method_id>/', views.ContactMethodDetailView.as_view(), name='contact-method-detail'),
]