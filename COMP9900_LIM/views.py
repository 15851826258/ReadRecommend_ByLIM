# from django.core.serializers import json
from django.shortcuts import render
import json
# Create your views here.
from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse, redirect
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib import messages
from . import models
import datetime


def index(request):
    if request.method == 'POST':
        # get the information from POST request
        username = request.POST.get("username")
        password = request.POST.get("password")
        # try method. in case there is no such a user
        try:
            # create a user instance
            user_instance = models.User.objects.get(UserName=username)
            # check the password
            if user_instance.Password == password:
                # password right login success!
                request.session['username'] = username
                # login success-->homepage.html
                return HttpResponseRedirect('homepage/')
            else:
                # password wrong login fail!
                messages.error(request, 'Wrong password!Please try again.')
                return render(request, 'login/index.html')
        except models.User.DoesNotExist:
            messages.error(request, "Username not exist")
            return render(request, 'login/index.html')
    return render(request, 'login/index.html')


def regist(request):
    if request.method == 'POST':
        # get the input from website request
        username = request.POST.get('username')
        password = request.POST.get('password')
        # input check start #
        try:  # check if the user exist
            user_check = models.User.objects.get(UserName=username)  # get the user instance  # user exists
            print("Username has been used")
            messages.error(request, "Username has been used")
            return render(request, 'login/regist.html')
        except models.User.DoesNotExist:
            # create a object of user
            User_ob = models.User()
            # put the username and password in
            User_ob.UserName = username
            User_ob.Password = password
            User_ob.save()  # save the change to the database

            # start--create a default collection for each new user
            default_collection = models.Collection()  # create a collection instance
            default_collection.CoName = 'Default'  # a default name for collection
            default_collection.CoOwner = models.User.objects.get(UserId=User_ob.UserId)
            default_collection.save()
            request.session["username"] = username
            # end--create a default collection for each new user
            return HttpResponseRedirect('homepage/')
    return render(request, "login/regist.html")


def profileview(request):
    if request.method == 'GET':
        # get the user name in the session
        username = request.session["username"]
        # get the user information
        user_instance = models.User.objects.get(UserName=username)
        collection_instance = models.Collection.objects.filter(CoOwner_id=user_instance.UserId)
        collection_data = {}
        allbook = {}
        # get all this user's collections and all books this user added to his collection
        for i in collection_instance:
            books_id = models.CoBk.objects.filter(CoId_id=i.CoId)
            for j in books_id:
                allbook[j.CreateTime] = j
            collection_data[i.CoName] = i.CoId
        # sort by the books's added time
        # get the top 10 added books
        a = sorted(allbook.keys(), reverse=True)
        top_name = {}
        top_id = []
        for i in a:
            # get the time when this book was added
            Ctime = str(i).split(".")[0]
            book = allbook[i]
            bookname = models.Book.objects.get(BkId=book.BkId_id)
            if book.BkId_id in top_id:
                continue
            top_id.append(book.BkId_id)
            top_name[Ctime] = bookname
            if len(top_id) == 10:
                break
        # get the goal of this month
        year = str(datetime.datetime.now()).split("-")[0]
        month = str(datetime.datetime.now()).split("-")[1]
        date = year + '-' + month
        goals = models.Goals.objects.filter(user_id=user_instance.UserId).filter(create_time=date)
        if goals.exists():
            goal = goals[0].goal
        else:
            goal = 0
        # we considered that if user rate this book, which means user has finished reading this book
        num_rating = models.Rating.objects.filter(user_id=user_instance.UserId).filter(
            first_rate=date)
        num = 0
        for i in num_rating:
            # get the list of books rated by this month
            books = models.CoBk.objects.filter(Userid_id=i.user_id).filter(BkId_id=i.book_id)
            # make sure user has added this book to his collection
            if books.exists():
                num += 1
        return render(request, "login/profile.html",
                      {"username": username, "collection_data": collection_data, "top_10": top_name, 'user':username,
                       "num_rating": num, "goal": goal})


def createCollection(request):
    username = request.session["username"]  # get username from session
    if request.method == "POST":
        collection_name = request.POST.get("Coname")  # get the collection named by user
        User_instance = models.User.objects.get(UserName=username)  # get user information
        # start --duplication check
        Collections_instance = models.Collection.objects.filter(CoOwner_id=User_instance.UserId)
        collection_list = []
        for i in Collections_instance:
            collection_list.append(i.CoName)
        # if new created collection name had been used
        if collection_name in collection_list:
            messages.error(request, "collection name has been used")
            # reload the profile page
            return HttpResponseRedirect('profile/')
        # end --duplication check
        # start--create new collection
        else:
            New_collection_instance = models.Collection()
            New_collection_instance.CoName = collection_name
            New_collection_instance.CoOwner = models.User.objects.get(UserId=User_instance.UserId)
            New_collection_instance.save()
            # end--create new collection
            # create list of collection for return
            messages.success(request, "Successfully Create")
            # reload the profile page
            return HttpResponseRedirect('profile/')


def deleteCollection(request):
    username = request.session["username"]  # get username from session
    user_instance = models.User.objects.get(UserName=username)  # get user information
    if request.method == 'GET':
        coname = request.GET["id"]  # get the id of the collection which user wants to delete
        # check the default collection
        if coname != 'Default':
            # delete collection by name
            userid = user_instance.UserId
            Collection_instance = models.Collection.objects.get(CoName=coname, CoOwner=userid)
            # remove the books addition information in this collection
            models.CoBk.objects.filter(CoId_id=Collection_instance.CoId).delete()
            Collection_instance.delete()
            messages.success(request, "Successfully Delete")
            # reload the profile page
            return HttpResponseRedirect('profile/')
        else:
            # reload the profile page
            messages.error(request, "Cannot delete Default collection")
            return HttpResponseRedirect('profile/')


def logout(request):
    if request.method == 'GET':
        # remove the session
        del request.session['username']
        # after logout, show top 10 books with high popularity and high rating
        books = models.Book.objects.order_by('-Popularity', '-Rating').all()
        categories = []
        authors = []
        search_result_instance = {}
        if len(books) >= 10:
            books = books[:10]
        search_result_instance['Book'] = books
        # get these books categories and authors for filter function
        for i in books:
            if i.Category not in categories:
                categories.append(i.Category)
            if i.BkAuthor not in authors:
                authors.append(i.BkAuthor)
        return render(request, "login/search.html", {'username': '', 'search_result_instance': search_result_instance,
                                                     'nouser': 1,'Authors': sorted(set(authors)),
                                                     'Categories': sorted(set(categories))})
    return render(request, 'login/search.html')


def deleteBk(request):
    username = request.session["username"]  # get the username from session
    if request.method == 'POST':
        # get the book id and collection id
        record = request.GET["id"]
        book_id = record.split("@")[0]
        collection_id = record.split("@")[1]
        all = []
        # delete the book
        models.CoBk.objects.filter(CoId_id=collection_id).filter(BkId_id=book_id).delete()
        # get the updated books list
        books_list = models.CoBk.objects.filter(CoId_id=collection_id)
        for i in books_list:
            # get the book information
            all.append(models.Book.objects.get(BkId=i.BkId.BkId))
        return render(request, "login/codetail.html", {'username':username, "all": all, 'collection_id': collection_id})


