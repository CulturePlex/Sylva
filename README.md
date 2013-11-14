[![Build Status](https://travis-ci.org/gabmunrio/Sylva.png?branch=master)](https://travis-ci.org/gabmunrio/Sylva)
[![Coverage Status](https://coveralls.io/repos/gabmunrio/Sylva/badge.png?branch=master)](https://coveralls.io/r/gabmunrio/Sylva?branch=master)

Sylva
==========
Sylva_ is a Relaxed-Schema Graph Database Management System.

Installation:
-------------

Just in case, first thing you need is to have installed pip_ and virtualenv_ in your machine::

  $ sudo apt-get install python-pip python-dev build-essential python-profiler libpq-dev
  $ sudo pip install --upgrade pip
  $ sudo pip install --upgrade virtualenv

Then, it's a good option to use virtualenvwrapper_::

  $ sudo pip install virtualenvwrapper

In the instructions given on virtualenvwrapper_, you should to set the working
directory for your virtual environments. So, you could add it in the end of
your .bashrc file (newer versions of virtualenvwrapper don't require this)::

  $ mkdir -p ~/.venvs
  export WORKON_HOME=~/.venvs
  source /usr/local/bin/virtualenvwrapper.sh

And finally, create a virtualenv for the project::

  $ mkvirtualenv sylva --no-site-packages

After you setup your virtual environment, you should be able to enable and
disable it. The system propmt must change where you have it enable::

  $ workon sylva
  $ deactivate

Now, if you didn't get the project yet, clone it in your desired location::

  $ cd $HOME
  $ git clone git@github.com:CulturePlex/sylva.git git/sylva

Enter in the new location and update the virtual environment previously created::

  $ cd git/sylva/
  $ workon sylva
  $ pip install -U -r requirements.txt

Relational Database
-------------------

Now you have installed the Django_ project and almost ready to run it. Before that,
you must create a database. In developing stage, we use SQLite::

  $ cd $HOME
  $ cd sylva/sylva
  $ python manage.py syncdb --noinput
  $ python manage.py migrate
  $ python manage.py createsuperuser

And that is. If you run the project using the standalone development server of
Django_, you could be able to access to the URL http://localhost:8000/::

  $ python manage.py runserver localhost:8000
  $ xdg-open http://localhost:8000/

Graph Database
--------------

The last piece to make Sylva works is the Neo4j_ graph database. You can download
the most current version (1.9.2_ as today). After downloading, we need to unzip
and setup some parameters::

  $ cd git/sylva
  $ wget dist.neo4j.org/neo4j-community-1.9.2-unix.tar.gz
  $ tar -zxvf neo4j-community-1.9.2-unix.tar.gz
  $ mv neo4j-community-1.9.2-unix neo4j

Now, as indicated in `settings.py` in section `GRAPHDATABASES`, you need to edit
the file `neo4j/conf/neo4j-server.properties` and set the next properies (the
default configuration is reserved for testing client libraries)::

  org.neo4j.server.webserver.port=7373
  org.neo4j.server.webadmin.data.uri=/db/sylva/

And then you are ready to run the Neo4j_ server::

  $ ./neo4j/bin/neo4j console

.. _Sylva: http://www.sylvadb.com
.. _Neo4j: http://neo4j.org
.. _1.9.2: http://dist.neo4j.org/neo4j-community-1.9.2-unix.tar.gz
.. _Django: https://www.djangoproject.com/
.. _pip: http://pypi.python.org/pypi/pip
.. _virtualenv: http://pypi.python.org/pypi/virtualenv
.. _virtualenvwrapper: http://www.doughellmann.com/docs/virtualenvwrapper/
