
import hashlib

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.utils import timezone

from .forms import *
from .models import *

# Create your views here.
def checkUserloggedIn(request):
    status = 0
    if request.session.has_key('data'):
        status = 1
    return status

def fetchTipData(tipid):
    # tipdata = serializers.serialize("json", tipData.objects.filter(id__lte = tipid).order_by('-id'))
    tipdata =  tipData.objects.filter(id__lte = tipid).order_by('-id')
    return tipdata

def registerUser(request):
    status = ''
    message = ''
    form= UserData(request.POST or None)
    if form.is_valid():
            userData = form.save(commit=False)
            useremail = userInfo.objects.filter(email= userData.email)
            if useremail:
                status = 'failure'
                message ='Email Id already registered'
            else:
                userData.password = hashlib.md5(form.cleaned_data['password'].encode("utf-8")).hexdigest()
                userData.date_created = timezone.now()
                userData.save()
                status = 'success'
                message ='Registration successful. Log in to access more features'
                form = {}

    return render(request, 'registration.html', {'status': status,'message': message, 'data': form})

def loginUser(request):
    status = ''
    message = ''
    form= LoginUser(request.POST or None)
    if checkUserloggedIn(request) == 1:
        return HttpResponseRedirect("/myProfile")
    else:
        if form.is_valid():
            useremail = userInfo.objects.filter(email=form.cleaned_data['email'])
            if len(useremail) == 0:
                status = 'failure'
                message = 'Email id not registered'
            else:
                session = {}
                for e in useremail:
                    session['user_id'] = e.id
                    session['fullname'] = e.fullname
                    session['contact'] = e.contact
                    session['email'] = e.email
                    session['password'] = e.password
                    session['tip_id'] = e.tip_id
                    session['tip_date'] = str(e.tip_date)
                password = hashlib.md5(form.cleaned_data['password'].encode("utf-8")).hexdigest()
                if password == session['password']:
                    session['password'] = ''
                    request.session['data'] = session
                    request.session.modified = True
                    return HttpResponseRedirect("/myProfile")
                else:
                    status = 'failure'
                    message = 'Incorrect Password'
    return render(request, 'login.html', {'status': status,'message': message})

def myProfile(request):
    if checkUserloggedIn(request) == 1:
        status = 'success'
        message = 'User Logged In'
        data = request.session['data']
        return render(request, 'myProfile.html', {'status': status,'message': message,'data': data})
    else:
        return HttpResponseRedirect("/logIn")

def stockData(request):
    if checkUserloggedIn(request) == 1:
        return render(request, 'stockData.html')
    else:
        return HttpResponseRedirect("/logIn")

def dailyTips(request):
    if checkUserloggedIn(request) == 1:
        today = str(timezone.now().date())
        tipid = request.session['data']['tip_id']
        tipinfo = {}
        print("in dailytip")
        print("pre:")
        print(request.session['data'])
        if request.session['data']['tip_date'] == today:
            tipinfo = fetchTipData(tipid)
        else:
            tipid = tipid + 1
            tipinfo = fetchTipData(tipid)
            request.session['data']['tip_id'] = tipid
            request.session['data']['tip_date'] = today
            request.session.modified = True
            userinfo = userInfo.objects.get(id=request.session['data']['user_id'])
            userinfo.tip_id = tipid
            userinfo.tip_date = today
            userinfo.save()
        data = {}
        if len(tipinfo) > 0:
            for e in tipinfo:
                if e.id == tipid:
                    data['tipInfo'] = e
                    break
            data['tipData'] = tipinfo
        
        print("post:")
        print(request.session['data'])
        return render(request, 'dailyTips.html',{'status': 'success','message': '','data': data})
    else:
        return HttpResponseRedirect("/logIn")

def logOut(request):
    try:
        del request.session['data']
        request.session.modified = True
    except:
      pass
    return HttpResponseRedirect("/logIn")

def underConstruction(request):
    return render(request, 'underConstruction.html')