from odoo.tests import tagged
from odoo.tests.common import TransactionCase

from odoo.addons.account_analytic_responsible.hooks import (
    AUTO_CTX,
    AUTOMATIONS,
    MODULE,
    _ensure_automations,
)

XMLID_PROJECT = "%s.automation_from_project" % MODULE
XMLID_SALE = "%s.automation_from_sale_order" % MODULE


@tagged("post_install", "-at_install")
class TestResponsible(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.plan = cls.env["account.analytic.plan"].create({"name": "Test plan"})
        cls.account = cls.env["account.analytic.account"].create(
            {"name": "Test account", "plan_id": cls.plan.id}
        )
        users = cls.env["res.users"].with_context(no_reset_password=True)
        cls.user_a = users.create({"name": "Responsible A", "login": "aar_user_a"})
        cls.user_b = users.create({"name": "Responsible B", "login": "aar_user_b"})

    def _module_automations(self):
        imd = self.env["ir.model.data"].search(
            [("module", "=", MODULE), ("model", "=", "base.automation")]
        )
        return self.env["base.automation"].with_context(active_test=False).browse(
            imd.mapped("res_id")
        )

    # 1
    def test_manual_assignment_marks_manual(self):
        self.account.responsible_id = self.user_a
        self.assertTrue(self.account.responsible_manual)

        account = self.env["account.analytic.account"].create(
            {
                "name": "Created with responsible",
                "plan_id": self.plan.id,
                "responsible_id": self.user_b.id,
            }
        )
        self.assertTrue(account.responsible_manual)

    def test_change_is_tracked(self):
        # Finish the creation tracking first, as if it had been committed
        self.env.flush_all()
        self.env.cr.precommit.run()
        self.account.responsible_id = self.user_a
        self.env.flush_all()
        self.env.cr.precommit.run()
        tracking = self.env["mail.tracking.value"].search(
            [
                ("mail_message_id.model", "=", "account.analytic.account"),
                ("mail_message_id.res_id", "=", self.account.id),
                ("field.name", "=", "responsible_id"),
            ]
        )
        self.assertEqual(tracking.new_value_integer, self.user_a.id)

    # 2
    def test_manual_clear_unmarks_manual(self):
        self.account.responsible_id = self.user_a
        self.account.responsible_id = False
        self.assertFalse(self.account.responsible_manual)

    # 3
    def test_auto_context_does_not_mark_manual(self):
        self.account.with_context(**{AUTO_CTX: True}).responsible_id = self.user_a
        self.assertEqual(self.account.responsible_id, self.user_a)
        self.assertFalse(self.account.responsible_manual)

    def test_explicit_manual_value_is_respected(self):
        self.account.write({"responsible_id": self.user_a.id, "responsible_manual": False})
        self.assertFalse(self.account.responsible_manual)

    # 4
    def test_analytic_lines_follow_account(self):
        line = self.env["account.analytic.line"].create(
            {"name": "Line", "account_id": self.account.id, "amount": 100.0}
        )
        self.assertFalse(line.analytic_responsible_id)
        self.account.responsible_id = self.user_a
        self.assertEqual(line.analytic_responsible_id, self.user_a)
        self.account.responsible_id = self.user_b
        self.assertEqual(line.analytic_responsible_id, self.user_b)
        lines = self.env["account.analytic.line"].search(
            [("analytic_responsible_id", "=", self.user_b.id)]
        )
        self.assertIn(line, lines)
        groups = self.env["account.analytic.line"].read_group(
            [("account_id", "=", self.account.id)],
            ["amount:sum"],
            ["analytic_responsible_id"],
        )
        self.assertEqual(groups[0]["analytic_responsible_id"][0], self.user_b.id)
        self.assertEqual(groups[0]["amount"], 100.0)

    # 5
    def test_no_automation_without_model(self):
        definitions = [dict(AUTOMATIONS[0], xml_name="automation_missing", model="x.missing.model")]
        self.assertFalse(_ensure_automations(self.env, definitions))
        self.assertFalse(self.env.ref("%s.automation_missing" % MODULE, raise_if_not_found=False))
        for definition in AUTOMATIONS:
            if definition["model"] not in self.env:
                self.assertFalse(
                    self.env.ref("%s.%s" % (MODULE, definition["xml_name"]), raise_if_not_found=False)
                )

    # 6
    def test_automation_project_exists_inactive(self):
        if "project.project" not in self.env:
            self.skipTest("project is not installed")
        automation = self.env.ref(XMLID_PROJECT)
        self.assertFalse(automation.active)
        self.assertEqual(automation.model_id.model, "project.project")
        self.assertEqual(automation.trigger, "on_create_or_write")

    def test_automation_sale_exists_inactive(self):
        if "sale.order" not in self.env:
            self.skipTest("sale is not installed")
        automation = self.env.ref(XMLID_SALE)
        self.assertFalse(automation.active)
        self.assertEqual(automation.model_id.model, "sale.order")
        self.assertEqual(automation.trigger, "on_write")

    # 7
    def test_ensure_automations_idempotent(self):
        before = self._module_automations()
        _ensure_automations(self.env)
        _ensure_automations(self.env)
        self.assertEqual(self._module_automations(), before)

    def test_deleted_automation_is_recreated(self):
        before = self._module_automations()
        if not before:
            self.skipTest("neither project nor sale is installed")
        before[0].unlink()
        created = _ensure_automations(self.env)
        self.assertEqual(len(created), 1)
        self.assertFalse(created.active)
        self.assertEqual(len(self._module_automations()), len(before))

    # 8
    def test_automation_from_project(self):
        if "project.project" not in self.env:
            self.skipTest("project is not installed")
        self.env.ref(XMLID_PROJECT).active = True
        project = self.env["project.project"].create(
            {
                "name": "Project",
                "analytic_account_id": self.account.id,
                "user_id": self.user_a.id,
            }
        )
        self.assertEqual(self.account.responsible_id, self.user_a)
        self.assertFalse(self.account.responsible_manual)

        project.user_id = self.user_b
        self.assertEqual(self.account.responsible_id, self.user_b)
        self.assertFalse(self.account.responsible_manual)

        # A manual assignment is not overwritten any more
        self.account.responsible_id = self.user_a
        self.assertTrue(self.account.responsible_manual)
        project.user_id = self.user_b
        self.assertEqual(self.account.responsible_id, self.user_a)

        # Unchecking the flag gives control back to the automation
        self.account.responsible_manual = False
        project.user_id = self.env.user
        self.assertEqual(self.account.responsible_id, self.env.user)

    def test_automation_from_project_inactive(self):
        if "project.project" not in self.env:
            self.skipTest("project is not installed")
        self.env["project.project"].create(
            {
                "name": "Project",
                "analytic_account_id": self.account.id,
                "user_id": self.user_a.id,
            }
        )
        self.assertFalse(self.account.responsible_id)

    # 9
    def _create_order(self, account, user):
        product = self.env["product.product"].create(
            {"name": "Service", "type": "service", "list_price": 100.0}
        )
        partner = self.env["res.partner"].create({"name": "Customer"})
        return self.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "user_id": user.id,
                "analytic_account_id": account.id,
                "order_line": [(0, 0, {"product_id": product.id, "product_uom_qty": 1})],
            }
        )

    def test_automation_from_sale_order(self):
        if "sale.order" not in self.env:
            self.skipTest("sale is not installed")
        self.env.ref(XMLID_SALE).active = True

        order = self._create_order(self.account, self.user_a)
        self.assertFalse(self.account.responsible_id)
        order.action_confirm()
        self.assertEqual(self.account.responsible_id, self.user_a)
        self.assertFalse(self.account.responsible_manual)

        # The account already has a responsible: a second order does not change it
        order_2 = self._create_order(self.account, self.user_b)
        order_2.action_confirm()
        self.assertEqual(self.account.responsible_id, self.user_a)

    def test_automation_from_sale_order_manual(self):
        if "sale.order" not in self.env:
            self.skipTest("sale is not installed")
        self.env.ref(XMLID_SALE).active = True
        # Manually set without responsible cannot happen through the UI, but
        # the automation must respect the flag anyway.
        self.account.write({"responsible_id": False, "responsible_manual": True})
        order = self._create_order(self.account, self.user_b)
        order.action_confirm()
        self.assertFalse(self.account.responsible_id)

    # 10
    def test_copy_keeps_responsible_not_manual(self):
        self.account.responsible_id = self.user_a
        self.assertTrue(self.account.responsible_manual)
        copy = self.account.copy()
        self.assertEqual(copy.responsible_id, self.user_a)
        self.assertFalse(copy.responsible_manual)
