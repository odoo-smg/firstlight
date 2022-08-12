from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare
import logging
_logger = logging.getLogger(__name__)


class flspstockpicking2(models.Model):
    _inherit = 'stock.picking'
    _check_company_auto = True

    flsp_packingdesc = fields.Text(string="Packing Description")
    flsp_confirmed_date = fields.Datetime(string="Confirmed Delivery", readonly=True)
    flsp_confirmed_by = fields.Many2one('res.users', string="Confirmed by", readonly=True)
    flsp_delivery_eta = fields.Date(string="Delivery ETA")
    flsp_customer_received = fields.Date(string="Received by Customer")
    attachment_ids = fields.Many2many('ir.attachment', 'stock_picking_attachment_rel',
                                      string='Attachments/Pictures',
                                      help='Attach pictures here')
    location_id = fields.Many2one('stock.location', 'From', check_company=True, required=True, domain=[('usage', '=', 'internal')])
    location_dest_id = fields.Many2one('stock.location', 'To', check_company=True, required=True, domain=[('usage', '=', 'internal')])

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

    def package_info(self):
        """
            Purpose: To call the packaging info wizard so as to fill the package info and send email
        """
        view_id = self.env.ref('flspstock.package_form_view').id
        name = 'Package Info'
        return {
            'name': name,
            'view_mode': 'form',
            'res_model': 'flspstock.package',
            'view_id': view_id,
            'views': [(view_id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_order_id': self.id,  # getting the default id
            }
        }

    def button_validate(self):
        """
            Purpose:    Check qty before validation
            Note:       Original method is defined in addons\stock\models\stock_picking.py
        """
        self.ensure_one()
        if not self.move_lines and not self.move_line_ids:
            raise UserError(_('Please add some items to move.'))

        # Check qty required with available_qty_in_source_location
        for line in self.move_line_ids:
            qty_to_transfer = line.qty_done
            if not qty_to_transfer:
                qty_to_transfer = line.product_uom_qty

            precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            if float_compare(qty_to_transfer, 0, precision_digits=precision_digits) <= 0:
                raise UserError(_("Please update quantity in 'Done' or 'Reserved' with a number bigger than 0."))

            if line.location_id and line.location_id.active and line.location_id.usage == 'internal':
                # only check available_qty_in_source_location when the location is 'Internal'
                available_qty_in_source_location = self.env['stock.quant'].get_flsp_stock_quantity(line.product_id, line.location_id, line.lot_id, line.package_id)
                if float_compare(available_qty_in_source_location, qty_to_transfer, precision_digits=precision_digits) == -1:
                    raise UserError(
                        _( """There is not enough quantity available in the Source Location.
    %s pieces of %s are remaining in location %s, but you want to transfer %s pieces.
    Please adjust your quantities or correct your stock with an inventory adjustment."""
                        )
                        % (available_qty_in_source_location, "[" + line.product_id.default_code + "] " + line.product_id.name, line.location_id.name, qty_to_transfer)
                    )

        return super(flspstockpicking2, self).button_validate()
