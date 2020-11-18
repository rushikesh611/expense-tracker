from django.contrib import admin
from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('', views.index, name='income'),
    path('add-income',views.add_income, name='add-income'),
    path('edit-income/<int:id>',views.income_edit, name='income-edit'),
    path('delete-income/<int:id>',views.delete_income, name='income-delete'),
    path('search-income/',csrf_exempt(views.search_income), name='search_income'),
    path("income-summary", views.income_summary, name="income-summary"),

     path("export_csv", views.export_csv, name="export-income-csv"),
     path("export_pdf",views.export_pdf, name="export-income-pdf"),

        path('summary_rest', views.income_summary_rest,
         name='income_summary_rest'),
    path('three_months_summary', views.last_3months_income_stats,
         name='three_months_summary_'),
    path('last_3months_income_source_stats', views.last_3months_income_source_stats,
         name='last_3months_income_source_stats_'),

]