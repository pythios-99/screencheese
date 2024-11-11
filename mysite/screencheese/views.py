from django.shortcuts import render,redirect, get_object_or_404, get_list_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from .models import Movie, Review, Genre
from django.contrib.auth.decorators import login_required
from django.db.models import Q
# from django.db.models.aggregates import Avg
from django.db.models.aggregates import Count
import requests
from .key import key
from pprint import pprint
from  django.utils import timezone
from datetime import timedelta
from datetime import date

@login_required(login_url="/screencheese/login")
def home (request) :

    current_date = timezone.now()
    max_date = current_date - timedelta(days=56)
    movies_in  = Movie.objects.filter(release_date__gte=max_date, release_date__lte=current_date)

    best_rated = Movie.objects.order_by("-avg_rating")[:40]
    user_liked_genres = Genre.objects.filter(movie__review__rating__gt=7, movie__review__author=request.user)
    recommended = Movie.objects.filter(genres__in=user_liked_genres).order_by("-avg_rating").exclude(review__author=request.user)[:5]

    reviewed_movies = []
    genres_list = []
    recommendations = []
    movie_ids = []
    further_recommendations_check = False
    for movie in best_rated :
        try:
            review = Review.objects.get(movie=movie, author=request.user)
            reviewed_movies.append(movie)
            if review.rating >= 7 :
                      further_recommendations_check = True
                      for genre in movie.genres.all() :
                           if genre not in genres_list:
                            genres_list.append(genre)
                            movie_ids.append(movie.id)
                      
        except:
            pass
            

    if further_recommendations_check == True :
        for movie in best_rated:
            for genre in movie.genres.all():
                if genre in genres_list:
                    if movie not in recommendations :
                        if movie not in reviewed_movies :
                            # print(movie)
                            recommendations.append(movie) 
            
    if recommendations == [] :
         for movie in best_rated :
            recommendations.append(movie)
    
    top_rated =  Movie.objects.order_by("-avg_rating")[:10]

    return(render(request, 'screencheese/home.html', context = {"recently_released":movies_in, "recommendations":recommendations, "top_rated":top_rated})) #'path':path

def sign_up (request):

       return render(request, "screencheese/sign_up.html")

def user_creator (request) :
    try:


        user_name = request.POST['username']
        user_email = request.POST['email']
        user_password = request.POST['password']

        user = User.objects.create_user(username=user_name, email=user_email, password=user_password)
        
        # you can also use the create user function
    except (KeyError) :
           return render(request, "screencheese/sign_up.html",
                         {"user" : user, 
                          "error_message": "Unable to create user.", }
                        )
    except(IntegrityError):
           return render(request, "screencheese/sign_up.html",
                         {"user" : user, 
                          "error_message": "Someone already has that username, please choose a new one.", }
                        )




    login(request,user)
    return redirect('screencheese:homepage')



def log_in (request,) :
    return render(request, "screencheese/log_in.html")



def log_iner(request): 

        user_username = request.POST["username"]
        user_password = request.POST["password"]
        user = authenticate(request, username=user_username, password=user_password)
        if user :
            login(request, user)
            return HttpResponseRedirect('home')
        
        elif user is None :
                return render(request,"screencheese/login_error_page.html")

        else :
                            return render(
            request,
            "screencheese/log_in.html",
            {
                "error_message": "Unable to log in.\nCheck all fields are filled with the correct information",
            },
        )


@login_required(login_url="/screencheese/login")
def log_out (request) :
       logout(request)
       return HttpResponseRedirect('login')



@login_required(login_url="/screencheese/login")
def search(request) :
    movie_name = request.GET["movie name"]
    movie_paths = []
    movie_ids = []
    api_key = key
    url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query=" + movie_name
    result = requests.get(url)
    contents = result.json()['results']
    
    
    for m in contents :
        if m["adult"] == False:
            try:
                if m['original_language'] == "en":
                    movie_paths.append(f"https://image.tmdb.org/t/p/w300{m['poster_path']}")
                    movie_ids.append(m['id'])
            except:
                 pass
        
         #+ m['poster_path'])






    
    return render(request, "screencheese/search_results.html", context= {"movie_name":movie_name, "movies": zip(movie_ids, movie_paths)})



       #return redirect("screencheese:movie_page", movie=movie_name)




