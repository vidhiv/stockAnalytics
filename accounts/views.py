
import hashlib

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.http import JsonResponse
from django.core import serializers

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

def getStockLivePrice(stockCode):
    status = 'failure'
    stockprice = 0.0
    price = raw_stock_data.objects.filter(stock_ticker = stockCode).order_by('-stock_time')[:1]
    if len(price) > 0:
        status = 'success'
        stockprice = price[0].close_price

    return {'status': status, 'stockprice': stockprice}

def fetchPortfolio(userID):
    openposition = []
    trading = []
    tilldateprofit = 0
    buyingData =  portfolio.objects.filter(user_id = userID, buy_sell = 'buy').order_by('stock', 'trade_date')
    sellingData =  portfolio.objects.filter(user_id = userID, buy_sell = 'sell').order_by('stock', 'trade_date')
    # print(len(buyingData))
    # print(len(sellingData))
    if len(buyingData) > 0 and len(sellingData) > 0:
        b = 0
        s = 0 
        while s < len(sellingData):
            bd = buyingData[b]
            sd = sellingData[s]
            if sd.stock == bd.stock:
                sellqty = 0
                sellprice = 0
                stockname = sd.stock
                buyqty = 0
                buyprice = 0
                while s < len(sellingData):
                    sd = sellingData[s]
                    if sd.stock == stockname:
                        sellqty += sd.qty
                        sellprice += (sd.price * sd.qty)
                        s += 1
                    else:
                        break
                    
                while b < len(buyingData):
                    bd = buyingData[b]
                    if bd.stock == stockname:
                        buyqty += bd.qty
                        buyprice += (bd.price * bd.qty)
                        b += 1
                    else:
                        break
                
                perbuyprice = buyprice/buyqty
                pnl = sellprice - (sellqty * perbuyprice)
                tilldateprofit += pnl
                trading.append({'stock': stockname, 'pnl': pnl, 'buyPrice': (sellqty * perbuyprice), 'sellPrice': sellprice, 'qty': sellqty})
                if buyqty > sellqty:
                    openposition.append({'buy_sell': 'buy', 'stock': stockname,'qty': (buyqty - sellqty), 'price' : perbuyprice, 'trade_date' : bd.trade_date })
            else:
                openposition.append(bd)
                b += 1

        while b < len(buyingData):
            bd = buyingData[b]
            openposition.append(bd)
            b += 1
    else:
        if len(buyingData) > 0:
            openposition = buyingData

    myportfolio = {
        'openposition' : openposition,
        'pnl': trading,
        'tilldateprofit': tilldateprofit
    }
    return myportfolio

def checkIfOverSEll(data):
    overSell = True
    totalbuy = portfolio.objects.raw("SELECT sum(qty) as id FROM accounts_portfolio where user_id = %s and stock = %s and buy_sell = 'buy'",[data['user_id'], data['stock']])[0]
    totalsell = portfolio.objects.raw("SELECT sum(qty) as id FROM accounts_portfolio where user_id = %s and stock = %s and buy_sell = 'sell'",[data['user_id'], data['stock']])[0]
    totalbuy = totalbuy.__dict__['id']
    totalsell = totalsell.__dict__['id']
    if totalbuy == None:
        totalbuy = 0
    if totalsell == None:
        totalsell = 0
    allowed = totalbuy - totalsell
    # print("allowed")
    # print(allowed)
    if int(data['qty']) <= allowed:
        overSell = False
    return overSell

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
        portfolio = fetchPortfolio(request.session['data']['user_id'])
        # print(portfolio['pnl'])
        return render(request, 'stockData.html', {'status': 'success','message': 'Data fetched','data': portfolio})
    else:
        return HttpResponseRedirect("/logIn")

def dailyTips(request):
    if checkUserloggedIn(request) == 1:
        today = str(timezone.now().date())
        tipid = request.session['data']['tip_id']
        tipinfo = {}
        print("in dailytip")
        print(len(tipinfo))
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
        # print(len(tipinfo))
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

