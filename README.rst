Service Book
============

Small dashboard that lists all QA projects, and displays their swagger
documentation and everything we have about them.


Running locally
---------------

Create a local virtualenv, install requirements, initialize the DB
then run the service::

    $ virtualenv .
    $ bin/pip install -r requirements.txt
    $ bin/python setup.py develop
    $ bin/servicebook-import
    $ bin/servicebook




Running with Docker
-------------------

You can run the app using the provided Dockerfile, by building the docker
image, then running it. It will bind the app to your 5000 port::

    $ make docker-build
    $ make docker-run




