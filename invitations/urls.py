from django.urls import path, include
from rest_framework.routers import DefaultRouter
from  .views import GuestViewSet, ScanLogViewSet,TableViewSet
from invitations import views

router = DefaultRouter()
router.register(r'guests',GuestViewSet)
router.register(r'scanlogs', ScanLogViewSet)
router.register(r'tables', TableViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # path('download_qr/<int:guest_id>/', views.telecharger_qr_code, name='download_qr'),
    # path('generate_invitation/<int:guest_id>/', views.generer_carte_invitation, name='generate_invitation'),
]