def homepage(request):
    if request.session.get("username", ""):  # get the login status
        username = request.session["username"]  # get the username form session
        user_instance = models.User.objects.get(UserName=username)  # get user information
        # get all collections
        Collections_instance = models.Collection.objects.filter(CoOwner_id=user_instance.UserId)
        mode = int(user_instance.Recommend_model)  # get the recommendation model user selected last time
        books = []
        authors = []
        categories = []
        search_result_instance = {}
        # according to the last book user added to his collection and based on the last recommendation model he
        # chose to recommend the books with the same kind of the last added book to user
        if user_instance.Last_add != 0 and mode != 0:
            # get the book user added to his collection last time
            book = models.Book.objects.filter(BkId=user_instance.Last_add)
            book = book[0]
            if mode == 1:  # based on author
                # get the books have the same author with the book user added
                books = models.Book.objects.filter(BkAuthor=book.BkAuthor).order_by('-Popularity', '-Rating')
                # we only select the top 10 books from our search results and sorted by popularity and rating
                if len(books) >= 10:
                    books = books[:10]
                search_result_instance['Recommend'] = list(books)
            if mode == 2:  # based on category
                # get the book have the same category with the book user added
                books = models.Book.objects.filter(Category=book.Category).order_by('-Popularity', '-Rating')
                if len(books) >= 10:
                    books = books[:10]
                search_result_instance['Recommend'] = list(books)
            if mode == 3:  # based on rating
                for i in models.Book.objects.order_by('-Rating', '-Popularity').all():
                    # we only selected the books have the similar rating with the selected book
                    if abs(book.Rating - i.Rating) <= 0.5:
                        books.append(i)
                    if len(books) >= 10:
                        break
                search_result_instance['Recommend'] = books
            if mode == 4:  # based on popularity
                for i in models.Book.objects.order_by('-Popularity', '-Rating').all():
                    # we only selected the books have the similar popularity with the selected book
                    if abs(book.Popularity - i.Popularity) <= 2:
                        books.append(i)
                    if len(books) >= 10:
                        break
                search_result_instance['Recommend'] = books
        # get the list of authors and categories of our results in order to filter function
        for i in books:
            categories.append(i.Category)
            authors.append(i.BkAuthor)
        # and we also list 10 books with high rating and popularity
        books2 = models.Book.objects.order_by('-Popularity', '-Rating').all()
        if len(books2) >= 10:
            books2 = books2[:10]
        search_result_instance['Book'] = list(books2)
        for i in books2:
            categories.append(i.Category)
            authors.append(i.BkAuthor)
        search_result_instance['Author'] = []
        search_result_instance['User'] = []
        return render(request, 'login/search.html', {'username': username,
                                                     'search_result_instance': search_result_instance,
                                                     "collections": Collections_instance,
                                                     'Authors': sorted(set(authors)),
                                                     'Categories': sorted(set(categories))})
    else:
        # show top 10 books with high rating and high popularity
        books = models.Book.objects.order_by('-Popularity', '-Rating').all()
        categories = []
        authors = []
        search_result_instance = {}
        if len(books) >= 10:
            books = books[:10]
        search_result_instance['Book'] = list(books)
        search_result_instance['Author'] = []
        search_result_instance['User'] = []
        for i in books:
            categories.append(i.Category)
            authors.append(i.BkAuthor)
        return render(request, "login/search.html", {'search_result_instance': search_result_instance,
                                                     'Authors': sorted(set(authors)),
                                                     'Categories': sorted(set(categories)),'nouser': 1})


def search(request):
    search_cont = request.GET.get('search_content')  # get the search content
    search_result_instance = {}
    authors = []
    categories = []
    book_list = []
    author_list = []
    user_list = []
    # check the login status
    if request.session.get("username", ""):
        username = request.session["username"]  # get username from session
        # create a list to store collections information for addBook2Co drop-down box
        # receive data from web page requests
        User_instance = models.User.objects.get(UserName=username)  # get user information
        Collections_instance = models.Collection.objects.filter(CoOwner_id=User_instance.UserId)
        #  search for books with the search content in its title
        search_result_instance1 = models.Book.objects.filter(BkTitle__icontains=search_cont).order_by(
            '-Popularity', '-Rating')
        if search_result_instance1.exists():
            for i in search_result_instance1:
                book_list.append(i)
            # get all the authors and categories information of the results for filter function
            for i in book_list:
                if i.Category not in categories:
                    categories.append(i.Category)
                if i.BkAuthor not in authors:
                    authors.append(i.BkAuthor)
        search_result_instance['Book'] = book_list
        #  search for books with the search content in its author
        search_result_instance2 = models.Book.objects.filter(BkAuthor__icontains=search_cont).order_by(
            '-Popularity', '-Rating')
        # add books which are not in the title search results to author search result list
        if search_result_instance2.exists():
            for j in search_result_instance2:
                if j.BkAuthor not in authors:
                    authors.append(j.BkAuthor)
                if j.Category not in categories:
                    categories.append(j.Category)
                if j not in book_list:
                    author_list.append(j)
        search_result_instance['Author'] = author_list
        # seach for username with the search content in its username
        search_result_instance4 = models.User.objects.filter(UserName__icontains=search_cont)
        if search_result_instance4.exists():
            user_list = []
            for i in search_result_instance4:
                user_list.append(i)
        search_result_instance['User'] = user_list
        return render(request, "login/search.html",
                      {"username": username, "search_result_instance": search_result_instance,
                       "collections": Collections_instance, "search": search_cont, 'Authors': sorted(set(authors)),
                       'Categories': sorted(set(categories))})
    else:
        # search when no user is logged in
        #  search for books with the search content in its title
        search_result_instance1 = models.Book.objects.filter(BkTitle__icontains=search_cont).order_by(
            '-Popularity', '-Rating')
        if search_result_instance1.exists():
            for i in search_result_instance1:
                book_list.append(i)

            for i in book_list:
                if i.Category not in categories:
                    categories.append(i.Category)
                if i.BkAuthor not in authors:
                    authors.append(i.BkAuthor)
        search_result_instance['Book'] = book_list
        #  search for books with the search content in its author
        search_result_instance2 = models.Book.objects.filter(BkAuthor__icontains=search_cont).order_by(
            '-Popularity', '-Rating')
        if search_result_instance2.exists():
            for j in search_result_instance2:
                if j.BkAuthor not in authors:
                    authors.append(j.BkAuthor)
                if j.Category not in categories:
                    categories.append(j.Category)
                if j not in book_list:
                    author_list.append(j)
        search_result_instance['Author'] = author_list
        # seach for username with the search content in its username
        search_result_instance4 = models.User.objects.filter(UserName__icontains=search_cont)
        if search_result_instance4.exists():
            user_list =[]
            for i in search_result_instance4:
                user_list.append(i)
        search_result_instance['User'] = user_list
        return render(request, "login/search.html", {"search_result_instance": search_result_instance,
                                                     "search": search_cont, 'Authors': sorted(set(authors)),
                                                     'Categories': sorted(set(categories)), 'nouser': 1})


