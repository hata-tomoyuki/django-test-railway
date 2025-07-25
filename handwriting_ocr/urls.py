from django.urls import path

from . import views

app_name = 'handwriting_ocr'

urlpatterns = [
    path('', views.handwriting_page, name='handwriting_page'),
    path('recognize/', views.recognize_handwriting, name='recognize_handwriting'),
]
