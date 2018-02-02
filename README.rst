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

    $ pipenv install --dev
    $ pipenv shell
    $ servicebook-import --sqluri mysql+pymysql://book:book@0.0.0.0/book
    $ servicebook

The app runs on the 5001 port by default.


Running with Docker
-------------------

You can run the app using the provided Dockerfile, by building the docker
image, then running it. It will bind the app to your 5001 port::

    $ make docker-build
    $ make docker-run

The Docker image will reach out for the database that's set
**servicebook.ini**.

Running with external DB
------------------------

If you would like to use an external DB for storage, be sure to set the default
character set for the database to UTF-8 (utf8mr for mysql).


Authentication
--------------

The application can secure the HTTP API access for reads and/or writes.

You can define how anonymous accesses are handled with the
**anonymous_access** variable in the **common** section of the config file.

The value to set is a permission **scope**. Possible values:

- **read**: access to GET and HEAD calls - **default value when non specified**
- **readwrite**: access to PATCH, PUT, POST, DELETE, GET, HEAD
- **admin**: like readwrite - will be used for specific admin tasks

Client can also have a privileged access with an API key.
The key is passed in the Authorization header, prefixed by APIKey::

    Authorization APIKey ZGJkYWI3ZmQtZDEwNy00MzJiLWJlNDgtMjZkNTQyZGFiZDhi

The value is a base64-encoded UUID. Each application that whishes to get a
priviledged access should have its own API key and scope.

You can list/add/revoke keys using the **servicebook-keys** command::

    $ servicebook-keys --sqluri mysql+pymysql://book:book@0.0.0.0/book list
    No keys!

    $ servicebook-keys --sqluri mysql+pymysql://book:book@0.0.0.0/book add MyApp
    App: MyApp, Key: 399c1365-3700-4ce6-8fd1-f304a32a0794, Scope: read

    $ servicebook-keys --sqluri mysql+pymysql://book:book@0.0.0.0/book add MyApp2 --scope readwrite
    App: MyApp2, Key: e87271fd-ca31-46cf-8cc5-48b1f9348e4e, Scope: readwrite

    $ servicebook-keys --sqluri mysql+pymysql://book:book@0.0.0.0/book list
    App: MyApp, Key: 399c1365-3700-4ce6-8fd1-f304a32a0794, Scope: read
    App: MyApp2, Key: e87271fd-ca31-46cf-8cc5-48b1f9348e4e, Scope: readwrite

    $ servicebook-keys --sqluri mysql+pymysql://book:book@0.0.0.0/book revoke MyApp
    Key revoked for MyApp

    $ servicebook-keys --sqluri mysql+pymysql://book:book@0.0.0.0/book list
    App: MyApp2, Key: e87271fd-ca31-46cf-8cc5-48b1f9348e4e, Scope: readwrite


The default setup will make the data read-only and will required a privileged
access with **readwrite** scope for writing in the database.

You should have one separate key per calling service so it's easier to revoke or
renew a specific service access if required.