def addBk2Co(request):
    # get the login status
    if request.session.get("username", ""):
        username = request.session["username"]  # get username from session
        User_instance = models.User.objects.get(UserName=username)  # get user information
        # get collections information
        Collections_instance = models.Collection.objects.filter(CoOwner_id=User_instance.UserId)
        # start receiving data from web page requests
        authors = []
        categories = []
        if request.method == "POST":
            # get the parameters from front side
            record = request.POST.get("id", "")
            book_id = record.split("@")[0]
            co_id = record.split("@")[1]
            # get the search result of current page and after addBk2Co function, reload the same page
            search_result = request.POST["search_result"]
            print(search_result)
            search_result_instance = {}
            users_list = []
            authors_list = []
            books_list = []
            recommend_list = []
            # process the search result string
            # process the User part of the search result and assign the query result to search_result_instance
            # get the user id from search result string
            if len(search_result[1:-1].split("'User': ")[1]) > 2:  # if user search result exists
                users_result = search_result[1:-1].split("'User': ")[1][1:-1].replace(" ", "").split(",")
                for i in users_result:
                    users_list.append(models.User.objects.get(UserId=int(i.replace(
                        "<User:Userobject(", "").replace(")>", ""))))
            search_result = search_result[1:-1].split("'User': ")[0]
            # get the book id from author search result and assign the author query result to search_result_instance
            if len(search_result[:-2].split("'Author': ")[1]) > 2:  # if author search result exists
                authors_result = search_result[:-2].split("'Author': ")[1][1:-1].replace(" ", "").split(",")
                for i in authors_result:
                    book = models.Book.objects.get(BkId=int(i.replace(
                        "<Book:Bookobject(", "").replace(")>", "")))
                    authors_list.append(book)
                    if book.BkAuthor not in authors:
                        authors.append(book.BkAuthor)
                    if book.Category not in categories:
                        categories.append(book.Category)
            search_result = search_result.split("'Author': ")[0]
            # get the book id from book search result and assign the book query result to search_result_instance
            if len(search_result[:-2].split("'Book': ")[1]) > 2:  # if book search result exists
                books_result = search_result[:-2].split("'Book': ")[1][1:-1].replace(" ", "").split(",")
                for i in books_result:
                    book = models.Book.objects.get(BkId=int(i.replace(
                        "<Book:Bookobject(", "").replace(")>", "")))
                    books_list.append(book)
                    if book.BkAuthor not in authors:
                        authors.append(book.BkAuthor)
                    if book.Category not in categories:
                        categories.append(book.Category)
            search_result = search_result.split("'Book': ")[0]
            # get the book id from recommend search result and assign the recommend query result to search_result_instance
            if len(search_result) > 17:   # if recommend search result exists
                recommend_result = search_result[:-2].split("'Recommend': ")[1][1:-1].replace(" ", "").split(",")
                for i in recommend_result:
                    book = models.Book.objects.get(BkId=int(i.replace(
                        "<Book:Bookobject(", "").replace(")>", "")))
                    recommend_list.append(book)
                    if book.BkAuthor not in authors:
                        authors.append(book.BkAuthor)
                    if book.Category not in categories:
                        categories.append(book.Category)
            search_result_instance['Recommend'] = recommend_list
            search_result_instance['Book'] = books_list
            search_result_instance['Author'] = authors_list
            search_result_instance['User'] = users_list
            # check if this book has been added into this collection
            Cobook_list = models.CoBk.objects.filter(CoId_id=co_id)
            book_id_list = []
            for book in Cobook_list:
                book_id_list.append(book.BkId_id)
            if int(book_id) in book_id_list:
                messages.error(request, 'Duplicated Book add')
                return render(request, "login/search.html",
                                          {"username": username, "search_result_instance": search_result_instance,
                                           "collections": Collections_instance,
                                           'Authors': sorted(set(authors)), 'Categories': sorted(set(categories))})
            else:
                # change the data record in database
                CoBk = models.CoBk()
                CoBk.CoId_id = co_id
                CoBk.BkId_id = book_id
                CoBk.Userid = User_instance
                CoBk.read_dates = int(request.POST['days'])
                CoBk.save()
                # popularity add 1
                # change the user last added book record
                User_instance.Last_add = int(book_id)
                User_instance.save()
                Book = models.Book.objects.get(BkId=book_id)
                Popularity = Book.Popularity
                Book.Popularity = Popularity + 1
                Book.save()
                messages.success(request, "Add to collection successfully")
                return render(request, "login/search.html",
                                          {"username": username, "search_result_instance": search_result_instance,
                                           "collections": Collections_instance,
                                           'Authors': sorted(set(authors)), 'Categories': sorted(set(categories))})


