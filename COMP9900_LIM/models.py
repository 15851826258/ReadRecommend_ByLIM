"""
backend model
Steps to migrate:
1.makemigrations COMP9900_LIM
2.sqlmigrate COMP9900_LIM 0001
3.migrate
"""
from django.db import models


class User(models.Model):
    # userid
    UserId = models.AutoField('UserId', primary_key=True)
    # username
    UserName = models.CharField('UserName', unique=True, max_length=15)
    # password
    Password = models.CharField('Password', null=False, max_length=15)
    # createtime set the time
    CreateTime = models.DateTimeField(auto_now=True)
    # recommend model set as int
    Recommend_model = models.IntegerField('Recommend_model', default=0)
    # last add time
    Last_add = models.IntegerField('Last_add', default=0)

    # change the defalut name of the table
    # if not set,the name will be 'database_tablename'
    class Meta:
        db_table = 'User'


class Book(models.Model):
    # Bookid
    BkId = models.AutoField('Bkid', primary_key=True)
    # Book Title(name)
    BkTitle = models.CharField('BkTitle', max_length=100)
    # Book Author(s)
    BkAuthor = models.CharField('BkAuthor', max_length=100)
    # Book Publisher
    BkPublisher = models.CharField('BkPublisher', max_length=100)
    # Book publication date
    BkPubDate = models.CharField('BkPubDate', max_length=8)
    # Book category
    Category = models.CharField('Category', max_length=20)
    # popularity
    Popularity = models.IntegerField('Popularity', default=0)
    # Rating
    Rating = models.FloatField('Reting', default=0)

    # change the defalut name of the table
    class Meta:
        db_table = 'Book'


class Collection(models.Model):
    # collectionId
    CoId = models.AutoField('CoId', primary_key=True)
    # collection Name set by the owner
    CoName = models.CharField('CoName', max_length=15)
    # owner --foreign key of user
    CoOwner = models.ForeignKey('User', on_delete=models.CASCADE)
    # createtime --won't change after set
    CoCreateDate = models.DateTimeField(auto_now_add=True)
    # updatedate --Everytime being update the time will change
    CoUpdateDate = models.DateTimeField(auto_now=True)

    # change the defalut name of the table
    class Meta:
        db_table = 'Collection'


class Review(models.Model):
    # review id
    ReviewId = models.AutoField('ReviewId', primary_key=True)
    # book id --foreign key of table 'Book'
    BkId = models.ForeignKey('Book', on_delete=models.CASCADE)
    # user id --foreign key of table 'User'
    UserId = models.ForeignKey('User', on_delete=models.CASCADE)
    # review content
    ReviewCont = models.TextField('ReviewCont')
    # review date
    ReviewDate = models.DateTimeField('ReviewDate', auto_now_add=True)
    # poster directory
    Poster = models.CharField('Poster', null=False, max_length=15)

    # change the defalut name of the table
    class Meta:
        db_table = 'Review'


class CoBk(models.Model):
    # three foreign keys
    Userid = models.ForeignKey('User', on_delete=models.CASCADE)
    CoId = models.ForeignKey('Collection', on_delete=models.CASCADE)
    BkId = models.ForeignKey('Book', on_delete=models.CASCADE)
    # createtime set the time for the top 10 recent book
    CreateTime = models.DateTimeField(auto_now=True)
    read_dates = models.IntegerField('read_days', null=True)
    status = models.CharField('status', null=True, max_length=15)

    # change the defalut name of the table
    class Meta:
        db_table = 'CoBk'


class Rating(models.Model):
    # foreign keys
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    book = models.ForeignKey('Book', on_delete=models.CASCADE)
    # ratung stars as float
    rating_stars = models.FloatField('rating stars', null=False)
    #create time
    post_time = models.DateTimeField('post_time', auto_now=True)
    #first time rate
    first_rate = models.CharField('first_rate', max_length=7, null=True)

    class Meta:
        db_table = 'rating_record'


class Goals(models.Model):
    # user id foreign key
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    # create time
    create_time = models.CharField('create_time', max_length=7, null=False)
    # num of goal
    goal = models.IntegerField('goal', default=0)

    class Meta:
        db_table = "Goals"
