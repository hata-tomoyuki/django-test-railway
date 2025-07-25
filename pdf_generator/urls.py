from django.urls import path

from . import views

app_name = 'pdf_generator'

urlpatterns = [
    path('', views.pdf_generator_page, name='pdf_generator_page'),
    path('generate-from-url/', views.generate_pdf_from_url, name='generate_pdf_from_url'),
    path('generate-from-html/', views.generate_pdf_from_html, name='generate_pdf_from_html'),
    path('check-wkhtmltopdf/', views.check_wkhtmltopdf, name='check_wkhtmltopdf'),
]