def Bkdetail(request):
    if request.session.get("username", ""):  # check the status of login
        username = request.session["username"]  # get the username from session
        user_instance = models.User.objects.get(UserName=username)  # get the user information
        record = request.GET["id"]  # get the book_id
        book_id = record.split('@')[0]
        status = ''
        extend_days = ''
        # if user check the book detail from their owner collection, because we may add one book to different
        # collections, so only click the detail button from the collection page, we can get this book's accurate
        # information like the date when this book was added to this book
        if len(record.split('@')) == 2:
            if record.split('@')[1]:
                # get the collection information
                collection_id = record.split('@')[1]
                # get the date when this book was added to this information
                data = models.CoBk.objects.filter(BkId_id=book_id).filter(CoId_id=collection_id)
                add_date = data[0].CreateTime
                read_date = int(data[0].read_dates)
                # calculate the end reading date by datetime class
                end_date = data[0].CreateTime + datetime.timedelta(days=read_date)
                # calculate time interval between the current time and when the user added ths book to his collection
                num_days = (datetime.datetime.now() - data[0].CreateTime).days
                # if we rated this book, which means we have read this book
                if models.Rating.objects.filter(user_id=user_instance.UserId).filter(book_id=book_id).exists():
                    status = 'finished'
                else:
                    # if time interval < end reading date
                    if int(num_days) < read_date:
                        status = 'reading'
                    else:
                        status = 'not_read'
                        extend_days = 7
        # get the book's information
        search_result = models.Book.objects.get(BkId=book_id)
        # get the user's collections information
        collection_list = models.Collection.objects.filter(CoOwner_id=user_instance.UserId)
        # get the review information sorted by review_date
        Reviews = models.Review.objects.filter(BkId_id=book_id).order_by('-ReviewDate')
        # get all rating scores from all users
        rating_list = models.Rating.objects.filter(book_id=book_id)
        score_stars = 0
        count = 0
        num = 0
        # calculate the total score
        for i in rating_list:
            count += 1
            score_stars += i.rating_stars
        if count != 0:
            light_score_stars = int(score_stars / count)
        else:
            light_score_stars = 0
        num += light_score_stars
        light_stars = list(range(light_score_stars))
        # check the half shining star
        if count != 0:
            if score_stars / count - light_score_stars >= 0.5:
                num += 0.5
                half_stars = list(range(1))
                gray_stars = list(range(5 - light_score_stars - 1))
            else:
                half_stars = list(range(0))
                gray_stars = list(range(5 - light_score_stars))
        else:
            gray_stars = list(range(5))
            half_stars = list(range(0))
        # get the current user's rating information
        rating = models.Rating.objects.filter(user_id=user_instance.UserId).filter(book_id=book_id).all()
        if len(rating) == 1:
            rating_stars = rating[0].rating_stars
        else:
            rating_stars = 0
        rating_stars_light = int(rating_stars)
        rating_stars_gray = 5 - int(rating_stars)
        # if user didn't check the book detail information at their own collection page
        if not status:
            return render(request, "login/detail.html",
                      {"username": username, "book": search_result, "count": count, "numofRating": num,
                       "collections": collection_list, "reviews": Reviews, 'light_stars': light_stars,
                       'gray_stars': gray_stars, 'half_stars': half_stars, 'rating_stars_gray': rating_stars_gray,
                       'rating_stars_light': rating_stars_light})
        # if user check the book detail information at their own collection page and we will show its status
        elif status == 'finished' or status == 'reading':
            return render(request, "login/detail.html",
                          {"username": username, "book": search_result, "count": count, "numofRating": num,
                           "collections": collection_list, "reviews": Reviews, 'light_stars': light_stars,
                           'gray_stars': gray_stars, 'half_stars': half_stars, 'rating_stars_gray': rating_stars_gray,
                           'rating_stars_light': rating_stars_light, 'state': status, 'add_date': add_date,
                           "end_date": end_date, 'collection_id': collection_id})
        # if status is not_read, we need provide a input box to extend the end reading date
        else:
            return render(request, "login/detail.html",
                          {"username": username, "book": search_result, "count": count, "numofRating": num,
                           "collections": collection_list, "reviews": Reviews, 'light_stars': light_stars,
                           'gray_stars': gray_stars, 'half_stars': half_stars, 'rating_stars_gray': rating_stars_gray,
                           'rating_stars_light': rating_stars_light, 'state': status, 'add_date': add_date,
                           "end_date": end_date, 'extend': extend_days, 'collection_id': collection_id})
    else:
        # if no user is logged in
        record = request.GET["id"]
        book_id = record.split('@')[0]  # get the book id
        search_result = models.Book.objects.get(BkId=book_id)  # get the book information
        # get the book reviews and sorted by review_date
        Reviews = models.Review.objects.filter(BkId_id=book_id).order_by('-ReviewDate')
        rating_list = models.Rating.objects.filter(book_id=book_id)  # get all the rating records from all users
        # calculate the total rating score
        score_stars = 0
        count = 0
        num = 0
        for i in rating_list:
            count += 1
            score_stars += i.rating_stars
        if count != 0:
            light_score_stars = int(score_stars / count)
        else:
            light_score_stars = 0
        num += light_score_stars
        light_stars = list(range(light_score_stars))
        # check the half star
        if count != 0:
            if score_stars / count - light_score_stars >= 0.5:
                num += 0.5
                half_stars = list(range(1))
                gray_stars = list(range(5 - light_score_stars - 1))
            else:
                half_stars = list(range(0))
                gray_stars = list(range(5 - light_score_stars))
        else:
            gray_stars = list(range(0))
            half_stars = list(range(0))
        # set personal rating sore to 0
        rating_stars = 0
        rating_stars_light = int(rating_stars)
        rating_stars_gray = 5 - int(rating_stars)
        return render(request, "login/detail.html",
                      {"book": search_result, "reviews": Reviews, "count": count, "numofRating": num,
                       'light_stars': light_stars, 'gray_stars': gray_stars, 'half_stars': half_stars,
                       'rating_stars_gray': rating_stars_gray, 'rating_stars_light': rating_stars_light})


def extend(request):
    username = request.session["username"]  # get the username from session
    user_instance = models.User.objects.get(UserName=username)  # get the user information
    record = request.POST["book_id"]  # get the book id
    book_id = record.split('@')[0]
    extend = request.POST['days']  # get the extend reading date
    collection_id = record.split('@')[1]  # get the collection id
    # get the reading date information of this book
    data = models.CoBk.objects.filter(BkId_id=book_id).filter(CoId_id=collection_id).all()
    book = data[0]
    # change the record of reading book
    book.read_dates = extend
    book.save()
    # reload the book detail page
    return HttpResponseRedirect(f'Bkdetail/?id={book_id}@{collection_id}')


def addBk(request):
    if request.session.get("username", ""):  # check the login status
        username = request.session["username"]  # get the username from session
        user_instance = models.User.objects.get(UserName=username)  # get the user information
        book_id = request.POST['book_id'].split("@")[0]  # get the book id
        # get the id of collection which contains this book, user may want to add this book from one collection
        # to another collection
        collection_of_book = request.POST['book_id'].split("@")[1]
        collection_id = request.POST['collection_id']  # get the id of collection which user wants to add this book to
        # check if this book has been added to this collection
        books_list = models.CoBk.objects.filter(CoId_id=collection_id)
        books = []
        for i in books_list:
            books.append(i.BkId.BkId)
        if int(book_id) in books:
            # reload the book detail page
            if collection_of_book:
                messages.error(request, 'Duplicated book add')
                return HttpResponseRedirect(f'Bkdetail/?id={book_id}@{collection_of_book}')
            else:
                messages.error(request, 'Duplicated book add')
                return HttpResponseRedirect(f'Bkdetail/?id={book_id}')
        else:
            # change the data record in the database
            CoBk = models.CoBk()
            CoBk.BkId = models.Book.objects.get(BkId=book_id)
            CoBk.CoId = models.Collection.objects.get(CoId=collection_id)
            CoBk.Userid = user_instance
            CoBk.read_dates = int(request.POST['days'])
            CoBk.save()
            Book = models.Book.objects.get(BkId=book_id)
            Popularity = Book.Popularity
            Book.Popularity = Popularity + 1
            Book.save()
            # reload the book detail page
            if collection_of_book:
                messages.success(request, 'Successfully Add')
                return HttpResponseRedirect(f'Bkdetail/?id={book_id}@{collection_of_book}')
            else:
                messages.success(request, 'Successfully Add')
                return HttpResponseRedirect(f'Bkdetail/?id={book_id}')


def addReview(request):
    if request.session.get("username", ""):  # check the login status
        username = request.session["username"]  # get the username from session
        user_instance = models.User.objects.get(UserName=username)  # get the user information
        book_id = request.POST['book_id'].split("@")[0]  # get the book id
        collection_id = request.POST['book_id'].split("@")[1]  # get the collection id
        # get the review content
        content = request.POST['content']
        # add review to the database
        Review = models.Review()
        Review.BkId_id = book_id
        Review.ReviewCont = content
        Review.UserId_id = user_instance.UserId
        Review.Poster = user_instance.UserName
        Review.save()
        # reload the book detail page
        if collection_id:
            return HttpResponseRedirect(f'Bkdetail/?id={book_id}@{collection_id}')
        else:
            return HttpResponseRedirect(f'Bkdetail/?id={book_id}')
    else:
        # if not login, jump to the login page
        return render(request, "login/index.html")


