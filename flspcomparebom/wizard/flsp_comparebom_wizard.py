# -*- coding: utf-8 -*-
import os

from odoo import models, fields, api
# import logging

# _logger = logging.getLogger(__name__)
# def _moduleName():
#     path = os.path.dirname(__file__)
#     return os.path.basename(os.path.dirname(path))
# openerpModule = _moduleName()

class FlspCompareBomWizard(models.TransientModel):
    """
        Class_Name: FlspCompareBomWizard
        Model_Name: flsp.comparebom.wizard
        Purpose:    To ask the user what BOMs to compare
        Date:       January/15/2021/F
        Author:     Sami Byaruhanga
    """
    _name = 'flsp.comparebom.wizard'
    _description = "FLSP Compare BoM Wizard"

    curActive = fields.Boolean(default=False)
    bom1 = fields.Many2one('mrp.bom', string='BOM 1', required=True, ondelete='cascade')
    bom2 = fields.Many2one('mrp.bom', string='BOM 2', required=True, ondelete='cascade')

    @api.onchange('curActive')
    def onchange_curActive(self):
        for rec in self:
            if rec.curActive:
                return {'domain': {'bom1': [('active','=',True)], 'bom2': [('active','=',True)]}}
            else:
                return {'domain': {'bom1': ['|',('active','=',True),('active','=',False)], 'bom2': ['|',('active','=',True),('active','=',False)]}}

    def select(self):
        """
                    Purpose:    Refactored version of compare called by a server action.
                                Will read the first 2 (or the first one twice) selected boms
                                Then open a compare bom form of the selected BOMS
                """
        active_ids = self.env.context.get('active_ids', [])
        if len(active_ids) >= 2:
            self.env['flsp.comparebom'].create({'bom1': active_ids[0], 'bom2': active_ids[1], })
            res = self.env['flsp.comparebom.view'].search([], limit=1).id
            view = self.env.ref('flspcomparebom.flsp_comparebom_view_form').id
        elif len(active_ids) == 1:
            self.env['flsp.comparebom'].create({'bom1': active_ids[0], 'bom2': active_ids[0], })
            res = self.env['flsp.comparebom.view'].search([], limit=1).id
            view = self.env.ref('flspcomparebom.flsp_comparebom_view_form').id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Compare BOMS',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view,
            'res_model': 'flsp.comparebom.view',
            'domain': [],
            'res_id': res,
        }

    def compare(self):
        """
            Purpose:    Save bom 1 and bom2 to flsp_comparebom table,
                        Then use that in def init to get information for bom comparison
                        Returns the view
        """
        self.ensure_one()
        self.env['flsp.comparebom'].create({'bom1': self.bom1.id, 'bom2': self.bom2.id, })
        res = self.env['flsp.comparebom.view'].search([], limit=1).id #returns number 1
        print(res)
        view = self.env.ref('flspcomparebom.flsp_comparebom_view_form').id
        # context = dict(self._context, active_ids=1)
        # print(context)

        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view,
            'res_model': 'flsp.comparebom.view',
            'domain': [],
            # 'target': 'new',  # to clear the breadcrumbs
            'target': 'main',  # to clear the breadcrumbs
            'res_id': res,      #very useful since it helps show which form to open, it can be any form i want
        }


class mrp_bom_inherit(models.Model):
    """
        Purpose inherit mrp.bom to change name to show versions
    """
    _inherit = 'mrp.bom'
    def name_get(self):
        return [(bom.id, '%s%s%s' % (bom.code and '%s: ' % bom.code or '', 'Version: %s ' % bom.version, bom.product_tmpl_id.display_name)) for bom in self]
