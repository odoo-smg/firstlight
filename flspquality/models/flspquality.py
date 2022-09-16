# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields, api, _, SUPERUSER_ID

# from odoo.exceptions import UserError, ValidationError
# import logging
# _logger = logging.getLogger(__name__)

class FlspQuality(models.Model):
    """
        class_name: FlspQuality
        model_name: flsp.quality
        Purpose:    To create customer quality control
        Date:       Jan/25th/2021/W
        Author:     Sami Byaruhanga
        Note:       Most of the source code is based from ODOO QUALITY AND QUALITY CONTROL modules
    """
    _name = 'flsp.quality'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'FLSP Customer Quality Control'
    _check_company_auto = True

    name = fields.Char('Name', default=lambda self: _('New'))
    title = fields.Char('Title')
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)

    date_create = fields.Datetime('Date Created', default=datetime.now())
    date_assign = fields.Datetime('Date Assigned')
    date_close = fields.Datetime('Date Closed')

    description = fields.Html('Description')
    action_corrective = fields.Html('Corrective Action')
    action_preventive = fields.Html('Preventive Action')

    created_by = fields.Many2one('res.users', 'Created By', default=lambda self: self.env.user)
    partner_id = fields.Many2one('res.partner', 'Customer', domain=[('customer_rank', '!=', 0)], check_company=True)
    product_tmpl_id = fields.Many2one('product.template', 'Product', check_company=True,
        domain="[('type', 'in', ['consu', 'product']), '|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    product_id = fields.Many2one('product.product', 'Product Variant', domain="[('product_tmpl_id', '=', product_tmpl_id)]")
    lot_id = fields.Many2one('stock.production.lot', 'Lot/SN', check_company=True,
        domain="['|', ('product_id', '=', product_id), ('product_id.product_tmpl_id.id', '=', product_tmpl_id), '|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    priority = fields.Selection([('0', 'Normal'), ('1', 'Low'), ('2', 'High'), ('3', 'Very High')], string='Priority', index=True)

    rga_num = fields.Char('RGA #')
    responsible = fields.Selection([('E', 'Electrical'), ('M', 'Mechanical'), ('S', 'Sales')], string='Classification')
    reason = fields.Many2one('flsp.qualityreason', ondelete='cascade', required=True, string="Root Cause")
    stage_id = fields.Many2one('flsp.qualitystage', 'Stage', ondelete='restrict',
        group_expand='_read_group_stage_ids',
        default=lambda self: self.env['flsp.qualitystage'].search([], limit=1).id)
    sale_id = fields.Many2one('sale.order', 'S/O', domain="[('order_line.product_id', '=', product_id)]")

    @api.model
    def create(self, vals):
        """
            Purpose: To create a sequence for quality control
        """
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('flsp.quality') or 'New'
            result = super(FlspQuality, self).create(vals)
        return result

    @api.onchange('product_tmpl_id')
    def onchange_product_tmpl_id(self):
        self.product_id = self.product_tmpl_id.product_variant_ids.ids and \
                          self.product_tmpl_id.product_variant_ids.ids[0]
        self.sale_id = False
        self.partner_id = False

    @api.onchange('sale_id')
    def onchange_sale_id_add_customer(self):
        self.partner_id = self.sale_id.partner_id

    def write(self, vals):
        print("executing")
        res = super(FlspQuality, self).write(vals)
        if self.stage_id.done and 'stage_id' in vals:
            self.write({'date_close': fields.Datetime.now()})
        return res

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        """ Read group customization in order to display all the stages of the ECO type
        in the Kanban view, even if there is no ECO in that stage
        """
        stage_ids = stages._search([], order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)

class FlspQualityReason(models.Model):
    """
        class_name: FlspQualityReason
        model_name: flsp.qualityreason
        Purpose:    To help in creating root causes
        Date:       January/26th/2021/Tuesday
        Author:     Sami Byaruhanga
    """

    _name = 'flsp.qualityreason'
    _description = "Root Cause"

    name = fields.Char(string="Root Cause", required=True)
    description = fields.Text("Description")


class FlspQualityStage(models.Model):
    """
        class_name: FlspQualityStage
        model_name: flsp.qualitystage
        Purpose:    To help in creating stages which will be useful in Kanban view
        Date:       January/26th/2021/Tuesday
        Author:     Sami Byaruhanga
    """
    _name = 'flsp.qualitystage'
    _description = "Stages"
    _order = "sequence, id"
    _fold_name = 'folded'

    name = fields.Char('Name', required=True, translate=True)
    sequence = fields.Integer('Sequence')
    folded = fields.Boolean('Folded')
    done = fields.Boolean('Done')

# class QualityTag(models.Model):
#     _name = "quality.tag"
#     _description = "Quality Tag"
#
#     name = fields.Char('Tag Name', required=True)
#     color = fields.Integer('Color Index', help='Used in the kanban view')  # TDE: should be default value


