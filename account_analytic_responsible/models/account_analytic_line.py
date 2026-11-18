from odoo import fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    analytic_responsible_id = fields.Many2one(
        related="account_id.responsible_id",
        store=True,
        index=True,
        string="Account Responsible",
    )