def addRating(request):
    if request.session.get('username', ''):  # check the login status
        username = request.session['username']  # get the username from session
        user_instance = models.User.objects.get(UserName=username)  # get the user information
        rating_stars = request.POST['rating_stars']  # get the user rating
        book_id = request.POST['book_id'].split('@')[0]  # get the book id
        collection_id = request.POST['book_id'].split('@')[1]  # get the collection id
        # get user rating record for this book
        rating = models.Rating.objects.filter(user_id=user_instance.UserId).filter(book_id=book_id).all()
        if len(rating) == 1:  # if user have rated this book before
            rating[0].rating_stars = rating_stars
            rating[0].save()
        else:
            Rating = models.Rating()  # change the record in database
            Rating.book_id = book_id
            Rating.rating_stars = rating_stars
            Rating.user_id = user_instance.UserId
            Rating.first_rate = str(datetime.datetime.now()).split('-')[0] + '-' + str(datetime.datetime.now()).split(
                '-')[1]
            Rating.save()
        # reload the book detail page
        if collection_id:
            return HttpResponseRedirect(f'Bkdetail/?id={book_id}@{collection_id}')
        else:
            return HttpResponseRedirect(f'Bkdetail/?id={book_id}')
    else:
        # if not log in, jump to the login page
        return render(request, 'login/index.html')


def Codetail(request):
    record = request.GET["coid"]
    coid = record.split('@')[0]  # get the collection id
    user = record.split('@')[1]  # get the user id
    all = []
    # get all books from that collection
    books_list = models.CoBk.objects.filter(CoId_id=coid)
    # get collection information
    collection = models.Collection.objects.get(CoId=coid)
    for i in books_list:
        all.append(models.Book.objects.get(BkId=i.BkId.BkId))
    if request.session.get("username", ""):  # check the login status
        username = request.session["username"]  # get the username from session
        if user == username:  # if user check his own collection
            return render(request, 'login/codetail.html', {'username': username, 'collection_id': coid,
                                                           'all': all, 'collection_name': collection.CoName})
        else:
            return render(request, 'login/codetail.html', {'username': username, 'all': all,
                                                           'collection_name': collection.CoName})
    else:
        return render(request, 'login/codetail.html', {'all': all, 'collection_name': collection.CoName})


def Userdetail(request):
    if request.session.get("username", ""):  # check the login status
        username = request.session["username"]  # get the username from session
        record = request.GET["id"]  # get the searched user's id
        searched_user = models.User.objects.get(UserId=record)  # get searched user information
        if searched_user.UserName != username:  # if searched user is not current user
            # get searched user collections information
            collection_instance = models.Collection.objects.filter(CoOwner_id=searched_user.UserId)
            allbook = {}
            collection_data = {}
            for i in collection_instance:
                # check all books information and get top10 books from searched user's collections
                books_id = models.CoBk.objects.filter(CoId_id=i.CoId)
                for j in books_id:
                    allbook[j.CreateTime] = j
                collection_data[i.CoName] = i.CoId
            # sort by the books's added time
            a = sorted(allbook.keys(), reverse=True)
            top_name = {}
            top_id = []
            for i in a:
                # get the time when this book was added
                Ctime = str(i).split(".")[0]
                book = allbook[i]
                bookname = models.Book.objects.get(BkId=book.BkId_id)
                if book.BkId_id in top_id:
                    continue
                top_id.append(book.BkId_id)
                top_name[Ctime] = bookname
                if len(top_id) == 10:
                    break
            return render(request, 'login/Userdetail.html', {'username': username, "collection_data": collection_data,
                                                             'user': searched_user.UserName, 'top_10': top_name})
        else:
            # if searched user is current login user, then load the profile page
            return HttpResponseRedirect('profile/')
    else:
        record = request.GET["id"]
        collection_user = models.User.objects.get(UserId=record)
        # check all books information and get the top 10 added books from searched user's collections
        collection_instance = models.Collection.objects.filter(CoOwner_id=collection_user.UserId)
        allbook = {}
        collection_data = {}
        for i in collection_instance:
            books_list = []
            books_id = models.CoBk.objects.filter(CoId_id=i.CoId)
            for j in books_id:
                books_detail = models.Book.objects.get(BkId=j.BkId_id)
                books_list.append(books_detail)
                allbook[j.CreateTime] = j
            collection_data[i.CoName] = i.CoId
        # sort by the books's added time
        a = sorted(allbook.keys(), reverse=True)
        top_name = {}
        top_id = []
        for i in a:
            # get the time when this book was added
            Ctime = str(i).split(".")[0]
            book = allbook[i]
            bookname = models.Book.objects.get(BkId=book.BkId_id)
            if book.BkId_id in top_id:
                continue
            top_id.append(book.BkId_id)
            top_name[Ctime] = bookname
            if len(top_id) == 10:
                break
        return render(request, 'login/Userdetail.html', {"collection_data": collection_data, 'top_10': top_name})


def recommendModel(request):
    if request.session.get('username', ''):  # get the status of login
        username = request.session['username']  # get username from session
        User_instance = models.User.objects.get(UserName=username)  # get user information
        # get user's all collections
        Collections_instance = models.Collection.objects.filter(CoOwner_id=User_instance.UserId)
        mode = int(request.GET.get('mode'))  # get the recommend mode
        book_id = request.GET.get('book_id')  # get the selected book id
        book = models.Book.objects.get(BkId=book_id)  # get the information of selected book
        books = []
        authors = []
        categories = []
        search_result_instance = {}
        if mode == 1:  # based on author
            # search the books have the same author with the selected book and sorted by popularity and rating
            books = models.Book.objects.filter(BkAuthor=book.BkAuthor).order_by('-Popularity', '-Rating')
            # pick the top 10
            if len(books) >= 10:
                books = books[:10]
            search_result_instance['User'] = []
            search_result_instance['Author'] = list(books)
            search_result_instance['Book'] = []
        if mode == 2: # based on category
            # search the books have tht same category with the selected book and sorted by popularity and rating
            books = models.Book.objects.filter(Category=book.Category).order_by('-Popularity', '-Rating')
            if len(books) >= 10:
                books = books[:10]
            search_result_instance['User'] = []
            search_result_instance['Author'] = []
            search_result_instance['Book'] = list(books)
        if mode == 3: # based on rating
            # search the books have tht similar rating with the selected book and sorted by popularity and rating
            for i in models.Book.objects.order_by('-Popularity', '-Rating').all():
                if abs(book.Rating - i.Rating) <= 0.5:
                    books.append(i)
                if len(books) >= 10:
                    break
            search_result_instance['User'] = []
            search_result_instance['Author'] = []
            search_result_instance['Book'] = books
        if mode == 4: # based on popularity
            # search the books have tht similar popularity with the selected book and sorted by popularity and rating
            for i in models.Book.objects.order_by('-Popularity', '-Rating').all():
                if abs(book.Popularity - i.Popularity) <= 2:
                    books.append(i)
                if len(books) >= 10:
                    break
            search_result_instance['User'] = []
            search_result_instance['Author'] = []
            search_result_instance['Book'] = books
        # get authors and categories of all searched book for filter function
        for i in books:
            if i.Category not in categories:
                categories.append(i.Category)
            if i.BkAuthor not in authors:
                authors.append(i.BkAuthor)
        User_instance.Recommend_model = mode
        User_instance.save()
        # if recommend mode, we will not show filter input boxes
        return  render(request, 'login/search.html', {'username': username,
                                                      'search_result_instance': search_result_instance,
                                                      "collections": Collections_instance,
                                                      'Authors': sorted(set(authors)),
                                                      'Categories': sorted(set(categories)), 'Rate_init': 0,
                                                      "recommendationmodeal": 1})
        
    else:
        return render(request, 'login/index.html')


