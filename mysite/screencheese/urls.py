from django.urls import path
from . import views




app_name = "screencheese"
urlpatterns = [
    path("home", views.home , name="homepage"),
    path("login", views.log_in, name="log_in"),
    path("log_iner", views.log_iner, name="log_iner"),
    path("sign_up", views.sign_up , name = "SignUpPage"),
    path("user_creator", views.user_creator, name="user_creator"),
    path("log_out", views.log_out, name="log_out"),
    path("search", views.search, name="search"),
    path("movie/<int:movie>", views.movie_page, name="movie_page"),
    path("review_publisher/<int:movie>", views.review_publisher, name="review_publisher"),
    path("delete_review/<int:movie>", views.delete_review, name="delete_review"),
    path("all_movies", views.all_movies, name="all_movies"),
    path("review_manager", views.review_manager, name="review_manager"),
    path("like/<int:id>", views.like, name="like"),
    path("unlike/<int:id>", views.unlike, name="unlike"),
    path("create_movie_page/<str:movie_id>", views.create_movie_page, name="create_movie_page"),
#    path("", views., name=""),



]
