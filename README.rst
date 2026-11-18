===================
zv-account-analytic
===================

.. |badge1| image:: https://img.shields.io/badge/runboat-Try%20me-875A7B.png
    :target: https://runboat.zverp.com/webui/builds.html?repo=zvERP/zv-account-analytic
    :alt: Try me on Runboat

|badge1|

Analytic accounting addons for Odoo 16.0.

Available addons
----------------

.. list-table::
   :widths: 35 15 50
   :header-rows: 1

   * - Addon
     - Version
     - Summary
   * - `account_analytic_responsible <account_analytic_responsible/>`_
     - 16.0.1.0.0
     - Responsible person per analytic account and grouping by responsible

Runboat
-------

The repository follows the OCA addons-repository layout used by Runboat
(``setup/`` with one ``setup.py`` per addon and ``setup/_metapackage``).
The Odoo series is taken from the ``16.0`` branch. Regenerate ``setup/``
after adding an addon with::

    setuptools-odoo-make-default -d . -m zverp-account-analytic --clean
