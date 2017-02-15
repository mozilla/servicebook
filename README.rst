Service Book
============

Mozilla Services projects API. Provides a Database of all projects and
a set of API to interact with them.

|travis| |master-coverage|


.. |master-coverage| image::
    https://coveralls.io/repos/mozilla/servicebook/badge.svg?branch=master
    :alt: Coverage
    :target: https://coveralls.io/r/mozilla/servicebook

.. |travis| image:: https://travis-ci.org/mozilla/servicebook.svg?branch=master
    :target: https://travis-ci.org/mozilla/servicebook


Use the Service Book
--------------------

The Service Book provides a RESTFul HTTP API. If you are using Python, you can
use the restjson client: https://github.com/tarekziade/restjson

It provides a simple tool to interact with the Service Book.


Running locally
---------------

The servicebook uses a MySQL database by default, but you can use
SQLITE3 or postgres by tweaking the **sqluri** option in **servicebook.ini**.

Create a local virtualenv, install requirements, initialize the DB
then run the service::

    $ virtualenv .
    $ bin/pip install -r requirements.txt
    $ bin/python setup.py develop
    $ bin/servicebook-import --sqluri mysql+pymysql://book:book@0.0.0.0/book
    $ bin/servicebook

The app runs on the 5001 port by default.


Running with Docker
-------------------

You can run the app using the provided Dockerfile, by building the docker
image, then running it. It will bind the app to your 5001 port::

    $ make docker-build
    $ make docker-run

The Docker image will reach out for the database that's set
**servicebook.ini**.


Key managment
-------------

The application asks for clients to provide a key when they try to
modify the database. Keys are stored in a table in the database.

Each application that whishes to get an access should have its own
API key.

You can list/add/revoke keys using the **servicebook-keys** command::

    $ bin/servicebook-keys --sqluri mysql+pymysql://book:book@0.0.0.0/book list
    No keys!

    $ bin/servicebook-keys --sqluri mysql+pymysql://book:book@0.0.0.0/book add MyApp
    App: MyApp, Key: 399c1365-3700-4ce6-8fd1-f304a32a0794

    $ bin/servicebook-keys --sqluri mysql+pymysql://book:book@0.0.0.0/book add MyApp2
    App: MyApp2, Key: ef2b1158-27ca-4994-a887-c0d531a0749d

    $ bin/servicebook-keys --sqluri mysql+pymysql://book:book@0.0.0.0/book list
    App: MyApp, Key: 399c1365-3700-4ce6-8fd1-f304a32a0794
    App: MyApp2, Key: ef2b1158-27ca-4994-a887-c0d531a0749d

    $ bin/servicebook-keys --sqluri mysql+pymysql://book:book@0.0.0.0/book revoke MyApp
    Key revoked for MyApp

    $ bin/servicebook-keys --sqluri mysql+pymysql://book:book@0.0.0.0/book list
    App: MyApp2, Key: ef2b1158-27ca-4994-a887-c0d531a0749d
