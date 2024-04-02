# movierama
a small social sharing app where registered users can submit a movie they like and others will like or hate that movie.

# so, walk through:
a few words about the submitted code:
The router.py is the flask router script that serves as the backend of the web app and is written in python. There you can see 3 main endpoints, "get_movies" which gets all the submitted movies and can filter them, "insert_movie" which is used to insert movie to database, and "opinion_movie" which is called when liking or hating a movie. The data are persisted in a relational sqlite3 db that I installed on the server.
The helloworld.vue is the front end of the app. (ignore the irrelevant name "helloworld"). I use vue js 2 for the frontend and here I use axios to call the backend endpoints and you can see at the top of the component how html places the data in the UI. 
Finally, I serve the frontend and backend builds from a linux server (ec2-instance) on amazon web services. You can access it from the link above.

# a few words on how to use the app
When landing on the landing page, as an unregistered user, you can see some movies I have stored in the database. You can sort them by clicking on the likes, hates, date buttons. You can filter by user who submitted the movie, by clicking on a name in a movie box, and click the name again to remove the user filter. Now if you want to insert or like a movie, put a name and password on the top of the page and either log in or sign up (does not make a difference). Now you can like/hate movies as per the requirements, see what movies you have already liked and insert movie. You cannot like you own movies. Log out to become unregistered again, and log in with different name.
