============================
Analytic Account Responsible
============================

This module adds a **responsible** person to each analytic account and copies
it to the analytic items, so that invoicing and costs can be grouped and
filtered by person in the analytic reporting (list, pivot and graph views).

* *Responsible* field on the analytic account, with change tracking in the
  chatter.
* *Set Manually* flag, checked automatically when the responsible is changed by
  hand, so that the automated actions never overwrite a manual assignment.
* *Account Responsible* stored on the analytic items. It always shows the
  current responsible of the account: changing it moves all the account's
  items, including those of previous years.
* Filters *My Analytic Accounts*, *Without Responsible* and *From My Analytic
  Accounts*, and grouping by responsible.
* Two automated actions, created **inactive**, to fill the responsible from the
  project manager or from the salesperson of the confirmed sale order.

The module does not depend on Project or Sales: each automated action is only
created when its model is installed, also when that module is installed later.

**Table of contents**

.. contents::
   :local:

Configuration
=============

Nothing is filled in on installation: existing analytic accounts stay without
responsible until one is assigned by hand or an automated action is activated.

To fill the responsible automatically, go to *Settings > Technical > Automation
> Automated Actions*, and activate the one that fits your company (usually only
one):

* **Analytic account responsible: copy project manager** (requires Project).
  When a project is created, or its project manager or analytic account
  changes, the project manager is written on its analytic account. If several
  projects share an account, the last modified one wins.
* **Analytic account responsible: copy salesperson of confirmed order**
  (requires Sales). When a sale order is confirmed, its salesperson is written
  on its analytic account, only if the account has no responsible yet. The
  first confirmed order wins.

Both skip the accounts marked as *Set Manually*. Their condition and code can be
edited from the same screen. If an automated action is deleted, it is created
again, inactive, on the next server start.

The automated actions only react to changes. To fill the existing accounts once,
run a server action on the projects (archived ones included) with the same code
as the automated action.

Usage
=====

On the analytic account form, set the *Responsible*. The *Set Manually* box is
checked automatically; uncheck it to give control back to the automated actions.
Clearing the responsible by hand also unchecks it.

To see the invoiced amount per responsible:

#. Go to *Invoicing > Accounting > Management > Analytic Items* (requires the
   accounting features to be shown).
#. Switch to the pivot view.
#. Group the rows by *Account Responsible*, filter the customer invoices of
   the year and use the *Amount* measure.

The *From My Analytic Accounts* filter shows the items of the accounts where the
current user is the responsible.
