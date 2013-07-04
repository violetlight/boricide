from django.db import models
from django.contrib.auth.models import User
from tastypie.models import create_api_key
import urllib2
import urllib
import json

models.signals.post_save.connect(create_api_key, sender=User)


class Artist(models.Model):
    name = models.CharField(max_length=100)
    website = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)

    def __unicode__(self):
        return self.name


class Venue(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    lat = models.DecimalField(max_digits=20, decimal_places=10, blank=True)
    lng = models.DecimalField(max_digits=20, decimal_places=10, blank=True)

    def save(self, *args, **kwargs):
        url = 'http://maps.googleapis.com/maps/api/geocode/json?sensor=false&address=' + urllib.quote_plus(self.address)
        try:
            data = json.loads(urllib2.urlopen(url).read())
            self.lat = data["results"][0]["geometry"]["location"]["lat"]
            self.lng = data["results"][0]["geometry"]["location"]["lng"]
        except:
            return
        super(Venue, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name


class Event(models.Model):
    name = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    venue = models.ForeignKey(Venue)
    door_price = models.DecimalField(max_digits=5, decimal_places=2)
    advance_price = models.DecimalField(max_digits=5, decimal_places=2, blank=True)
    description = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.advance_price:
            self.advance_price = self.door_price
        super(Event, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name


class Concert(Event):
    artists = models.ManyToManyField(Artist)


class UserPref(models.Model):
    user = models.OneToOneField(User)
    ArtistsStarred = models.ManyToManyField(Artist, blank=True)
    ConcertsStarred = models.ManyToManyField(Concert, blank=True)

    def __unicode__(self):
        return self.user.get_full_name()
