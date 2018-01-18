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
            borrowNum = 10
            borrowedNum = 0
            #添加到数据库
            User.objects.create(username= username,password=password, borrowNum=borrowNum, borrowedNum=borrowedNum)
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
    book_obejct = Book.objects.all()
    ctx = {}
    ctx['username'] = username
    ctx['book_obejct'] = book_obejct

    return render(req, 'index.html', ctx)

#退出
def logout(req):
    response = HttpResponse('logout !!')
    #清理cookie里保存username
    response.delete_cookie('username')
    return HttpResponseRedirect('/')

# personInfo    个人信息
def personInfo(req):
    username = req.COOKIES.get('username', '')
    ctx = {}
    if req.method == 'POST':
        readerName = req.POST['readerName']
        telphone = req.POST['telphone']
        email = req.POST['email']
        User.objects.filter(username=username).update(readerName=readerName, telphone=telphone, email=email)
        HttpResponseRedirect('/../personInfo')
    else:
        userObejct = User.objects.get(username=username)
        readerId = userObejct.id
        readerName = userObejct.readerName
        borrowedNum = userObejct.borrowedNum
        telphone = userObejct.telphone
        email = userObejct.email
        ctx['readerId'] = readerId
        ctx['username'] = username
        ctx['readerName'] = readerName
        ctx['borrowedNum'] = borrowedNum
        ctx['telphone'] = telphone
        ctx['email'] = email

    return render(req, 'personInfo.html', ctx)

# borrowBook    借书
def borrowBook(req):
    username = req.COOKIES.get('username','')
    ctx = {}
    ctx['username'] = username

    # borrowBook提交表单
    if req.method == 'POST':
        try:
            req_dict = req.POST     # req_dict是页面提交的参数
            button_value = req_dict['button']           # 1是搜索框，2是索书，3是还书，4是缺书
            print('button_value : {}'.format(button_value))
            # 搜索框
            if button_value == '1':
                searchBookName = req.POST['searchBookName']
                try:
                    search_object = Book.objects.get(bookName=searchBookName)
                    ctx['search_object'] = search_object
                except Exception as e:
                    ctx['error'] = '未查到书籍'

            # 索书
            elif button_value == '2':
                readerId = req_dict['readerId']
                bookId = req_dict['bookId']
                reader_object = User.objects.get(id=readerId)       # 通过readerId获取外键User对象
                book_object = Book.objects.get(bookId=bookId)

                # 对借书表进行修改
                borrowbook = BorrowBook(borrowUser=reader_object, borrowBookId=book_object)
                borrowbook.save()       # 创建一条记录

                # 对读者表进行修改
                reader_object.borrowedNum += 1  # 读者借书+1
                reader_object.save()            # 保存

                # 对book表进行修改
                book_object.bookSurplus -= 1        # 剩余书籍-1
                book_object.isBorrow -= 1           # 可借-1
                book_object.save()

            # 预订书籍
            elif button_value == '3':
                readerId = req_dict['readerId']
                bookName = req_dict['bookName']

                reader_object = User.objects.get(id=readerId)  # 通过readerId获取外键User对象

                # 对预订书表进行修改
                borrowbook = subscribeBook(subscribeUser=reader_object, subscribeBookName=bookName)
                borrowbook.save()  # 创建一条记录

            # 缺书登记
            elif button_value == '4':
                readerId = req_dict['readerId']
                bookName = req_dict['bookName']

                reader_object = User.objects.get(id=readerId)  # 通过readerId获取外键User对象

                # 对预订书表进行修改
                borrowbook = LackBook(LackUser=reader_object, LackBook=bookName)
                borrowbook.save()  # 创建一条记录



        except Exception as e:
            print(e)

    else:
        pass


    return render(req, 'borrowBook.html', ctx)

# returnBook    还书
def returnBook(req):
    username = req.COOKIES.get('username', '')
    book_obejct = Book.objects.all()
    ctx = {}
    ctx['username'] = username
    ctx['book_obejct'] = book_obejct

    if req.POST:
        try:
            req_dict = req.POST  # req_dict是页面提交的参数
            button_value = req_dict['button']  # 1是搜索  2是归还
            print('button_value : {}'.format(button_value))

            if button_value == '0':
                searchBookId = req.POST['searchBookId']
                search_borrowBook_obejct = BorrowBook.objects.get(borrowBookId=int(searchBookId))  # 获取借书表的对象
                borrowData = search_borrowBook_obejct.borrowData
                ctx['borrowData'] = borrowData

                search_book_obejct = Book.objects.get(bookId=int(searchBookId))     # 获取书的对象
                ctx['search_book_obejct'] = search_book_obejct

            else:                               # 点击了归还按钮
                returnBookId = int(req.POST['button'])
                search_book_obejct = Book.objects.get(bookId=returnBookId)  # 获取书的对象
                search_borrowBook_obejct = BorrowBook.objects.get(borrowBookId=returnBookId)  # 获取借书表的对象
                search_borrowBook_obejct.delete()       # 删除借书表该行数据

                # book表的剩余量、可借都加1
                search_book_obejct.bookSurplus += 1
                search_book_obejct.isBorrow += 1
                search_book_obejct.save()

                # 读者表已借书本减1
                user_object = User.objects.get(username=username)
                user_object.borrowedNum -= 1
                user_object.save()

                # 初始化
                ctx = {}
        except Exception as e:
            print(e)

    return render(req, 'returnBook.html', ctx)
