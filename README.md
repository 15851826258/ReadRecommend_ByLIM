# COMP3900/9900 2020T2 Group Project 
Group Name: LIM

# Backend README.md
## Purpose of this file
To intruct user how to set up the project


## Backend source code navigation

```bash

frontend:
   COMP9900_LIM:      # The main code folder
    > templates
        - models.py   # All database configuration
        - views.py    # All backend codes

```


## Requirements
`Python3` is required in order to run the front end of this project

If you don't have `Python3` installed on your computer you can download and istall it on the official website at: `https://www.python.org/downloads/`

`MySQL` is required in order to use the database features of this project

If you don't have `MySQL` installed on your computer you can download and istall it on the official website at: `https://dev.mysql.com/downloads/mysql/`



# Frontend README.md
## Purpose of this file
To intruct user how to set up the frontend of this web site and how to access it with browsers

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

If you don't have `Python3` installed on your computer you can download and istall it on the official website at: `https://www.python.org/downloads/`

`MySQL` is required in order to use the database features of this project

If you don't have `MySQL` installed on your computer you can download and istall it on the official website at: `https://dev.mysql.com/downloads/mysql/`

## Uasge
### Run the server locally
To start the frontend server locally, open your terminal and get into the directory of this project

Then run the follwing command:

```bash
$ python manage.py runserver 8080
```

A front end server will start on your mechine on port 8080

#### `Reminder: Do not close the terminal untill you are done useing the website`

### Access the website using browsers (e.g. Chrome)

Open your browser and type in the domain name  `http://127.0.0.1:8080/index/ then you will land on the home page of the website!

Enjoy!




