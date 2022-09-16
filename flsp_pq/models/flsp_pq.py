# -*- coding: utf-8 -*-
from odoo import api, fields, models

class Flsp_PqComment(models.Model):
    """
            Class_Name: FLSP_PQ_Comment
            Model_Name: To create the comments to specify on the product description
            Purpose:    To help create PQ'S
            Date:       Dec/2nd/Wednesday/2020
            Updated:
            Author:     Sami Byaruhanga
    """
    _name = "flsp.pqcomment"
    _description = "Flsp PQ Comment"
    _rec_name = "flsp_pqcomment_name"

    flsp_pqcomment_name = fields.Char(string='PQ Comment Name', required=True, help='Specify the Pq comment name')
    flsp_pqcomment_desc = fields.Char(string='PQ Comment Description', help='Enter detailed pq comment description')


class Flsp_PQ(models.Model):
    """
            Class_Name: FLSP_PQ
            Model_Name: inherits the purchase model
            Purpose:    To help create PQ'S
            Date:       Dec/2nd/Wednesday/2020
            Updated:
            Author:     Sami Byaruhanga
    """
    _inherit = 'purchase.order'

    flsp_pq_check = fields.Boolean(string='PQ', help='Check box if its a PQ', default=False)
    flsp_pq_name = fields.Char(string='PQ Reference', index=True, copy=False, )


    @api.model
    def create(self, vals):
        """
            Purpose: To create the sequence For the PQ's
        """
        vals['flsp_pq_name'] = self.env['ir.sequence'].next_by_code('test.order')
        return super(Flsp_PQ, self).create(vals)
    _sql_constraints = [
        ('unique_pq_number', 'UNIQUE(flsp_pq_name)', 'The PQ Number must be unique')
    ]

class Flsp_PQ_line(models.Model):
    """
        Class_Name: FLSP_PQ
        Model_Name: inherits the purchase model
        Purpose:    To help add the comment on the order line
        Date:       Dec/2nd/Wednesday/2020
        Updated:
        Author:     Sami Byaruhanga
    """
    _inherit = 'purchase.order.line'

    flsp_pq_check = fields.Boolean(related='order_id'
                                           '.flsp_pq_check')
    flsp_pq_comment = fields.Many2one('flsp.pqcomment', string='PQ Comment', ondelete='cascade',
                    help='Specify the PQ comment to add on the product description')
