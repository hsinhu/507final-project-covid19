from django.db import models
from django.core.validators import MinLengthValidator


class CountryCases(models.Model):
    Country_ID = models.CharField(max_length=100, null=False, primary_key = True)
    Country_Name = models.CharField(max_length=100, null=False)
    Confirmed = models.IntegerField()
    Deaths = models.IntegerField()
    Recovered = models.IntegerField()


class StateCases(models.Model):
    State_Name = models.CharField(max_length=100, null=False, primary_key = True)
    State_fips = models.IntegerField(null=False)
    State_abbr = models.CharField(max_length=3, null=False)
    Confirmed = models.IntegerField()
    Confirmed_Per_100000_People = models.CharField(max_length=20)
    Deaths = models.IntegerField()
    Deaths_Per_100000_People = models.CharField(max_length=20)


class CountyCases(models.Model):
    State_Name = models.ForeignKey('StateCases', null=False,
                                on_delete=models.CASCADE)
    County_fips = models.IntegerField()
    County_name = models.CharField(max_length=100, null=False)
    Confirmed = models.IntegerField()
    Confirmed_Per_100000_People = models.CharField(max_length=20)
    Deaths = models.IntegerField()
    Deaths_Per_100000_People = models.CharField(max_length=20)


class StateProjection(models.Model):
    State_Name = models.CharField(max_length=100, null=False)
    date_reported = models.DateField(null=False)
    allbed_mean = models.IntegerField()
    ICUbed_mean = models.IntegerField()
    InvVen_mean = models.IntegerField()
    deaths_mean_daily = models.IntegerField()
    totalDeath_mean = models.IntegerField()
    bedshortage_mean = models.IntegerField()
    icushortage_mean = models.IntegerField()