def filter(request):
    author = request.POST.get('Author_name')  # get the author filter information
    category = request.POST.get('Category')  # get the category filter information
    rating_score = request.POST.get('Rating_score')  # get the rating filter information
    search = request.POST.get('search_content')  # get the search content information
    if not rating_score:
        rating_score = 0
    search_result_instance = {}
    books_list = []
    author_book = []
    authors = []
    categories = []
    if request.session.get("username", ""):  # check the login status
        username = request.session["username"]  # get username from session
        User_instance = models.User.objects.get(UserName=username)  # get the user information
        # get this user's collections information
        Collections_instance = models.Collection.objects.filter(CoOwner_id=User_instance.UserId)
        if author:
            if category:  # if we filter with both author and category information
                # filter books searched by title and sort the filter result by tht popularity and rating
                search_result_instance1 = models.Book.objects.filter(BkTitle__icontains=search).filter(
                    BkAuthor=author).filter(Category=category).order_by('-Popularity', '-Rating')
                if search_result_instance1.exists():  # if filter result exists
                    # check if its rating higher than our filter rating parameter
                    for i in search_result_instance1:
                        rating_list = models.Rating.objects.filter(book_id=i.BkId)
                        count = 0
                        score_stars = 0
                        for j in rating_list:
                            count += 1
                            score_stars += j.rating_stars
                        if count:
                            if score_stars / count >= int(rating_score):
                                books_list.append(i)
                                authors.append(i.BkAuthor)
                                categories.append(i.Category)
                        else:
                            # if user didn't set the rating filter parameter we add the books without rating records
                            # into our result
                            if rating_score == 0:
                                books_list.append(i)
                                authors.append(i.BkAuthor)
                                categories.append(i.Category)
                # filter books searched by authorename and sort filter result by popularity and rating
                search_result_instance2 = models.Book.objects.filter(BkAuthor__icontains=search).filter(
                    BkAuthor=author).filter(Category=category).order_by('-Popularity', '-Rating')
                # if result exists
                if search_result_instance2.exists():
                    # check if its rating score higher than our filter rating parameter
                    for i in search_result_instance2:
                        rating_list = models.Rating.objects.filter(book_id=i.BkId)
                        count = 0
                        score_stars = 0
                        for j in rating_list:
                            count += 1
                            score_stars += j.rating_stars
                        if count:
                            if score_stars / count >= int(rating_score):
                                # filter out the duplicate book
                                if i not in books_list:
                                    author_book.append(i)
                                    authors.append(i.BkAuthor)
                                    categories.append(i.Category)
                        else:
                            # if user didn't set the rating filter parameter we add the books without rating
                            # records into our result
                            if rating_score == 0:
                                if i not in books_list:
                                    author_book.append(i)
                                    authors.append(i.BkAuthor)
                                    categories.append(i.Category)
                search_result_instance['Book'] = books_list
                search_result_instance['Author'] = author_book
                search_result_instance['User'] = []
                return render(request, 'login/search.html', {"username": username,
                                                             "search_result_instance": search_result_instance,
                                                             "collections": Collections_instance,
                                                             "search": search, 'Authors': sorted(set(authors)),
                                                             'Categories': sorted(set(categories))})
            else:  # filter with author
                # filter books searched by title with the author and sort filter result by popularity and rating
                search_result_instance1 = models.Book.objects.filter(BkTitle__icontains=search).filter(
                    BkAuthor=author).order_by('-Popularity', '-Rating')
                if search_result_instance1.exists():  # if result exists
                    for i in search_result_instance1:
                        # check if its rating higher than our filter rating parameter
                        rating_list = models.Rating.objects.filter(book_id=i.BkId)
                        count = 0
                        score_stars = 0
                        for j in rating_list:
                            count += 1
                            score_stars += j.rating_stars
                        if count:
                            if score_stars / count >= int(rating_score):
                                books_list.append(i)
                                categories.append(i.Category)
                                authors.append(i.BkAuthor)
                        else:
                            if rating_score == 0:
                                books_list.append(i)
                                categories.append(i.Category)
                                authors.append(i.BkAuthor)
                # filter books searched by authorname with author and sort filter result by popularity and rating
                search_result_instance2 = models.Book.objects.filter(BkAuthor__icontains=search).filter(
                    BkAuthor=author).order_by('-Popularity', '-Rating')
                if search_result_instance2.exists():
                    for i in search_result_instance2:
                        # check if its rating higher than our filter rating parameter
                        rating_list = models.Rating.objects.filter(book_id=i.BkId)
                        count = 0
                        score_stars = 0
                        for j in rating_list:
                            count += 1
                            score_stars += j.rating_stars
                        if count:
                            if score_stars / count >= int(rating_score):
                                if i not in books_list:
                                    author_book.append(i)
                                    categories.append(i.Category)
                                    authors.append(i.BkAuthor)
                        else:
                            if rating_score == 0:
                                if i not in books_list:
                                    author_book.append(i)
                                    categories.append(i.Category)
                                    authors.append(i.BkAuthor)
                search_result_instance['Book'] = books_list
                search_result_instance['Author'] = author_book
                search_result_instance['User'] = []
                return render(request, 'login/search.html', {"username": username,
                                                             "search_result_instance": search_result_instance,
                                                             "collections": Collections_instance,
                                                             "search": search, 'Authors': sorted(set(authors)),
                                                             'Categories': sorted(set(categories))})
        else:
            if category:
                # filter books searched by title with category and sort filter result by popularity and rating
                search_result_instance1 = models.Book.objects.filter(BkTitle__icontains=search).filter(
                    Category=category).order_by('-Popularity', '-Rating')
                if search_result_instance1.exists():
                    for i in search_result_instance1:
                        # check if its rating higher than our filter rating parameter
                        rating_list = models.Rating.objects.filter(book_id=i.BkId)
                        count = 0
                        score_stars = 0
                        for j in rating_list:
                            count += 1
                            score_stars += j.rating_stars
                        if count:
                            if score_stars / count >= int(rating_score):
                                books_list.append(i)
                                authors.append(i.BkAuthor)
                                categories.append(i.Category)
                        else:
                            if rating_score == 0:
                                books_list.append(i)
                                authors.append(i.BkAuthor)
                                categories.append(i.Category)
                # filter books searched by authorname with category and sort filter result by popularity and rating
                search_result_instance2 = models.Book.objects.filter(BkAuthor__icontains=search).filter(
                    Category=category).order_by('-Popularity', '-Rating')
                if search_result_instance2.exists():
                    for i in search_result_instance2:
                        # check if its rating higher than our filter rating parameter
                        rating_list = models.Rating.objects.filter(book_id=i.BkId)
                        count = 0
                        score_stars = 0
                        for j in rating_list:
                            count += 1
                            score_stars += j.rating_stars
                        if count:
                            if score_stars / count >= int(rating_score):
                                # remove the duplicate book
                                if i not in books_list:
                                    author_book.append(i)
                                    authors.append(i.BkAuthor)
                                    categories.append(i.Category)
                        else:
                            if rating_score == 0:
                                if i not in books_list:
                                    author_book.append(i)
                                    authors.append(i.BkAuthor)
                                    categories.append(i.Category)
                search_result_instance['Book'] = books_list
                search_result_instance['Author'] = author_book
                search_result_instance['User'] = []
                return render(request, 'login/search.html',
                              {"username": username, "search_result_instance": search_result_instance,
                               "collections": Collections_instance, "search": search, 'Authors': sorted(set(authors)),
                               'Categories': sorted(set(categories))})
            else:
                # filter books searched by title with rating score and sort the filter result by popularity and rating
                search_result_instance1 = models.Book.objects.filter(BkTitle__icontains=search).order_by(
                    '-Rating', '-Popularity')
                if search_result_instance1.exists():
                    for i in search_result_instance1:
                        # check if its rating higher than our filter rating parameter
                        rating_list = models.Rating.objects.filter(book_id=i.BkId)
                        count = 0
                        score_stars = 0
                        for j in rating_list:
                            count += 1
                            score_stars += j.rating_stars
                        if count:
                            if score_stars / count >= int(rating_score):
                                books_list.append(i)
                                authors.append(i.BkAuthor)
                                categories.append(i.Category)
                        else:
                            if rating_score == 0:
                                books_list.append(i)
                                authors.append(i.BkAuthor)
                                categories.append(i.Category)
                # filter books searched by authorname with rating and sort the filter result by popularity and rating
                search_result_instance2 = models.Book.objects.filter(BkAuthor__icontains=search).order_by(
                    '-Popularity', '-Rating')
                if search_result_instance2.exists():
                    for i in search_result_instance2:
                        # check if its rating higher than our filter rating parameter
                        rating_list = models.Rating.objects.filter(book_id=i.BkId)
                        count = 0
                        score_stars = 0
                        for j in rating_list:
                            count += 1
                            score_stars += j.rating_stars
                        if count:
                            if score_stars / count >= int(rating_score):
                                if i not in books_list:
                                    author_book.append(i)
                                    authors.append(i.BkAuthor)
                                    categories.append(i.Category)
                        else:
                            if rating_score == 0:
                                if i not in books_list:
                                    author_book.append(i)
                                    authors.append(i.BkAuthor)
                                    categories.append(i.Category)
                search_result_instance['Book'] = books_list
                search_result_instance['Author'] = author_book
                search_result_instance['User'] = []
                return render(request, 'login/search.html',
                              {"username": username, "search_result_instance": search_result_instance,
                               "collections": Collections_instance, "search": search, 'Authors': sorted(set(authors)),
                               'Categories': sorted(set(categories))})
    else:  # if not log in, repeat the steps above
        if author:
            if category:
                # filter books searched by title and sort the filter result by popularity and rating
                search_result_instance1 = models.Book.objects.filter(BkTitle__icontains=search).filter(
                    BkAuthor=author).filter(Category=category).order_by('-Popularity', '-Rating')
                if search_result_instance1.exists():
                    for i in search_result_instance1:
                        # check if its rating higher than our filter rating parameter
                        rating_list = models.Rating.objects.filter(book_id=i.BkId)
                        count = 0
                        score_stars = 0
                        for j in rating_list:
                            count += 1
                            score_stars += j.rating_stars
                        if count:
                            if score_stars / count >= int(rating_score):
                                books_list.append(i)
                                authors.append(i.BkAuthor)
                                categories.append(i.Category)
                        else:
                            if rating_score == 0:
                                books_list.append(i)
                                authors.append(i.BkAuthor)
                                categories.append(i.Category)
                # filter books searched by author name and sort the filter result by popularity and rating
                search_result_instance2 = models.Book.objects.filter(BkAuthor__icontains=search).filter(
                    BkAuthor=author).filter(Category=category).order_by('-Popularity', '-Rating')
                if search_result_instance2.exists():
                    for i in search_result_instance2:
                        # check if its rating higher than our filter rating parameter
                        rating_list = models.Rating.objects.filter(book_id=i.BkId)
                        count = 0
                        score_stars = 0
                        for j in rating_list:
                            count += 1
                            score_stars += j.rating_stars
                        if count:
                            if score_stars / count >= int(rating_score):
                                if i not in books_list:
                                    author_book.append(i)
                                    authors.append(i.BkAuthor)
                                    categories.append(i.Category)
                        else:
                            if rating_score == 0:
                                if i not in books_list:
                                    author_book.append(i)
                                    authors.append(i.BkAuthor)
                                    categories.append(i.Category)
                search_result_instance['Book'] = books_list
                search_result_instance['Author'] = author_book
                search_result_instance['User'] = []
                return render(request, 'login/search.html', {"search_result_instance": search_result_instance,
                                                             'search': search, 'Authors': sorted(set(authors)),
                                                             'Categories': sorted(set(categories)), 'nouser': 1})
            else:
                # filter books searched by title with author and sort the filter result by popularity and rating
                search_result_instance1 = models.Book.objects.filter(BkTitle__icontains=search).filter(
                    BkAuthor=author).order_by('-Popularity', '-Rating')
                if search_result_instance1.exists():
                    for i in search_result_instance1:
                        rating_list = models.Rating.objects.filter(book_id=i.BkId)
                        count = 0
                        score_stars = 0
                        for j in rating_list:
                            count += 1
                            score_stars += j.rating_stars
                        if count:
                            if score_stars / count >= int(rating_score):
                                books_list.append(i)
                                categories.append(i.Category)
                                authors.append(i.BkAuthor)
                        else:
                            if rating_score == 0:
                                books_list.append(i)
                                categories.append(i.Category)
                                authors.append(i.BkAuthor)
                # filter books searched by author name with author and sort the filter result by popularity and rating
                search_result_instance2 = models.Book.objects.filter(BkAuthor__icontains=search).filter(
                    BkAuthor=author).order_by('-Popularity', '-Rating')
                if search_result_instance2.exists():
                    for i in search_result_instance2:
                        rating_list = models.Rating.objects.filter(book_id=i.BkId)
                        count = 0
                        score_stars = 0
                        for j in rating_list:
                            count += 1
                            score_stars += j.rating_stars
                        if count:
                            if score_stars / count >= int(rating_score):
                                if i not in books_list:
                                    author_book.append(i)
                                    categories.append(i.Category)
                                    authors.append(i.BkAuthor)
                        else:
                            if rating_score == 0:
                                if i not in books_list:
                                    author_book.append(i)
                                    categories.append(i.Category)
                                    authors.append(i.BkAuthor)
                search_result_instance['Book'] = books_list
                search_result_instance['Author'] = author_book
                search_result_instance['User'] = []
                return render(request, 'login/search.html',
                              {"search_result_instance": search_result_instance, "search": search,
                               'Authors': sorted(set(authors)), 'Categories': sorted(set(categories)), 'nouser': 1})
        else:
            if category:
                # filter books searched by title with category and sort the filter result by popularity and rating
                search_result_instance1 = models.Book.objects.filter(BkTitle__icontains=search).filter(
                    Category=category).order_by('-Popularity', '-Rating')
                if search_result_instance1.exists():
                    for i in search_result_instance1:
                        rating_list = models.Rating.objects.filter(book_id=i.BkId)
                        count = 0
                        score_stars = 0
                        for j in rating_list:
                            count += 1
                            score_stars += j.rating_stars
                        if count:
                            if score_stars / count >= int(rating_score):
                                books_list.append(i)
                                authors.append(i.BkAuthor)
                                categories.append(i.Category)
                        else:
                            if rating_score == 0:
                                books_list.append(i)
                                authors.append(i.BkAuthor)
                                categories.append(i.Category)
                # filter books searched by author name with category and sort the filter result by popularity and rating
                search_result_instance2 = models.Book.objects.filter(BkAuthor__icontains=search).filter(
                    Category=category).order_by('-Popularity', '-Rating')
                if search_result_instance2.exists():
                    for i in search_result_instance2:
                        rating_list = models.Rating.objects.filter(book_id=i.BkId)
                        count = 0
                        score_stars = 0
                        for j in rating_list:
                            count += 1
                            score_stars += j.rating_stars
                        if count:
                            if score_stars / count >= int(rating_score):
                                if i not in books_list:
                                    author_book.append(i)
                                    authors.append(i.BkAuthor)
                                    categories.append(i.Category)
                        else:
                            if rating_score == 0:
                                if i not in books_list:
                                    author_book.append(i)
                                    authors.append(i.BkAuthor)
                                    categories.append(i.Category)
                search_result_instance['Book'] = books_list
                search_result_instance['Author'] = author_book
                search_result_instance['User'] = []
                return render(request, 'login/search.html',
                              {"search_result_instance": search_result_instance, "search": search,
                               'Authors': sorted(set(authors)), 'Categories': sorted(set(categories)), 'nouser': 1})
            else:
                # filter books searched by title with rating score and sort the filter result by popularity and rating
                search_result_instance1 = models.Book.objects.filter(
                    BkTitle__icontains=search).order_by('-Popularity', '-Rating')
                if search_result_instance1.exists():
                    for i in search_result_instance1:
                        rating_list = models.Rating.objects.filter(book_id=i.BkId)
                        count = 0
                        score_stars = 0
                        for j in rating_list:
                            count += 1
                            score_stars += j.rating_stars
                        if count:
                            if score_stars / count >= int(rating_score):
                                books_list.append(i)
                                authors.append(i.BkAuthor)
                                categories.append(i.Category)
                        else:
                            if rating_score == 0:
                                books_list.append(i)
                                authors.append(i.BkAuthor)
                                categories.append(i.Category)
                # filter books searched by authorname with rating and sort the filter result by popularity and rating
                search_result_instance2 = models.Book.objects.filter(
                    BkAuthor__icontains=search).order_by('-Popularity', '-Rating')
                if search_result_instance2.exists():
                    for i in search_result_instance2:
                        rating_list = models.Rating.objects.filter(book_id=i.BkId)
                        count = 0
                        score_stars = 0
                        for j in rating_list:
                            count += 1
                            score_stars += j.rating_stars
                        if count:
                            if score_stars / count >= int(rating_score):
                                if i not in books_list:
                                    author_book.append(i)
                                    authors.append(i.BkAuthor)
                                    categories.append(i.Category)
                        else:
                            if rating_score == 0:
                                if i not in books_list:
                                    author_book.append(i)
                                    authors.append(i.BkAuthor)
                                    categories.append(i.Category)
                search_result_instance['Book'] = books_list
                search_result_instance['Author'] = author_book
                search_result_instance['User'] = []
                return render(request, 'login/search.html',
                              {"search_result_instance": search_result_instance, "search": search,
                               'Authors': sorted(set(authors)), 'Categories': sorted(set(categories)), 'nouser': 1})


