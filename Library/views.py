from Library.models import *
from django.shortcuts import render,render_to_response
from django.http import HttpResponse,HttpResponseRedirect
from django.template import RequestContext
from django import forms
from django.contrib import messages
import urllib.parse
import time
import re
import random

#表单
class UserForm(forms.Form):
    username = forms.CharField(label='用户名',max_length=100)
    password = forms.CharField(label='密码',widget=forms.PasswordInput())


#注册
def regist(req):
    if req.method == 'POST':
        uf = UserForm(req.POST)
        if uf.is_valid():
            #获得表单数据
            username = uf.cleaned_data['username']
            password = uf.cleaned_data['password']
            #添加到数据库
            User.objects.create(username= username,password=password)
            return HttpResponseRedirect('/login/')
    else:
        uf = UserForm()
    return render(req, 'regist.html',{'uf':uf})

#登陆
def login(req):
    if req.method == 'POST':
        uf = UserForm(req.POST)
        if uf.is_valid():
            #获取表单用户密码
            username = uf.cleaned_data['username']      #cleaned_data类型是字典，里面是提交成功后的信息
            password = uf.cleaned_data['password']
            #获取的表单数据与数据库进行比较
            user = User.objects.filter(username__exact = username,password__exact = password)
            if user:
                #比较成功，跳转index
                response = HttpResponseRedirect('/../index/')
                #将username写入浏览器cookie,失效时间为3600
                response.set_cookie('username',username,3600)
                return response
            else:
                return render(
                    req, 'login.html', {
                        'uf': uf,
                        'error': 'username or password error!'
                    })
                #比较失败，还在login
                #return HttpResponseRedirect('/onlines/login/')
    else:
        uf = UserForm()
    return render(req, 'login.html',{'uf':uf})

#登陆成功
def index(req):
    username = req.COOKIES.get('username','')

    ctx = {}
    ctx['username'] = username

    return render(req, 'index.html', ctx)

#退出
def logout(req):
    response = HttpResponse('logout !!')
    #清理cookie里保存username
    response.delete_cookie('username')
    return HttpResponseRedirect('/')

# personInfo    个人信息
def personInfo(req):
    username = req.COOKIES.get('username','')
    userObejct = User.objects.get(username=username)
    readerName = userObejct.readerName
    telphone = userObejct.telphone
    email = userObejct.email
    ctx = {}
    ctx['username'] = username
    ctx['readerName'] = readerName
    ctx['telphone'] = telphone
    ctx['email'] = email

    return render(req, 'personInfo.html', ctx)

# bookInfo    图书信息
def bookInfo(req):
    username = req.COOKIES.get('username','')

    ctx = {}
    ctx['username'] = username

    return render(req, 'bookInfo.html', ctx)

# borrowBook    借书
def borrowBook(req):
    username = req.COOKIES.get('username','')

    ctx = {}
    ctx['username'] = username

    return render(req, 'borrowBook.html', ctx)

# returnBook    还书
def returnBook(req):
    username = req.COOKIES.get('username','')

    ctx = {}
    ctx['username'] = username

    return render(req, 'returnBook.html', ctx)




# 搜索
def search(req):
    req.encoding = 'utf-8'

    username = req.COOKIES.get('username', '')
    down_num = User.objects.get(username=username).down_num
    had_down_num = User.objects.get(username=username).had_down_num
    jurisdiction = User.objects.get(username=username).jurisdiction
    if jurisdiction == 'wotu':
        jurisdiction_name = '我图网'
    elif jurisdiction == 'csdn':
        jurisdiction_name = 'CSDN'


    ctx = {'username': username,
           'down_num': down_num,
           'had_down_num': had_down_num,
           'jurisdiction_name': jurisdiction_name
           }
    #cookies = {'Cookie': cookie}
    if 'q' in req.POST:
        if judge_num(down_num, had_down_num):
            message = '你搜索的内容为: ' + req.POST['q']
            url1 = req.POST['q']
            down_url, imgs_url = down(url1, jurisdiction)
            if down_url:
                had_down_num_add(username)
            had_down_num = User.objects.get(username=username).had_down_num
            ctx['had_down_num'] = had_down_num
            ctx['down_url'] = down_url
            ctx['imgs_url'] = imgs_url
            ctx['message'] = message
        else:
            ctx['message'] = '次数用完，请充值'
    else:
        ctx['message'] = '请输入下载内容'
    return render(req, 'search.html', ctx)

def judge_num(down_num, had_down_num):
    if down_num > had_down_num :
        return True
    else:
        return False

