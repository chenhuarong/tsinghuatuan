#-*- coding: UTF-8 -*-
from django.db import models


class User(models.Model):
    weixin_id = models.CharField(max_length=255)
    stu_id = models.CharField(max_length=255)

class  Activity(models.Model):
    name = models.CharField(max_length=255)
    key = models.CharField(max_length=255)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    place = models.CharField(max_length=255)
    book_start = models.DateTimeField()
    book_end = models.DateTimeField()
    total_tickets = models.IntegerField()
    remain_tickets = models.IntegerField()

class Ticket(models.Model):
    user = models.ForeignKey(User)
    unique_id = models.CharField(max_length=255)
    activity = models.ForeignKey(Activity)
    isUsed = models.IntegerField()
    seat = models.CharField(max_length=255)

class Order(models.Model):
    user = models.ForeignKey(User)
    activity = models.ForeignKey(Activity)
    isCancelled = models.BooleanField()
    tickets = models.IntegerField()
