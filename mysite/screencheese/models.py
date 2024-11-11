import datetime
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.


class Genre (models.Model) :
    genre_name = models.CharField(max_length=100)
    genre_description = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self) -> str:
        return self.genre_name


class Movie (models.Model) :
    movie_name = models.CharField(max_length=100)
    release_date = models.DateField(null=True,blank=True)
    film_studio = models.CharField(max_length=100,null=True,blank=True)
    avg_rating = models.DecimalField(max_digits=3,decimal_places=1,null=True,blank=True)
    released = models.BooleanField(null=True,blank=True)
    genres = models.ManyToManyField(Genre,null=True,blank=True)
    description = models.TextField(null=True,blank=True)
    poster_path = models.URLField(null=True,blank=True)
    director = models.CharField(null=True,blank=True, max_length=100)

    def __str__(self) -> str:
        return self.movie_name

class Review (models.Model) :
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    likers = models.ManyToManyField(User,related_name='liked_reviews',null=True, blank=True)
    rating = models.DecimalField(max_digits=3,decimal_places=1)
    text = models.TextField(null=True, blank=True)
    pub_date = models.DateField("date published", auto_now_add=True)

    

    def __str__(self) -> str:
        return f'{self.movie.movie_name} ({self.rating})'  



