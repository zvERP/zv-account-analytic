import logging

from odoo import api, fields, models

from ..hooks import AUTO_CTX, _ensure_automations

_logger = logging.getLogger(__name__)


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    responsible_id = fields.Many2one(
        comodel_name="res.users",
        string="Responsible",
        tracking=True,
        index=True,
        copy=True,
        domain=[("share", "=", False)],
        help="Person responsible for this analytic account. It is copied to "
        "its analytic items so that they can be grouped by responsible.",
    )
    responsible_manual = fields.Boolean(
        string="Set Manually",
        copy=False,
        default=False,
        help="Checked automatically when the responsible is changed by hand. "
        "While it is checked, the automated actions of this module do not "
        "change the responsible. Uncheck it to give control back to them.",
    )

    @api.onchange("responsible_id")
    def _onchange_responsible_id(self):
        # Show the user right away that the change will be kept as manual.
        self.responsible_manual = bool(self.responsible_id)

    def _mark_manual(self, vals):
        if (
            "responsible_id" in vals
            and "responsible_manual" not in vals
            and not self.env.context.get(AUTO_CTX)
        ):
            vals["responsible_manual"] = bool(vals["responsible_id"])
        return vals

    @api.model_create_multi
    def create(self, vals_list):
        return super().create([self._mark_manual(dict(v)) for v in vals_list])

    def write(self, vals):
        return super().write(self._mark_manual(dict(vals)))

    def copy_data(self, default=None):
        # The copy keeps the responsible but not the manual flag.
        default = dict(default or {})
        default.setdefault("responsible_manual", False)
        return super().copy_data(default)

    def _register_hook(self):
        res = super()._register_hook()
        # Create the automations whose model was installed after this module.
        try:
            with self.env.cr.savepoint():
                _ensure_automations(self.env)
        except Exception:
            _logger.exception("Could not create the analytic responsible automations")
        return res
