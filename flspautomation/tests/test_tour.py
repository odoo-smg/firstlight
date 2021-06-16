from odoo.tests.common import HttpCase, tagged

@tagged('flsp', 'flsp-tour', '-standard')
class TestSalesUI(HttpCase):

    # def test_tour_01(self):
    #     print("perry.............start ")
    #     self.browser_js("/web",
    #         "odoo.__DEBUG__.services['web_tour.tour'].run('it_sale_tour')",
    #         "odoo.__DEBUG__.services['web_tour.tour'].tours.it_sale_tour.ready",
    #         login="perryhe@smartrendmfg.com",
    #         password="testdb")
    #
    #     print("perry.............end")

    def test_flsp_tour_01(self):
        self.browser_js("/web",
                        "odoo.__DEBUG__.services['web_tour.tour'].run('flsp_sale_tour_01')",
                        "odoo.__DEBUG__.services['web_tour.tour'].tours.flsp_sale_tour_01.ready",
                        login="perryhe@smartrendmfg.com",
                        password="hpy4smg11")

    def test_flsp_tour_02(self):
        self.browser_js("/web",
                        "odoo.__DEBUG__.services['web_tour.tour'].run('flsp_sale_tour_02')",
                        "odoo.__DEBUG__.services['web_tour.tour'].tours.flsp_sale_tour_02.ready",
                        login="perryhe@smartrendmfg.com",
                        password="hpy4smg11")
