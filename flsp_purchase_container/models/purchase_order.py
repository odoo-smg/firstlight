from odoo import fields, models, api


class FLSPPurchaseContainerPO(models.Model):
    _inherit = 'purchase.order'
    _check_company_auto = True

    def action_view_picking(self):
        res = super(FLSPPurchaseContainerPO, self).action_view_picking()
        res['context']['search_default_draft'] = 1
        res['context']['search_default_waiting'] = 1
        res['context']['search_default_available'] = 1
        return res
