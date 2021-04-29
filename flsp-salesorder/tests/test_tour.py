from odoo.tests.common import HttpCase, tagged

@tagged('flsp', 'flsptour', '-standard')
class TestCustomerBadgeUI(HttpCase):

    def test_badge_create_success(self):
        self.browser_js("/web",
                        "odoo.__DEBUG__.services['web_tour.tour'].run('badge_create_success')",
                        "odoo.__DEBUG__.services['web_tour.tour'].tours.badge_create_success.ready",
                        login="perryhe@smartrendmfg.com",
                        password="testdb")

    def test_badge_create_no_rewardLevel(self):
        self.browser_js("/web",
                        "odoo.__DEBUG__.services['web_tour.tour'].run('badge_create_no_rewardLevel')",
                        "odoo.__DEBUG__.services['web_tour.tour'].tours.badge_create_no_rewardLevel.ready",
                        login="perryhe@smartrendmfg.com",
                        password="testdb")

    def test_badge_manage_for_customer(self):
        self.browser_js("/web",
                        "odoo.__DEBUG__.services['web_tour.tour'].run('badge_manage_for_customer')",
                        "odoo.__DEBUG__.services['web_tour.tour'].tours.badge_manage_for_customer.ready",
                        login="perryhe@smartrendmfg.com",
                        password="testdb")
