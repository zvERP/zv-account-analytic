import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

MODULE = "account_analytic_responsible"

# Context key used by the automated actions when they write the responsible,
# so that the write is not taken as a manual assignment.
AUTO_CTX = "analytic_responsible_auto"

CODE_FROM_PROJECT = """\
# Copy the project manager to the analytic account of the project.
# Accounts whose responsible was set manually are left untouched.
for project in records:
    account = project.analytic_account_id
    if (
        account
        and not account.responsible_manual
        and account.responsible_id != project.user_id
    ):
        account.sudo().with_context(analytic_responsible_auto=True).write(
            {"responsible_id": project.user_id.id}
        )
"""

CODE_FROM_SALE_ORDER = """\
# Copy the salesperson of the confirmed order to its analytic account,
# only when the account has no responsible yet and was not set manually.
for order in records:
    account = order.analytic_account_id
    if account and not account.responsible_manual and not account.responsible_id:
        account.sudo().with_context(analytic_responsible_auto=True).write(
            {"responsible_id": order.user_id.id}
        )
"""

AUTOMATIONS = [
    {
        "xml_name": "automation_from_project",
        "model": "project.project",
        "name": "Analytic account responsible: copy project manager",
        "name_es": (
            "Responsable de cuenta analítica: copiar responsable del proyecto"
        ),
        "trigger": "on_create_or_write",
        "trigger_fields": ["user_id", "analytic_account_id"],
        "filter_pre_domain": False,
        "filter_domain": "[('analytic_account_id', '!=', False)]",
        "code": CODE_FROM_PROJECT,
    },
    {
        "xml_name": "automation_from_sale_order",
        "model": "sale.order",
        "name": "Analytic account responsible: copy salesperson of confirmed order",
        "name_es": (
            "Responsable de cuenta analítica: "
            "copiar comercial del pedido confirmado"
        ),
        "trigger": "on_write",
        "trigger_fields": ["state"],
        "filter_pre_domain": "[('state', '!=', 'sale')]",
        "filter_domain": (
            "[('state', '=', 'sale'), ('analytic_account_id', '!=', False)]"
        ),
        "code": CODE_FROM_SALE_ORDER,
    },
]


def _ensure_automations(env, definitions=None):
    """Create the (inactive) automated actions whose model is installed.

    Idempotent: an automation whose XML id already exists is skipped, so it
    is cheap to call on every registry load. Returns the created records.
    """
    created = env["base.automation"]
    for definition in definitions if definitions is not None else AUTOMATIONS:
        xml_id = "%s.%s" % (MODULE, definition["xml_name"])
        if definition["model"] not in env:
            continue
        if env.ref(xml_id, raise_if_not_found=False):
            continue
        model = env["ir.model"]._get(definition["model"])
        trigger_fields = env["ir.model.fields"].search(
            [
                ("model_id", "=", model.id),
                ("name", "in", definition["trigger_fields"]),
            ]
        )
        values = {
            "name": definition["name"],
            "model_id": model.id,
            "trigger": definition["trigger"],
            "trigger_field_ids": [(6, 0, trigger_fields.ids)],
            "filter_pre_domain": definition["filter_pre_domain"],
            "filter_domain": definition["filter_domain"],
            "state": "code",
            "code": definition["code"],
            "active": False,
        }
        automation = env["base.automation"]._load_records(
            [{"xml_id": xml_id, "values": values, "noupdate": True}]
        )
        _set_spanish_name(env, automation, definition)
        _logger.info("Created inactive automated action %s", xml_id)
        created |= automation
    return created


def _set_spanish_name(env, automation, definition):
    if not definition.get("name_es"):
        return
    langs = [
        code for code, _name in env["res.lang"].get_installed() if code[:2] == "es"
    ]
    if langs:
        automation.action_server_id.update_field_translations(
            "name", {lang: definition["name_es"] for lang in langs}
        )


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _ensure_automations(env)
