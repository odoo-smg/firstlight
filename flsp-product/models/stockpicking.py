from odoo import fields, models, api


class flspstockpicking(models.Model):
    _inherit = 'stock.picking'
    _check_company_auto = True

    flsp_allow_validate = fields.Boolean(string="Allow Validate Button", compute='_allow_validate')

    def _allow_validate(self):
        for picking in self:
            picking.flsp_allow_validate = any(m.flsp_acc_valid == False for m in picking.move_lines)

    #def _compute_has_tracking(self):
        #for picking in self:
            #picking.has_tracking = any(m.has_tracking != 'none' for m in picking.move_lines)        
