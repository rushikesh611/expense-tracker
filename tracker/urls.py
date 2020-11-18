from django.contrib import admin
from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('', views.index, name='tracker'),
    path('add-expense',views.add_expense, name='add-expense'),
    path("summary", views.expense_summary, name="expenses-summary"),
    path('edit-expense/<int:id>',views.expense_edit, name='expense-edit'),
    path('delete-expense/<int:id>',views.delete_expense, name='expense-delete'),
    path('search-expenses/',csrf_exempt(views.search_expenses), name='search_expenses'),

    path("export_csv", views.export_csv, name="export-csv"),
    path("export_pdf",views.export_pdf, name="export-pdf"),

    path('expenses/summary_rest', views.expense_summary_rest,
         name='expenses_summary_rest'),
         
    path('expenses/three_months_summary', views.last_3months_stats,
         name='three_months_summary'),

    path('expenses/last_3months_expense_source_stats',
         views.last_3months_expense_source_stats, name="last_3months_expense_source_stats"),

]