# 下载
def down(url1, jurisdiction):
    if jurisdiction == 'wotu':
        cookies = wotuCookies.objects.all() # 获取所有的cookies
        cookie = random.choice(cookies)     # 随机取一个cookie
        down_url = wotu_down(url1, str(cookie))
        imgs_url = get_img(url1, cookie)
        return down_url, imgs_url
    elif jurisdiction == 'csdn':
        vips = csdnVIP.objects.all()         # 获取所有的vip账号
        vip = random.choice(vips)            # 从中选择一个vip账号

        v_user = vip.username
        v_pwd = vip.password
        #print(v_user, v_pwd)
        login_url = "https://passport.csdn.net/account/login"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36",
        }
        # 设置session
        csdn_session = requests.Session()

        # 获取登录页面的源代码内的lt & execution
        login_text = csdn_session.get(url=login_url, headers=headers).text
        lt_execution = re.findall('name="lt" value="(.*?)".*\sname="execution" value="(.*?)"', login_text, re.S)

        # 提交的数据
        data = {"username": v_user,
                "password": v_pwd,
                "lt": lt_execution[0][0],
                "execution": lt_execution[0][1],
                "_eventId": "submit"}

        # 利用session登录csdn
        csdn_session.post(url=login_url, data=data, headers=headers)

        down_id = url1.split('/')[-1]
        down_url = 'http://download.csdn.net/index.php/vip_download/download_client/{}'.format(down_id)
        res = csdn_session.get(down_url)
        #down_url = 'http://dl.download.csdn.net/down11/20180107/3783e8f88939ec23f36d730e6c52b54c.rar?response-content-disposition=attachment%3Bfilename%3D%22%E6%B7%B1%E5%85%A5%E6%B5%85%E5%87%BA%20mybatis%E6%8A%80%E6%9C%AF%E5%8E%9F%E7%90%86%E4%B8%8E%E5%AE%9E%E8%B7%B5.rar%22&OSSAccessKeyId=9q6nvzoJGowBj4q1&Expires=1515405863&Signature=ST%2Be64YvGL%2BOhXgn24SkLmSFb1o%3D&user=wj20180110&sourceid=10192431&sourcescore=8&isvip=1&wj20180110&10192431'
        down_url = res.url
        print(down_url)
        imgs_url = []
        return down_url, imgs_url

# 我图网获取下载链接
def wotu_down(url_1, cookie):
    #cookie = '''user_uutoken=6dc8n%2BHJfNK4SLJz3rFXpIjagwhbI%2BuRbLyeFZuAHeDx%2FeuphT0tax97E1GvhFbDq1hFgYnKV%2FYA8o0ZlScNb1yIMjZXmbVs; returnurl=http%3A%2F%2Fwww.ooopic.com%2Fpic_27057964.html; Hm_lvt_6260fe7b21d72d3521d999c79fe01fc7=1514872102; Hm_lpvt_6260fe7b21d72d3521d999c79fe01fc7=1514889191; Hm_lvt_5b1cb8ea5bd686369a321f1c5e6408b6=1514872102; Hm_lpvt_5b1cb8ea5bd686369a321f1c5e6408b6=1514889191; reg_login_from=vip_top; lastUsername=qq196212736; td_cookie=18446744071472005120; hukelink=100; showqrcode20171123=1; userid=865382; username=qq196212736; nickname=qq196212736; ooo_auth=b6a3I2hw%2BQXuiO63trsZqwNWzwjEiPdNbxJs5wIhxN5PQPjWwrgcythvRSnRc4rep114enFBQ64d53JOF0AcDN9wnG%2B6sXJ8yMkP2H2DaBSvHUuCyZcvPtZFnFFsPMEs1QoOedX4Uo9ndVd2qdP4; ooo_nicaia=c203DYbeEAqVWkmV1ivdmZqdO67fRKjfp%2BwqKxI9ehZvBUs32222XJSnIJDgIVuB1q1kp4WNTyK2gzEwyl6sl%2BIbbBm%2FFnTcM%2Bc3M1aZM%2Blgv4y54OM2mtMFA7eQlbVZl6MH'''
    cookies = {'Cookie': cookie}
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0",
    }
    res_1 = requests.get(url=url_1, headers=headers, cookies=cookies)
    ret_1 = res_1.text
    cmp_1 = r'<a target="_blank" href="(.*)" c'

    # http://downloads.ooopic.com/down_newfreevip.php?id=27233883
    url_2 = re.findall(cmp_1, ret_1)[0]

    res_2 = requests.get(url=url_2, headers=headers, cookies=cookies)
    ret_2 = res_2.text
    token_cmp = r'<input type="hidden" id="token" name="token" value="(.*)">'
    picid_cmp = r'<input type="hidden" id="picid" name="picid" value="(.*)">'
    token = re.findall(token_cmp, ret_2)[0]
    picid = re.findall(picid_cmp, ret_2)[0]

    down_url = 'http://downloads.ooopic.com/down_newfreevip.php?action=down&id={}&token={}'.format(picid, token)
    return down_url

# 我图网获取下载图片
def get_img(url_1, cookie):
    cookies = {'Cookie': cookie}
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0",
    }

    text = requests.get(url=url_1, headers=headers).content.decode('gb2312')
    cmp = r'<img src="(.*)"  width="730'
    imgs_url = re.findall(cmp, text)
    return imgs_url

# 已下载次数+1
def had_down_num_add(username):
    user = User.objects.get(username=username)
    user.had_down_num += 1
    user.save()

