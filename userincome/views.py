from django.shortcuts import render, redirect
from .models import Source, UserIncome
from django.core.paginator import Paginator
from userpreferences.models import UserPreferences
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import json
import datetime
import calendar
import os
from django.http import JsonResponse, HttpResponse
import csv

import tempfile
from django.db.models import Sum
from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa
# Create your views here.

@login_required(login_url='/authentication/login')
def search_income(request):
    if request.method == 'POST':
        search_str=json.loads(request.body).get('searchText')
        income=UserIncome.objects.filter(
            amount__istartswith=search_str,owner=request.user) | UserIncome.objects.filter(
            date__istartswith=search_str,owner=request.user) | UserIncome.objects.filter(
            description__icontains=search_str,owner=request.user) | UserIncome.objects.filter(
            source__icontains=search_str,owner=request.user)       
        data=income.values()
        return JsonResponse(list(data),safe=False)


@login_required(login_url='/authentication/login')
def index(request):
    categories = Source.objects.all()
    income=UserIncome.objects.filter(owner=request.user)
    paginator=Paginator(income,5)
    page_number=request.GET.get('page')
    page_obj=paginator.get_page(page_number)
    currency = UserPreferences.objects.get(user=request.user).currency
    context={
        'income':income,
        'page_obj':page_obj,
        'currency':currency
    }
    return render(request,'income/index.html',context)

@login_required(login_url='/authentication/login')
def add_income(request):
    sources = Source.objects.all()
    context={
            'sources':sources,
            'values':request.POST
    }
    if request.method=='GET':
        return render(request,'income/add_income.html',context)

    if request.method=='POST':

        amount=request.POST['amount']
        if not amount:
            messages.error(request,'Amount is required')
            return render(request,'income/add_income.html',context)

        description=request.POST['description']
        date=request.POST['income_date']
        source=request.POST['source']

        if not description:
            messages.error(request,'Description is required')
            return render(request,'income/add_income.html',context)
        
        UserIncome.objects.create(owner=request.user,amount=amount,date=date,source=source,description=description)
        messages.success(request,'Record saved successfully')
        return redirect('income')

@login_required(login_url='/authentication/login')
def income_edit(request,id):
    income=UserIncome.objects.get(pk=id)
    sources = Source.objects.all()
    context={
            'income':income,
            'values':income,
            'sources':sources
        }
    if request.method=='GET':
        return render(request,'income/edit-income.html',context)

    if request.method=='POST':
        amount=request.POST['amount']
        if not amount:
            messages.error(request,'Amount is required')
            return render(request,'income/edit-income.html',context)

        description=request.POST['description']
        date=request.POST['income_date']
        source=request.POST['source']

        if not description:
            messages.error(request,'Description is required')
            return render(request,'income/edit-income.html',context)

        income.owner=request.user
        income.amount=amount
        income.date=date
        income.sources=sources
        income.description=description
        income.save()
        messages.success(request,'Record Updated Successfully')
        return redirect('income')
        
@login_required(login_url='/authentication/login')
def delete_income(request,id):
    income=UserIncome.objects.get(pk=id)
    income.delete()
    messages.success(request,'Record Deleted')
    return redirect('income')

@login_required(login_url='/authentication/login')
def income_summary(request):

    if not UserPreferences.objects.filter(user=request.user).exists():
        messages.info(request, 'Please choose your preferred currency')
        return redirect('preferences/index.html')
    all_income = UserIncome.objects.all()
    today = datetime.datetime.today().date()
    today2 = datetime.date.today()
    week_ago = today - datetime.timedelta(days=7)
    month_ago = today - datetime.timedelta(days=30)
    year_ago = today - datetime.timedelta(days=366)
    todays_amount = 0
    todays_count = 0
    this_week_amount = 0
    this_week_count = 0
    this_month_amount = 0
    this_month_count = 0
    this_year_amount = 0
    this_year_count = 0

    for one in all_income:
        if one.date == today:
            todays_amount += one.amount
            todays_count += 1

        if one.date >= week_ago:
            this_week_amount += one.amount
            this_week_count += 1

        if one.date >= month_ago:
            this_month_amount += one.amount
            this_month_count += 1

        if one.date >= year_ago:
            this_year_amount += one.amount
            this_year_count += 1

    context = {
        'currency': UserPreferences.objects.get(user=request.user).currency.split('-')[0],
        'today': {
            'amount': todays_amount,
            "count": todays_count,

        },
        'this_week': {
            'amount': this_week_amount,
            "count": this_week_count,

        },
        'this_month': {
            'amount': this_month_amount,
            "count": this_month_count,

        },
        'this_year': {
            'amount': this_year_amount,
            "count": this_year_count,

        },

    }
    return render(request, 'income/summary.html', context)


def income_summary_rest(request):
    all_income = UserIncome.objects.filter(owner=request.user)
    today = datetime.datetime.today().date()
    today_amount = 0
    months_data = {}
    week_days_data = {}

    def get_amount_for_month(month):
        month_amount = 0
        for one in all_income:
            month_, year = one.date.month, one.date.year
            if month == month_ and year == today_year:
                month_amount += one.amount
        return month_amount

    for x in range(1, 13):
        today_month, today_year = x, datetime.datetime.today().year
        for one in all_income:
            months_data[x] = get_amount_for_month(x)

    def get_amount_for_day(x, today_day, month, today_year):
        day_amount = 0
        for one in all_income:
            day_, date_,  month_, year_ = one.date.isoweekday(
            ), one.date.day, one.date.month, one.date.year
            if x == day_ and month == month_ and year_ == today_year:
                if not day_ > today_day:
                    day_amount += one.amount
        return day_amount

    for x in range(1, 8):
        today_day, today_month, today_year = datetime.datetime.today(
        ).isoweekday(), datetime.datetime.today(
        ).month, datetime.datetime.today().year
        for one in all_income:
            week_days_data[x] = get_amount_for_day(
                x, today_day, today_month, today_year)

    data = {"months": months_data, "days": week_days_data}
    return JsonResponse({'data': data}, safe=False)


