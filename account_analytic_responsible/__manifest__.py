{
    "name": "Analytic Account Responsible",
    "version": "16.0.1.0.0",
    "category": "Accounting/Accounting",
    "summary": "Responsible person per analytic account and grouping by responsible",
    "website": "https://www.zverp.com",
    "depends": ["analytic", "base_automation"],
    "data": [
        "views/account_analytic_account_views.xml",
        "views/account_analytic_line_views.xml",
    ],
    "post_init_hook": "post_init_hook",
    "license": "LGPL-3",
    "installable": True,
    "auto_install": False,
}
