# -*- coding: utf-8 -*-

from odoo import fields, models, api


class MrpBom(models.Model):
    _inherit = 'mrp.bom'
    _check_company_auto = True

    def name_get(self):
        if self.env.context.get('custom_search', False):
            result = []
            text = ''
            for r in self:
                if len(r.code) > 50:
                    text = r.code[:50] + '...'
                else:
                    text = r.code
                    if len(r.product_tmpl_id.name) > 25:
                        text = text + " " + r.product_tmpl_id.name[:25] + '...'
                    else:
                        text = text + " " + r.product_tmpl_id.name
                result.append((r.id, text))
            return result
        else:
            return [(bom.id, '%s%s' % (bom.code and '%s: ' % bom.code or '', bom.product_tmpl_id.display_name)) for bom in self]
