from django.db import models
from mongoengine import *

# Create your models here.

class LiveInfo(Document):
    title = StringField()
    url = StringField()
    obs = StringField()
    tag = StringField()
    owner = StringField()
    ob_num = IntField()
    # on-off =IntField()
    data_from = StringField()
    room_pic=StringField()
    room_imgsrc=StringField()

    meta = {'collection':'livetbl'}
