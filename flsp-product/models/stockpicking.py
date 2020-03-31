from odoo import fields, models, api


class flspstockpicking(models.Model):
    _inherit = 'stock.picking'
    _check_company_auto = True

    flsp_allow_validate = fields.Boolean(string="Allow Validate Button", compute='_allow_validate')
    product_id = fields.Many2one('product.product', 'Product', related='move_lines.product_id', domain="['&',['flsp_allow_validate','=',True],['type','in',['product','consu']],'|',['company_id','=',False],['company_id','=',company_id]]", readonly=False)

    def _allow_validate(self):
        for picking in self:
            picking.flsp_allow_validate = not(any(m.product_id.flsp_acc_valid == False for m in picking.move_lines))

    #def _compute_has_tracking(self):
        #for picking in self:
            #picking.has_tracking = any(m.has_tracking != 'none' for m in picking.move_lines)
