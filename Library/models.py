from django.db import models
import datetime
import django
# Create your models here.
# 用户表
class User(models.Model):
    username = models.CharField(max_length=50, verbose_name='用户名')
    password = models.CharField(max_length=50, verbose_name='密码')
    readerName = models.CharField(max_length=50, verbose_name='读者名', null=True)
    borrowNum = models.IntegerField(verbose_name='可借阅书籍数量', null=True)
    borrowedNum = models.IntegerField(verbose_name='已借阅书籍数量', null=True)
    telphone = models.CharField(max_length=50, verbose_name='手机号', null=True)
    email = models.CharField(max_length=50, verbose_name='邮箱', null=True)

    def __unicode__(self):
        return self.username

    class Meta:
        verbose_name = '读者'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username

# 书籍表
class Book(models.Model):
    bookId = models.IntegerField(primary_key=True, verbose_name='书籍ID')
    bookName = models.CharField(max_length=50, verbose_name='书籍名字')
    author = models.CharField(max_length=50, verbose_name='书籍作者')
    bookPublisher = models.CharField(max_length=50, verbose_name='书籍出版社')
    bookPublishDate = models.DateField(verbose_name='书籍出版时间')
    bookStorage = models.DateField(auto_now_add=True, verbose_name='书籍入库时间')
    bookNums = models.IntegerField(verbose_name='书籍总数量')
    bookSurplus = models.IntegerField(verbose_name='书籍剩余数量')
    isBorrow = models.IntegerField(verbose_name='可借')
    isLack = models.IntegerField(verbose_name='缺少')
    isNew = models.IntegerField(verbose_name='新书')

    def __unicode__(self):
        return self.bookName

    class Meta:
        verbose_name = '书籍'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.bookName

# 借书表
class BorrowBook(models.Model):
    borrowUser = models.ForeignKey(User, related_name='userBorrow', verbose_name='借书者', on_delete=models.CASCADE)
    borrowBookId = models.ForeignKey(Book, related_name='bookIdBorrow', verbose_name='书籍ID', on_delete=models.CASCADE)
    borrowData = models.DateField(default=django.utils.timezone.now, verbose_name='书籍借书时间')
    returnData = models.DateField(verbose_name='书籍归还时间', null=True)

    class Meta:
        verbose_name = '借书表'
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.borrowUser

# 预订书表
class subscribeBook(models.Model):
    subscribeUser = models.ForeignKey(User, related_name='userSubscribe', verbose_name='读者', on_delete=models.CASCADE)
    subscribeBookName = models.CharField(max_length=50, verbose_name='书籍编号')
    subscribeData = models.DateField(default=django.utils.timezone.now, verbose_name='书籍预订时间')


    class Meta:
        verbose_name = '预订书表'
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.subscribeBookName



# 还书表
class ReturnBook(models.Model):
    returnUser = models.ForeignKey(User, related_name='userReturn', verbose_name='还书者', on_delete=models.CASCADE)
    returnBookId = models.ForeignKey(Book, related_name='bookIdReturn', verbose_name='书籍ID', on_delete=models.CASCADE)
    returnData = models.DateField(default=django.utils.timezone.now, verbose_name='书籍归还时间')
    bookBroken = models.IntegerField(verbose_name='是否破坏')
    bookTimeout = models.IntegerField(verbose_name='是否超时')

    class Meta:
        verbose_name = '还书表'
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.returnBookId

    def __str__(self):
        return self.returnUser

# 缺书表
class LackBook(models.Model):
    LackUser = models.ForeignKey(User, related_name='userLack', verbose_name='缺书者', on_delete=models.CASCADE)
    LackBook = models.CharField(max_length=50, verbose_name='书籍名字')
    LackData = models.DateField(default=django.utils.timezone.now, verbose_name='缺书登记时间')

    class Meta:
        verbose_name = '缺书表'
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.LackBook

    def __str__(self):
        return self.LackBook
















