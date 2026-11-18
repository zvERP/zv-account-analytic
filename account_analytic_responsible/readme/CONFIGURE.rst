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
