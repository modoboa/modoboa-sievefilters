modoboa-sievefilters
====================

|gha| |codecov|

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
      'modoboa.parameters',
      # Extensions here
      # ...
      'modoboa_sievefilters',
    )

Run the following commands to setup the database tables::

  $ cd <modoboa_instance_dir>
  $ python manage.py collectstatic
  $ python manage.py load_initial_data
    
Finally, restart the python process running modoboa (uwsgi, gunicorn,
apache, whatever).

.. |gha| image:: https://github.com/modoboa/modoboa-postfix-sievefilters/actions/workflows/plugin.yml/badge.svg
   :target: https://github.com/modoboa/modoboa-postfix-sievefilters/actions/workflows/plugin.yml

.. |codecov| image:: https://codecov.io/gh/modoboa/modoboa-sievefilters/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/modoboa/modoboa-sievefilters
