modoboa-sievefilters
====================

|landscape|

The sieve filters editor of Modoboa.

Installation
------------

Install this extension system-wide or inside a virtual environment by
running the following command::

  $ pip install modoboa-sievefilters

Edit the settings.py file of your modoboa instance and add
``modoboa_sievefilters`` inside the ``MODOBOA_APPS`` variable like this::

    MODOBOA_APPS = (
      'modoboa',
      'modoboa.core',
      'modoboa.lib',
      'modoboa.admin',
      'modoboa.relaydomains',
      'modoboa.limits',
    
      # Extensions here
      # ...
      'modoboa_sievefilters',
    )

Run the following commands to setup the database tables::

  $ cd <modoboa_instance_dir>
  $ python manage.py load_initial_data
    
Finally, restart the python process running modoboa (uwsgi, gunicorn,
apache, whatever).

.. |landscape| image:: https://landscape.io/github/modoboa/modoboa-sievefilters/master/landscape.svg?style=flat
   :target: https://landscape.io/github/modoboa/modoboa-sievefilters/master
   :alt: Code Health
