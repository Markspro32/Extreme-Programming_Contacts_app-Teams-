from django.urls import path
from . import views

urlpatterns = [
    path('', views.ContactListView.as_view(), name='contact-list'),
    path('<int:contact_id>/', views.ContactDetailView.as_view(), name='contact-detail'),
]