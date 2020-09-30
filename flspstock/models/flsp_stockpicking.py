from odoo import fields, models, api


class flspstockpicking2(models.Model):
    _inherit = 'stock.picking'
    _check_company_auto = True

    flsp_packingdesc = fields.Text(string="Packing Description")
    flsp_confirmed_date = fields.Date(string="Confirmed Delivery", readonly=True)
    flsp_confirmed_by = fields.Many2one('res.users', string="Confirmed by", readonly=True)

    def button_flsp_delivery(self):
        view_id = self.env.ref('flspstock.flsp_delivery_wizard_form_view').id
        name = 'Confirm Delivery Date'
        carrier = self.carrier_id
        return {
            'name': name,
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'flspstock.deliverywizard',
            'view_id': view_id,
            'views': [(view_id, 'form')],
            'target': 'new',
            'context': {
                'default_stock_picking_id': self.id,
            }
        }
