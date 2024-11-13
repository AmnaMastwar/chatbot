from django.urls import path
from . import views


urlpatterns =  [
    path('',views.chatbot,name='chatbot'),
    path('qs', views.import_faq_data, name='questions'),
    path('api/menu-options/', views.get_menu_options, name='menu-options'),
    path('api/process-input/', views.process_input, name='process-input'),  
    path('api/process-subcategory-input/', views.process_subcategory_input, name='process-subcategory-input'),
]