@login_required(login_url='/authentication/login')
def income_detail(request):
    income = UserIncome.objects.all_income()
    context = {
        'income': income
    }
    return render('income/index.html', context)


@login_required(login_url='/authentication/login')
def income_delete(request, id):
    UserIncome.objects.get(id=id).delete()
    messages.success(request, 'Income  Deleted')
    return redirect('income')


def last_3months_income_stats(request):
    todays_date = datetime.date.today()
    three_months_ago = datetime.date.today() - datetime.timedelta(days=90)
    income = UserIncome.objects.filter(owner=request.user,
                                   date__gte=three_months_ago, date__lte=todays_date)
    # sources occuring.

    def get_sources(item):
        return item.source
    final = {}
    sources = list(set(map(get_sources, income)))

    def get_sources_count(y):
        new = UserIncome.objects.filter(source=y)
        count = new.count()
        amount = 0
        for y in new:
            amount += y.amount
        return {'count': count, 'amount': amount}

    for x in income:
        for y in sources:
            final[y] = get_sources_count(y)
    return JsonResponse({'sources_data': final}, safe=False)


# here income_date
def last_3months_income_source_stats(request):
    todays_date = datetime.date.today()
    last_month = datetime.date.today() - datetime.timedelta(days=0)
    last_2_month = last_month - datetime.timedelta(days=30)
    last_3_month = last_2_month - datetime.timedelta(days=30)

    last_month_income = UserIncome.objects.filter(owner=request.user,
                                              date__gte=last_month, date__lte=todays_date).order_by('date')
    prev_month_income = UserIncome.objects.filter(owner=request.user,
                                              date__gte=last_month, date__lte=last_2_month)
    prev_prev_month_income = UserIncome.objects.filter(owner=request.user,
                                                   date__gte=last_2_month, date__lte=last_3_month)

    keyed_data = []
    this_month_data = {'7th': 0, '15th': 0, '22nd': 0, '29th': 0}
    prev_month_data = {'7th': 0, '15th': 0, '22nd': 0, '29th': 0}
    prev_prev_month_data = {'7th': 0, '15th': 0, '22nd': 0, '29th': 0}

    for x in last_month_income:
        month = str(x.date)[:7]
        date_in_month = str(x.date)[:2]
        if int(date_in_month) <= 7:
            this_month_data['7th'] += x.amount
        if int(date_in_month) > 7 and int(date_in_month) <= 15:
            this_month_data['15th'] += x.amount
        if int(date_in_month) >= 16 and int(date_in_month) <= 21:
            this_month_data['22nd'] += x.amount
        if int(date_in_month) > 22 and int(date_in_month) < 31:
            this_month_data['29th'] += x.amount

    keyed_data.append({str(last_month): this_month_data})

    for x in prev_month_income:
        date_in_month = str(x.date)[:2]
        month = str(x.date)[:7]
        if int(date_in_month) <= 7:
            prev_month_data['7th'] += x.amount
        if int(date_in_month) > 7 and int(date_in_month) <= 15:
            prev_month_data['15th'] += x.amount
        if int(date_in_month) >= 16 and int(date_in_month) <= 21:
            prev_month_data['22nd'] += x.amount
        if int(date_in_month) > 22 and int(date_in_month) < 31:
            prev_month_data['29th'] += x.amount

    keyed_data.append({str(last_2_month): prev_month_data})

    for x in prev_prev_month_income:
        date_in_month = str(x.date)[:2]
        month = str(x.date)[:7]
        if int(date_in_month) <= 7:
            prev_prev_month_data['7th'] += x.amount
        if int(date_in_month) > 7 and int(date_in_month) <= 15:
            prev_prev_month_data['15th'] += x.amount
        if int(date_in_month) >= 16 and int(date_in_month) <= 21:
            prev_prev_month_data['22nd'] += x.amount
        if int(date_in_month) > 22 and int(date_in_month) < 31:
            prev_prev_month_data['29th'] += x.amount

    keyed_data.append({str(last_3_month): prev_month_data})
    return JsonResponse({'cumulative_income_data': keyed_data}, safe=False)



def export_csv(request):
    response=HttpResponse(content_type='text/csv')
    response['Content-Disposition']='attachment; filename=Income'+ \
        str(datetime.datetime.now())+'.csv'
    
    writer=csv.writer(response)
    writer.writerow(['Amount','Description','Source','Date'])

    income=UserIncome.objects.filter(owner=request.user)

    for inc in income:
        writer.writerow([inc.amount,inc.description,inc.source,inc.date])
    
    return response

def render_to_pdf(template_src, context_dict={}):
	template = get_template(template_src)
	html  = template.render(context_dict)
	result = BytesIO()
    
	pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)

	if not pdf.err:
		return HttpResponse(result.getvalue(), content_type='application/pdf')
	return None

# from collections import ChainMap
# class export_pdf(View):
def export_pdf(request, *args, **kwargs):
    income=UserIncome.objects.filter(owner=request.user).values()[0]
    # data={
    # }
    # for e in expenses:
    #     data.update(e)
    # import pdb
    # pdb.set_trace()
  
    pdf = render_to_pdf('tracker/pdf-output.html',dict(income))
    
    return HttpResponse(pdf, content_type='application/pdf')
