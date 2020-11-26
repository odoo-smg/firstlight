# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Deliveryflspwizard(models.TransientModel):
    _name = 'flspstock.deliverywizard'
    _description = "Wizard: Confirm Delivery Date"

    @api.model
    def default_get(self, fields):
        res = super(Deliveryflspwizard, self).default_get(fields)
        picking_id = self.env.context.get('default_stock_picking_id') or self.env.context.get('active_id')
        if picking_id:
            stock_picking = self.env['stock.picking'].browse(picking_id)
        if stock_picking.exists():
            if 'flsp_stock_picking_id' in fields:
                res['flsp_stock_picking_id'] = stock_picking.id
            if 'flsp_confirmed_date' in fields:
                res['flsp_confirmed_date'] = stock_picking.flsp_confirmed_date
            if 'flsp_confirmed_by' in fields:
                res['flsp_confirmed_by'] = stock_picking.flsp_confirmed_by
            if 'flsp_is_updating' in fields:
                if stock_picking.flsp_confirmed_by:
                    res['flsp_is_updating'] = True
                else:
                    res['flsp_is_updating'] = False

        res = self._convert_to_write(res)
        return res

    flsp_stock_picking_id = fields.Many2one('stock.picking', string="Delivery Order", readonly=True)
    flsp_confirmed_date = fields.Datetime(string="Confirmed Delivery Date", readonly=True)
    flsp_confirmed_by = fields.Many2one('res.users', string="Confirmed by", readonly=True)
    flsp_schedule_date = fields.Datetime(string="New Schedule Date", required=True)
    flsp_change_note = fields.Text(string="Change Note")
    flsp_is_updating = fields.Boolean(string="Is Updating")

    def flsp_confirm(self):
        self.ensure_one()
        self.flsp_stock_picking_id.write({'flsp_confirmed_by': self._uid, })
        self.flsp_stock_picking_id.write({'flsp_confirmed_date': self.flsp_schedule_date, })
        self.flsp_stock_picking_id.write({'scheduled_date': self.flsp_schedule_date, })
        self.flsp_stock_picking_id.sale_id.write({'commitment_date': self.flsp_schedule_date, })
        if self.flsp_is_updating:
            self.env['flspautoemails.bpmemails'].send_email(self, 'SO0008')
        else:
            self.env['flspautoemails.bpmemails'].send_email(self, 'SO0007')
        return {'type': 'ir.actions.act_window_close'}
