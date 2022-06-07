# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions


class FlspMrpSubBomLine(models.Model):
    """
        class_name: FlspMrpSubBomLine
        model_name: inherits BOM LINE
        Purpose:    To add check if the component allow substitution
        Date:       August/27nd/2021/Friday
        Author:     Alexandre Sousa
    """
    _inherit = 'mrp.bom.line'

    flsp_substitute = fields.Boolean(string="Substitute", copy=True)

    @api.onchange('flsp_substitute')
    def onchange_flsp_substitute(self):
        if not self.flsp_substitute:
            unchek = True
            for item in self.bom_id.flsp_substitution_line_ids:
                if self.product_id == item.product_id:
                    unchek = False
            if not unchek:
                raise exceptions.ValidationError("This product has substitute. Please, delete them before uncheck.")
                self.flsp_substitute = True
        else:
            if self.product_id.type != 'product':
                raise exceptions.ValidationError("This product cannot be substituted. Only Storable products can be substituted.")
                self.flsp_substitute = False
            if self.product_qty <= 0:
                raise exceptions.ValidationError("Product with quantity zero cannot be substituted.")
                self.flsp_substitute = False


    def unlink(self):
        for line in self:
            if line.flsp_substitute:
                raise ValidationError('not allowed to delete record with substitution')
        return super(FlspMrpSubBomLine, self).unlink()
