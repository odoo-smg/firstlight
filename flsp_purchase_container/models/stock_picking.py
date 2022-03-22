from odoo import fields, models, api


class Picking(models.Model):
    _inherit = 'stock.picking'
    _check_company_auto = True

    flsp_container_id = fields.Many2one('flsp.purchase.container', 'Container', compute='_container')

    def _container(self):
        for picking in self:
            if picking.flsp_purchase_id:
                receipts = self.env['flsp.purchase.container.line'].search([('picking_id', '=', picking.id)])
                if receipts:
                    for each in receipts:
                        picking.flsp_container_id = each.container_id
                else:
                    picking.flsp_container_id = False
            else:
                picking.flsp_container_id = False

    def flsp_container_wizard(self):
        action = self.env.ref('flsp_purchase_container.launch_flsp_purchase_container_stock_picking_wiz').read()[0]
        return action

    @api.depends('has_tracking', 'picking_type_id.use_create_lots', 'picking_type_id.use_existing_lots', 'picking_type_id.show_reserved', 'picking_type_id.show_operations', 'flsp_container_id')
    def _compute_display_assign_serial(self):
        super("Picking")._compute_display_assign_serial(values)
        for move in self:
            if self.flsp_container_id:
                move.display_assign_serial = False
                move.show_operations = False