# testseries/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Teacher Routes
    path('dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('category/create/', views.create_category, name='create_category'),
    path('test/create/', views.create_test, name='create_test'),
    path('test/<int:test_id>/questions/', views.manage_questions, name='manage_questions'),

    # Student Routes
    path('student/tests/', views.student_test_list, name='student_test_list'),
    path('test/<int:test_id>/attempt/', views.take_test, name='take_test'),
    path('result/<int:result_id>/', views.test_result, name='test_result'),
    path('result/<int:result_id>/pdf/', views.download_result_pdf, name='download_result_pdf'),
    
]