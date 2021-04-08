# -*- coding: utf-8 -*-
# from flspArchieveBase.mrp_plm.models.mrp_eco import MrpEco
from odoo import models, fields, api


class FlspEcoReject(models.Model):
    """
        class_name: FlspEcoReject
        model_name: mrp.eco
        Purpose:    To create a product backup to be used when rejecting an ECO Stage
        Date:       April.7th.2021.W
        Author:     Sami Byaruhanga
    """
    _inherit = 'mrp.eco'

    backup_pdct = fields.Many2one('product.template', string='Back up product', compute='create_backup', store=True)

    @api.depends('state')
    def create_backup(self):
        """"
            Purpose:    To create back up product based on state and product_templ_id
                        Unlink backup when the ECO Is done
        """
        for record in self:
            if record.state == 'confirmed':
                if record.product_tmpl_id:
                    print("We have confirmed state")
                    backup_pdct = record.product_tmpl_id.copy(default={'active': False,
                                                                       'name': record.product_tmpl_id.name  + ' ',
                                                                       })
                    record.backup_pdct = backup_pdct

            if record.state == 'done' and record.backup_pdct:
                print("ECO IS Done")
                record.backup_pdct.unlink()

    def reject(self):
        """
            Purpose:    To write the product to intial state
            Note:       Method inherited from parent class add the product_tmpl_id.write
        """
        self._create_or_update_approval(status='rejected')
        self.product_tmpl_id.write({'name': self.backup_pdct.name,
                                    'type': self.backup_pdct.type,
                                    'categ_id': self.backup_pdct.categ_id.id,
                                    'list_price': self.backup_pdct.list_price,
                                    'taxes_id': self.backup_pdct.taxes_id,
                                    'standard_price': self.backup_pdct.standard_price,
                                    'uom_id': self.backup_pdct.uom_id.id,
                                    'tracking': self.backup_pdct.tracking,
                                    'attachment_ids': self.backup_pdct.attachment_ids,
                                    'x_studio_specification': self.backup_pdct.x_studio_specification,
                                    'x_studio_drawing': self.backup_pdct.x_studio_drawing,
                                    })

"""
    In case we need for plm
    'volume': self.backup_pdct.volume,
    'legacy_code': self.backup_pdct.legacy_code,
    'weight': self.backup_pdct.weight,
    'sale_ok': self.backup_pdct.sale_ok,
    'purchase_ok': self.backup_pdct.purchase_ok,
    'uom_po_id': self.backup_pdct.uom_po_id,
    'flsp_specification': self.backup_pdct.flsp_specification,
    'flsp_tags_id': self.backup_pdct.flsp_tags_id,
    'flsp_manufacturer': self.backup_pdct.flsp_manufacturer,
    'flsp_manufacture_part_number': self.backup_pdct.flsp_manufacture_part_number,
"""