def goals(request):
    username = request.session['username']  # get the username from session
    user_instance = models.User.objects.get(UserName=username)  # get the user information
    # get the date with format "year-month"
    date = str(datetime.datetime.now()).split('-')[0] + "-" + str(datetime.datetime.now()).split('-')[1]
    goal = models.Goals.objects.filter(user_id=user_instance.UserId).filter(create_time=date)
    # check if user set a goal before
    if goal:
        goal[0].goal = int(request.POST['days'])
        goal[0].save()
    else:
        Goal = models.Goals()
        Goal.user_id = user_instance.UserId
        Goal.create_time = date
        Goal.goal = int(request.POST['days'])
        Goal.save()
    # reload the profile page
    return HttpResponseRedirect('profile/')


def goal_detail(request):
    username = request.session['username']  # get the username from session
    user_instance = models.User.objects.get(UserName=username)  # get user information
    # get the current date with format "year-month"
    date = str(datetime.datetime.now()).split('-')[0] + "-" + str(datetime.datetime.now()).split('-')[1]
    # check this month how many books were read by checking the first rating date of the book
    num_rating = models.Rating.objects.filter(user_id=user_instance.UserId).filter(
        first_rate=date)
    books_finished = []
    for i in num_rating:
        # get the list of books rated at this month
        books = models.CoBk.objects.filter(Userid_id=i.user_id).filter(BkId_id=i.book_id)
        # make sure user has added this book to his collection
        if books.exists():
            books_finished.append(models.Book.objects.get(BkId=i.book_id))
    return render(request, 'login/codetail.html', {'username':username, 'all': books_finished, "Rated": 1})


def goal_history(request):
    username = request.session['username']  # get username from session
    user_instance = models.User.objects.get(UserName=username)  # get the user information
    goals = models.Goals.objects.filter(user_id=user_instance.UserId)  # get user's historical goals
    history = {}
    for i in goals:
        num = 0
        data = []
        # by checking the first date we rate book to get how  many books we read at the previous months
        num_rating = models.Rating.objects.filter(user_id=user_instance.UserId).filter(first_rate=i.create_time)
        for j in num_rating:
            books = models.CoBk.objects.filter(Userid_id=j.user_id).filter(BkId_id=j.book_id)
            # make sure user has added this book to his collection
            if books.exists():
                num += 1
        # check the status of completeness
        if len(num_rating) >= int(i.goal):
            data.append(i.goal)
            data.append(num)
            data.append('completed')
            history[i.create_time] = data
        else:
            data.append(i.goal)
            data.append(num)
            data.append('not completed')
            history[i.create_time] = data
    return render(request, 'login/goal_history.html', {'username': username, 'history': history})

