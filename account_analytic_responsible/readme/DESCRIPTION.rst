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
