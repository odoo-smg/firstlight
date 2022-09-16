# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import calendar
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo import api, models


class FlspStockReportTransactions(models.AbstractModel):
    _name = 'report.flsp_stock_report_transactions.flsp_transrep'
    _description = 'FLSP - Stock Transactions'

    @api.model
    def _get_report_values(self, docids, data=None):
        lot = False
        if data['lot_id']:
            lot = data['lot_id'][1]

        query = ""
        query += " select sml.id, sml.date, sml.reference, sp.origin, pp.default_code, sml.product_uom_id, spl.name, "
        query += "        sml.qty_done, "
        query += "        case when sml.location_id = "+str(data['location_id'][0])+" then '-' else '+' end as operation, "
        query += " SUM(case when sml.location_id = "+str(data['location_id'][0])+" then sml.qty_done*(-1) else sml.qty_done end ) OVER (ORDER BY sml.date, sml.id ASC) as balance"
        query += " from   stock_move_line as sml"
        query += " inner join product_product as pp"
        query += " on         pp.id = sml.product_id"
        query += " left join stock_picking as sp"
        query += " on         sp.id = sml.picking_id"
        query += " left join  stock_production_lot as spl"
        query += " on         spl.id = sml.lot_id"
        query += " where  sml.product_id = " + str(data['product_id'][0])
        query += " and    sml.state = 'done'"
        query += " and    (sml.location_id = "+str(data['location_id'][0])+" or sml.location_dest_id = "+str(data['location_id'][0])+")"
        if data['lot_id']:
            query += " and    spl.id = " +str(data['lot_id'][0])
        query += " order by sml.date, sml.id ASC;"

        self._cr.execute(query)
        retvalue = self._cr.fetchall()

        return {
            'data' : retvalue,
            'product' : data['product_id'][1],
            'location': data['location_id'][1],
            'lot': lot,
            'tracking': data['tracking'],
        }