@login_required(login_url="/screencheese/login")
def create_movie_page (request,movie_id ) :
    api_key = key
    movie = movie_id
    url = "https://api.themoviedb.org/3/movie/" + movie + f'?api_key={api_key}'
    
    result = requests.get(url)
    contents = result.json()

    credits_url = f"https://api.themoviedb.org/3/movie/{movie}/credits?api_key={api_key}"
    credits_result = requests.get(credits_url)
    credits_contents = credits_result.json()

    # print (contents)
    # pprint(f"{credits_contents['crew']}")
    



    movie_name = contents["title"]

    try :
        if Movie.objects.get(movie_name=movie_name):
            return redirect ("screencheese:movie_page", movie_name)
    except:
         
       

        # return render(request,"screencheese/tempo.html")
    

        rel_date = contents["release_date"]
        film_studio = contents["production_companies"][0]["name"]
        poster_path = contents["poster_path"]
        genres = []
        all_genres = contents["genres"]
        for genre in all_genres:
            try:
                
                genres.append(Genre.objects.get(genre_name=genre["name"]))
            except: 
                g = Genre.objects.create(genre_name=genre["name"])
                genres.append(g)
        description = contents["overview"]
        poster_path = f"https://image.tmdb.org/t/p/w300{contents["poster_path"]}"
        for person in credits_contents['crew'] :
            
            if person["job"] == "Director" :
                director = person["name"]
        status = contents["status"]
        if status == "Released" :
             released = True
        else: 
             released = False


        new_movie = Movie.objects.create(movie_name=movie_name,release_date=rel_date,film_studio=film_studio,avg_rating=5.0,released=released,description=description,poster_path=poster_path,director=director)
        new_movie.genres.add(*genres)
        new_movie.save()
        


        


    return redirect('screencheese:movie_page', movie=new_movie.id)



@login_required(login_url="/screencheese/login")
def movie_page (request,movie) :
    
    movie_id = movie

    movie = Movie.objects.get(id=movie_id)
    try:
        user_review = Review.objects.get(author=request.user, movie=movie)
    except:
          user_review = None


    all_reviews = Review.objects.filter(movie=movie).exclude(author=request.user)


    all_reviews = all_reviews.annotate(nlikers=Count('likers')).order_by("-nlikers")


    current_date  = date.today()
    if movie.release_date <= current_date :
         movie.released = True
    else:
         movie.released = False

    if movie.released == True:
         release_check = True
    else :
         release_check = None

    

    if user_review:
        relevancy_score = None

    else:
        try:
            all_users_reviews = Review.objects.filter(author=request.user)

            user_liked_genres = Genre.objects.filter(movie__review__rating__gt=7, movie__review__author=request.user)
            relevancy_score = 0
            for genre in movie.genres.all() :
                if genre in user_liked_genres :
                    relevancy_score += 5
                    for review in all_users_reviews :
                        for review_genre in review.movie.genres.all() :
                            if review_genre == genre :
                                if review.rating >= 7 :
                                    relevancy_score += 1




        except:
            relevancy_score = 0


    genre_names = []
    for genre in movie.genres.all() :
         genre_names.append(genre.genre_name)
         print (genre.genre_name)

    rating_percentage = movie.avg_rating * 10
    rating_percentage = round(rating_percentage,0)
    print(rating_percentage)

    if rating_percentage <50:
         colour_check = "red"
    if rating_percentage >=50 and rating_percentage < 70:
         colour_check = "yellow"
    elif rating_percentage >= 70:
         colour_check = "green"


    return render(request,"screencheese/movie_page.html", context={"movie":movie, 'user_review':user_review, 'all_reviews':all_reviews, "relevancy_score":relevancy_score, "genres": genre_names, "release_check": release_check, "colour":colour_check, "percentage":rating_percentage})



@login_required(login_url="/screencheese/login")
def review_publisher (request,movie) :
    review_score = float(request.GET['review_score'])
    review_text = request.GET['review_text']
    movie_id = movie
    movie = Movie.objects.get(id=movie_id)
    review = Review.objects.create(movie=movie, author=request.user, rating=review_score, text=review_text)
    
    review_count = movie.review_set.all().count()
    if movie.avg_rating:
        movie.avg_rating = (float(movie.avg_rating * (review_count - 1)) + review_score)/review_count
    else:
        movie.avg_rating = review_score
    movie.save()
    # score = 0
    # num = 0

    # for review in all_reviews:
    #     if review.rating:
    #         score += review.rating
    #         num += 1

    # avg_score = round(score/num,1)
    # movie.avg_rating = avg_score
    return redirect('screencheese:movie_page', movie=movie.id)



@login_required(login_url="/screencheese/login")
def delete_review (request,movie) :
    movie_id = movie
    movie = Movie.objects.get(id=movie_id)
    review = Review.objects.get(movie=movie, author=request.user)
    review.delete()
    return redirect(request.META['HTTP_REFERER'])   

@login_required(login_url="/screencheese/login")
def all_movies (request) :
    
    all_movies = Movie.objects.order_by("-avg_rating")
    return render(request, "screencheese/all_movies.html", context = { 'all_movies':all_movies })

@login_required(login_url="/screencheese/login")
def review_manager (request) :
      user_reviews = Review.objects.filter(author=request.user)
      return render (request, "screencheese/review_manager.html", context={"user_reviews":user_reviews})

@login_required(login_url="/screencheese/login")
def like(request,id):
      review = Review.objects.get(id = id)
      review.likers.add(request.user)
      movie = review.movie.id
      print (review.movie.movie_name)
      return redirect(request.META['HTTP_REFERER'], movie)

@login_required(login_url="/screencheese/login")
def unlike(request,id):
      review = Review.objects.get(id = id)
      review.likers.remove(request.user)
      movie = review.movie.id
      return redirect(request.META['HTTP_REFERER'], movie)