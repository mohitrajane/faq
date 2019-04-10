import urllib
import json

from django.shortcuts import render,redirect
from django.template import loader,RequestContext
from django.http import HttpResponse,HttpResponseRedirect
from django.utils import timezone
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import patch_cache_control,never_cache

from .models import HOD,Question

# Create your views here.
def index(request):
    return render(request,'index.html')

def on_submit(request):
    choice=request.POST.get('choice',"")
    query=request.POST.get('query-textarea',"")
    mail=request.POST.get('mail_id',"")
    if(choice == 'cse'):
        branch =1
    elif(choice =='ce'):
        branch = 2
    elif(choice=='public'):
        branch = 3
    elif(choice=='eee'):
        branch = 4
    elif(choice=='ec'):
        branch = 5
    elif(choice=='eie'):
        branch = 6
    else:
        branch= 7
    # Starting reCaptcha Validation 
    recaptcha_response=request.POST.get('g-recaptcha-response',"")
    print("recaptcha response:{}".format(recaptcha_response))
    url='https://www.google.com/recaptcha/api/siteverify'
    values={
        'secret':settings.GOOGLE_RECAPTCHA_SECRET_KEY,
        'response':recaptcha_response
    }
    data=urllib.parse.urlencode(values).encode()
    req=urllib.request.Request(url,data=data)
    response=urllib.request.urlopen(req)
    result=json.loads(response.read().decode())
    print("result:{}".format(result))
    # # FInished Validation
    if result['success']:
        hod_object = HOD.objects.get(pk=branch)
        print("branch:{},query:{},time:{},mail{}".format(hod_object.name,query,timezone.now(),mail))
        ques = Question(branch_id=hod_object,query=query,query_date=timezone.now(),mail_id=mail)
        ques.save()
        return render(request,'index.html',{'status':"success"})
    else:
        messages.error(request,'Invalid reCATPCHA,Please try again')
        return render(request,'index.html',{'status':"failed"})
@never_cache
def hod_view(request,hod_id):
    hod_obj=HOD.objects.get(branch_id=hod_id)
    query_hod=Question.objects.filter(branch_id=hod_obj)
    print('hod name:{}'.format(hod_obj.name))
    return render(request,'hod.html',{"queries":query_hod,"hod":hod_obj})
@never_cache
def login_success(request):
    b_id=HOD.objects.get(name=request.user).branch_id
    return HttpResponseRedirect('/hod/{}'.format(b_id))
@never_cache
def logout_view(request):
    logout(request)
    return render(request,'registration/logout.html',context={})
@login_required
def del_item(request,hod_id,q_id):
    del_ele=Question.objects.get(pk=q_id)
    del_ele.delete()
    return HttpResponseRedirect('/hod/{}'.format(hod_id))
@login_required
def send_query_response(request):
    hod_id = request.POST.get("hod_id","")
    mail = request.POST.get("email","")
    subject = request.POST.get("subject")
    body = request.POST.get("body")
    print("id:{},mail:{},sub:{},body:{}".format(hod_id,mail,subject,body))
    val=send_mail(subject,body,'leomv3@gmail.com',[mail])
    print("mail send :),val{}".format(val))
    return HttpResponseRedirect('/hod/{}'.format(hod_id))
@login_required
def forward_view(request,q_id,forward_to,forward_f):
    print('\nq_id:{} forward_to:{} forward_f:{}'.format(q_id,forward_to,forward_f))
    Question.objects.filter(pk=q_id).update(branch_id=HOD.objects.get(branch_id=forward_to))
    return HttpResponseRedirect('/hod/{}'.format(forward_f))