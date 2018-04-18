# Instructions to Build the App 

For windows, Setting up the development environmnet


0. Download Python from [LINK](https://www.python.org/ftp/python/3.7.0/python-3.7.0b3-amd64-webinstall.exe)
1. Download this file [get_pip.py]([https://bootstrap.pypa.io/get-pip.py)
2. Go to the Download Location and run:
```

> python get_pip.py

```
Refer this doc [link](http://flask.pocoo.org/docs/0.12/installation/#windows-easy-install)

```
> pip install --upgrade pip setuptools
> pip install virtualenv

```

Download the source code in zip format and extract it.

After unzip, move in the folder and create a virtual environment by:

```
> virtualenv venv
> source venv/bin/activate
```

After activation, console will be:

```
(venv)> 
```

Install the packages

```
(venv)> pip install -r requirements.txt

```
Then, start the server


```
(venv)> python manage.py runserver
```

## Database Installation

Download mongoDb from this link for windows. [Download link](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-windows/#interactive-installation)


## Creating Database

Open two Shells:

In one shell, start mongod server

```
> mongod
```

Keep the shell running

In the other shell, start mongo server

```
> mongo

```

In mongo shell, create database dobpm,


```
> show dbs
> use dobpm
```

and create collections,

```
db.createCollection('users')
db.createCollection('profiles')
db.createCollection('orgs')
db.createCollection('creds')


```
