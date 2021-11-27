from django.db import models
from datetime import datetime    

# Create your models here.
class userInfo(models.Model):
    fullname= models.CharField(max_length=100)
    email= models.EmailField()
    contact= models.CharField(max_length=50)
    password= models.TextField()
    tip_id= models.IntegerField(default=0)
    tip_date= models.DateField(null=True, blank=True)
    date_created=models.DateTimeField()

class tipData(models.Model):
    tipContent = models.TextField()
    tipType = models.CharField(max_length=10)
    date_created=models.DateTimeField(default=datetime.now)

class stockList(models.Model):
    name = models.TextField()
    code = models.CharField(max_length=10)
    is_active = models.SmallIntegerField(default=1)
    sector = models.TextField()
    date_created=models.DateTimeField(default=datetime.now)