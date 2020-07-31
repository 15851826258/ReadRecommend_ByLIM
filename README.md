# COMP3900/9900 2020T2 Group Project 
Group Name: LIM

# Backend README.md
## Purpose of this file
To introduce user how to set up the project


## Backend source code navigation

```bash

   COMP990:            # the django configuration folder
        - settings.py  # the setting file contains the database login informaton
   COMP9900_LIM:       # The main code folder
        - models.py    # All database configuration
        - views.py     # All backend view functions

```


## Requirements
`Python3` is required in order to run the front end of this project

If you don't have `Python3` installed on your computer you can download and install it on the official website at: `https://www.python.org/downloads/`

`MySQL` is required in order to use the database features of this project

If you don't have `MySQL` installed on your computer you can download and install it on the official website at: `https://dev.mysql.com/downloads/mysql/`

The Django and pymysql should bu installed before the test


# Frontend README.md
## Purpose of this file
To introduce user how to set up the frontend of this web site and how to access it with browsers

## Frontend source code navigation

```bash

frontend:
   COMP9900_LIM:      # The main code folder
    > static          
        > imgs        # All imges
        > js          # All Js & JQuery files
        > login       # All css files
    > templates          
        > login       # All html files

```


## Requirements
`Python3` is required in order to run the front end of this project

If you don't have `Python3` installed on your computer you can download and install it on the official website at: `https://www.python.org/downloads/`

`MySQL` is required in order to use the database features of this project

If you don't have `MySQL` installed on your computer you can download and install it on the official website at: `https://dev.mysql.com/downloads/mysql/`

## Uasge
### Run the server locally
To start the frontend server locally, open your pycharm and get into the directory of this project

You need to change the setting of Django in `preferences/Languages&Frameworks/Django`:

by select `Enable Django Support` and fill the `Django project root`, `Settings` and `Manage script` with the location of the project, setting.py and manage.py.
And set the "Folder pattern to track files" with "migrations" 

Then change the database login information in `COMP9900/setting.py` and you also need to migrate the models into your database, by running `Tools/Run manage.py Task...` and command `makemigrations COMP9900_LIM`, `sqlmigrate COMP9900_LIM 0001` and `migrate` in turn.

And open the `Run/Edit Configurations` to set the `Run browser` to "127.0.0.1:8000/" and set the `Working directory` to the location of this project and then you can run the django server

A front end server will start on your machine on "127.0.0.1:8000"

### Access the website using browsers (e.g. Chrome)

Open your browser and type in the domain name  `http://127.0.0.1:8000/` then you will land on the home page of the website!

Enjoy!




