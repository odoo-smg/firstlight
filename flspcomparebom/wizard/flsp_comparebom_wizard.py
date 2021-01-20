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

    bom1 = fields.Many2one('mrp.bom', string='BOM 1', required=True, ondelete='cascade')
    bom2 = fields.Many2one('mrp.bom', string='BOM 2', required=True, ondelete='cascade')

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
