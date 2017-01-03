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