def getStockList(request):
    if checkUserloggedIn(request) == 1:
        text = "%" + request.GET.get('keyword') + "%"
        # stocks = stockList.objects.filter(name__icontains=text).order_by('name').values()
        stocks = stockList.objects.raw("SELECT * FROM accounts_stocklist where  name LIKE %s OR code like %s order by name",[text, text])
        print(len(stocks))
        if len(stocks) > 0:
            return JsonResponse({"data" : serializers.serialize('json', stocks), "status": "success"}, status=200)
        else:
            return JsonResponse({"message": "No data found", "status": "failure"}, status=200)
    else:
        return JsonResponse({"message": "You have been logged out. Please log in to continue", "status": "failure"}, status=200)
    
def companyInfo(request, companyId):
    if checkUserloggedIn(request) == 1:
        data = {}
        status = 'success'
        message = ''
        companyInfo = stockList.objects.filter(id=companyId).values()
        recentPriceUpdates = {}
        if len(companyInfo) == 1:
            data = list(companyInfo)
            recentPriceUpdates = raw_stock_data.objects.filter(stock_ticker = data[0]['code']).order_by('-stock_time')[:10]
            message = 'company info avaialable'
        else:
            status = 'failure'
            message = 'Information Unavailable'
        return render(request, 'companyInfo.html',{'status': status ,'message': message,'data': data, 'recentPriceUpdates' : recentPriceUpdates})
    else:
        return HttpResponseRedirect("/logIn")

def buyStock(request):
    if checkUserloggedIn(request) == 1:
        stock = request.GET.get('code')
        price = getStockLivePrice(stock)
        if(price['status'] == 'success'):
            insertinfo = portfolio.objects.create(user_id = request.session['data']['user_id'], stock = stock, qty = request.GET.get('quantity'), price = price['stockprice'], buy_sell = 'buy', trade_date = timezone.now())
            if insertinfo.__dict__['id']:
                return JsonResponse({"message": "Transaction successful (bought @ $"+ str(price['stockprice'])  + ")", "status": "success"}, status=200)
            else:
                return JsonResponse({"message": "Transaction incomplete", "status": "failure"}, status=200)
        else:
            return JsonResponse({"message": "Stock price not available. Transaction incomplete", "status": "failure"}, status=200)
    else:
        return JsonResponse({"message": "You have been logged out. Please log in to continue", "status": "failure"}, status=200)

def sellStock(request):
    if checkUserloggedIn(request) == 1:
        update = {}
        update['qty'] = request.GET.get('quantity')
        update['stock'] = request.GET.get('code')
        update['user_id'] = request.session['data']['user_id']
        update['price'] = getStockLivePrice(update['stock'])
        if(update['price']['status'] == 'success'):
            rstatus = checkIfOverSEll(update)
            # print(rstatus)
            if rstatus == True:
                return JsonResponse({"message": "Cannot sell more than you have bought", "status": "failure"}, status=200)
            else:
                updateinfo = portfolio.objects.create(user_id = update['user_id'], stock = update['stock'], qty = update['qty'], price = update['price']['stockprice'], buy_sell = 'sell', trade_date = timezone.now())
                if updateinfo.__dict__['id']:
                    return JsonResponse({"message": "Transaction successful (sold @ $"+ str(update['price']['stockprice'])  + ")", "status": "success"}, status=200)
                else:
                    return JsonResponse({"message": "Transaction incomplete", "status": "failure"}, status=200)
        else:
            return JsonResponse({"message": "Stock price not available. Transaction incomplete", "status": "failure"}, status=200)
    else:
        return JsonResponse({"message": "You have been logged out. Please log in to continue", "status": "failure"}, status=200)

def viewAllTrades(request):
    if checkUserloggedIn(request) == 1:
        data = {}
        status = 'success'
        message = ''
        uid = request.session['data']['user_id']
        print(uid)
        tradedata = portfolio.objects.filter(user_id=uid).order_by('id').values()
        if len(tradedata) > 0:
            data = list(tradedata)
            message = 'trade info avaialable'
        else:
            status = 'failure'
            message = 'You may have not performed any buy/sell transaction till now'
        return render(request, 'viewAllTrades.html',{'status': status ,'message': message,'data': data})
    else:
        return HttpResponseRedirect("/logIn")

def viewCorrelationGraph(request):
    if checkUserloggedIn(request) == 1:
        data = {}
        status = 'success'
        message = ''
        return render(request, 'viewCorrelationGraph.html',{'status': status ,'message': message,'data': data})
    else:
        return HttpResponseRedirect("/logIn")
