# -*- coding: utf-8 -*-

import json

from odoo import api, models, _
from odoo.tools import float_round

class FlspCostScenarioStructure(models.AbstractModel):
    _name = 'report.report_cost_scenario_structure'
    _description = 'BOM Structure Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = []
        for mo in docids:
            bom_id = mo.bom_id
            bom = self.env['mrp.bom'].browse(bom_id)
            candidates = bom.product_id or bom.product_tmpl_id.product_variant_ids
            # quantity = float(data.get('quantity', 1))
            quantity = float(mo.product_qty)
            for product_variant_id in candidates.ids:
                if data and data.get('childs'):
                    doc = self._get_pdf_line(bom_id, product_id=product_variant_id, qty=quantity, child_bom_ids=json.loads(data.get('childs')))
                else:
                    doc = self._get_pdf_line(bom_id, product_id=product_variant_id, qty=quantity, unfolded=True)
                doc['report_type'] = 'pdf'
                doc['report_structure'] = data and data.get('report_type') or 'all'
                docs.append(doc)
            if not candidates:
                if data and data.get('childs'):
                    doc = self._get_pdf_line(bom_id, qty=quantity, child_bom_ids=json.loads(data.get('childs')))
                else:
                    doc = self._get_pdf_line(bom_id, qty=quantity, unfolded=True)
                doc['report_type'] = 'pdf'
                doc['report_structure'] = data and data.get('report_type') or 'all'
                docs.append(doc)
        return {
            'doc_ids': docids,
            'doc_model': 'mrp.bom',
            'docs': docs,
        }

    @api.model
    def get_html(self, bom_id=False, searchQty=1, searchVariant=False):
        res = self._get_report_data(bom_id=bom_id, searchQty=searchQty, searchVariant=searchVariant)
        res['lines']['report_type'] = 'html'
        res['lines']['report_structure'] = 'all'
        res['lines']['has_attachments'] = res['lines']['attachments'] or any(component['attachments'] for component in res['lines']['components'])
        res['lines'] = self.env.ref('flsp_cost_scenario_structure.report_flsp_cost_bom').render({'data': res['lines']})
        return res

    @api.model
    def get_bom(self, bom_id=False, product_id=False, line_qty=False, line_id=False, level=False):
        lines = self._get_bom(bom_id=bom_id, product_id=product_id, line_qty=line_qty, line_id=line_id, level=level)
        return self.env.ref('flsp_cost_scenario_structure.report_flsp_cost_bom_line').render({'data': lines})

    @api.model
    def get_operations(self, bom_id=False, qty=0, level=0):
        bom = self.env['mrp.bom'].browse(bom_id)
        lines = self._get_operation_line(bom.routing_id, float_round(qty / bom.product_qty, precision_rounding=1, rounding_method='UP'), level)
        values = {
            'bom_id': bom_id,
            'currency': self.env.company.currency_id,
            'operations': lines,
        }
        return self.env.ref('flsp_cost_scenario_structure.report_flsp_mrp_operation_line').render({'data': values})

    @api.model
    def _get_report_data(self, bom_id, searchQty=0, searchVariant=False):
        lines = {}
        #mo_id = self.env['mrp.production'].browse(bom_id)
        #bom_id = mo_id.bom_id.id
        bom = self.env['mrp.bom'].browse(bom_id)
        #searchQty = mo_id.product_qty
        bom_quantity = searchQty or bom.product_qty or 1
        bom_product_variants = {}
        bom_uom_name = ''
        if bom:
            bom_uom_name = bom.product_uom_id.name

            # Get variants used for search
            if not bom.product_id:
                for variant in bom.product_tmpl_id.product_variant_ids:
                    bom_product_variants[variant.id] = variant.display_name
        lines = self._get_bom(bom_id, product_id=searchVariant, line_qty=bom_quantity, level=1)
        return {
            'lines': lines,
            'variants': bom_product_variants,
            'bom_uom_name': bom_uom_name,
            'bom_qty': bom_quantity,
            'is_variant_applied': self.env.user.user_has_groups('product.group_product_variant') and len(bom_product_variants) > 1,
            'is_uom_applied': self.env.user.user_has_groups('uom.group_uom')
        }

    def _get_bom(self, bom_id=False, product_id=False, line_qty=False, line_id=False, level=False):
        bom = self.env['mrp.bom'].browse(bom_id)
        company = bom.company_id or self.env.company
        bom_quantity = line_qty
        if line_id:
            current_line = self.env['mrp.bom.line'].browse(int(line_id))
            bom_quantity = current_line.product_uom_id._compute_quantity(line_qty, bom.product_uom_id)
        # Display bom components for current selected product variant
        if product_id:
            product = self.env['product.product'].browse(int(product_id))
        else:
            product = bom.product_id or bom.product_tmpl_id.product_variant_id
        if product:
            price = 0 # product.uom_id._compute_price(product.with_context(force_company=company.id).standard_price, bom.product_uom_id) * bom_quantity
            attachments = self.env['mrp.document'].search(['|', '&', ('res_model', '=', 'product.product'),
            ('res_id', '=', product.id), '&', ('res_model', '=', 'product.template'), ('res_id', '=', product.product_tmpl_id.id)])
        else:
            # Use the product template instead of the variant
            price = 0  # bom.product_tmpl_id.uom_id._compute_price(bom.product_tmpl_id.with_context(force_company=company.id).standard_price, bom.product_uom_id) * bom_quantity
            attachments = self.env['mrp.document'].search([('res_model', '=', 'product.template'), ('res_id', '=', bom.product_tmpl_id.id)])
        operations = []
        if bom.product_qty > 0:
            operations = self._get_operation_line(bom.routing_id, float_round(bom_quantity / bom.product_qty, precision_rounding=1, rounding_method='UP'), 0)
        on_hand = product.qty_available
        lines = {
            'bom': bom,
            'bom_qty': bom_quantity,
            'bom_prod_name': product.display_name[:70],
            'currency': company.currency_id,
            'product': product,
            'code': bom and bom.code or '',
            'price': price,
            'on_hand': on_hand,
            'actual_cost': product.standard_price,
            'highest': product.flsp_highest_price,
            'lowest': product.flsp_lowest_price,
            'latest': product.flsp_latest_cost,
            'usd_actual_cost': product.flsp_usd_cost,
            'usd_highest': product.flsp_usd_highest_price,
            'usd_lowest': product.flsp_usd_lowest_price,
            'usd_latest': product.flsp_usd_latest_cost,
            'total': sum([op['total'] for op in operations]),
            'level': level or 0,
            'operations': operations,
            'operations_cost': sum([op['total'] for op in operations]),
            'attachments': attachments,
            'operations_time': sum([op['duration_expected'] for op in operations])
        }
        components, total = self._get_bom_lines(bom, bom_quantity, product, line_id, level)
        lines['components'] = components
        lines['total'] += total
        return lines

    def _get_bom_lines(self, bom, bom_quantity, product, line_id, level):
        components = []
        total = 0
        for line in bom.bom_line_ids:
            line_quantity = (bom_quantity / (bom.product_qty or 1.0)) * line.product_qty
            if line._skip_bom_line(product):
                continue
            company = bom.company_id or self.env.company
            price = 0 # line.product_id.uom_id._compute_price(line.product_id.with_context(force_company=company.id).standard_price, line.product_uom_id) * line_quantity
            if line.child_bom_id:
                factor = line.product_uom_id._compute_quantity(line_quantity, line.child_bom_id.product_uom_id) / line.child_bom_id.product_qty
                sub_total = 0  # self._get_price(line.child_bom_id, factor, line.product_id)
            else:
                sub_total = price
            sub_total = self.env.company.currency_id.round(sub_total)
            prod_on_hand = line.product_id.qty_available
            components.append({
                'prod': line.product_id,
                'prod_id': line.product_id.id,
                'prod_name': line.product_id.display_name[:70],
                'code': line.child_bom_id and line.child_bom_id.code or '',
                'prod_qty': line_quantity,
                'prod_uom': line.product_uom_id.name,
                'prod_on_hand': prod_on_hand,
                'actual_cost': line.product_id.standard_price,
                'highest': line.product_id.flsp_highest_price,
                'lowest': line.product_id.flsp_lowest_price,
                'latest': line.product_id.flsp_latest_cost,
                'usd_actual_cost': line.product_id.flsp_usd_cost,
                'usd_highest': line.product_id.flsp_usd_highest_price,
                'usd_lowest': line.product_id.flsp_usd_lowest_price,
                'usd_latest': line.product_id.flsp_usd_latest_cost,
                'prod_cost': company.currency_id.round(price),
                'parent_id': bom.id,
                'line_id': line.id,
                'level': level or 0,
                'total': sub_total,
                'child_bom': line.child_bom_id.id,
                'phantom_bom': line.child_bom_id and line.child_bom_id.type == 'phantom' or False,
                'attachments': self.env['mrp.document'].search(['|', '&',
                    ('res_model', '=', 'product.product'), ('res_id', '=', line.product_id.id), '&', ('res_model', '=', 'product.template'), ('res_id', '=', line.product_id.product_tmpl_id.id)]),

            })
            total += sub_total
        return components, total

    def _get_operation_line(self, routing, qty, level):
        operations = []
        total = 0.0
        for operation in routing.operation_ids:
            operation_cycle = float_round(qty / operation.workcenter_id.capacity, precision_rounding=1, rounding_method='UP')
            duration_expected = operation_cycle * operation.time_cycle + operation.workcenter_id.time_stop + operation.workcenter_id.time_start
            total = ((duration_expected / 60.0) * operation.workcenter_id.costs_hour)
            operations.append({
                'level': level or 0,
                'operation': operation,
                'name': operation.name + ' - ' + operation.workcenter_id.name,
                'duration_expected': duration_expected,
                'total': self.env.company.currency_id.round(total),
            })
        return operations

    def _get_price(self, bom, factor, product):
        price = 0
        return price
        if bom.routing_id:
            # routing are defined on a BoM and don't have a concept of quantity.
            # It means that the operation time are defined for the quantity on
            # the BoM (the user produces a batch of products). E.g the user
            # product a batch of 10 units with a 5 minutes operation, the time
            # will be the 5 for a quantity between 1-10, then doubled for
            # 11-20,...
            operation_cycle = float_round(factor, precision_rounding=1, rounding_method='UP')
            operations = self._get_operation_line(bom.routing_id, operation_cycle, 0)
            price += sum([op['total'] for op in operations])

        for line in bom.bom_line_ids:
            if line._skip_bom_line(product):
                continue
            if line.child_bom_id:
                qty = line.product_uom_id._compute_quantity(line.product_qty * factor, line.child_bom_id.product_uom_id) / line.child_bom_id.product_qty
                sub_price = self._get_price(line.child_bom_id, qty, line.product_id)
                price += sub_price
            else:
                prod_qty = line.product_qty * factor
                company = bom.company_id or self.env.company
                not_rounded_price = line.product_id.uom_id._compute_price(line.product_id.with_context(force_comany=company.id).standard_price, line.product_uom_id) * prod_qty
                price += company.currency_id.round(not_rounded_price)
        return price

    def _get_pdf_line(self, bom_id, product_id=False, qty=1, child_bom_ids=[], unfolded=False):
        def get_sub_lines(bom, product_id, line_qty, line_id, level):
            data = self._get_bom(bom_id=bom.id, product_id=product_id, line_qty=line_qty, line_id=line_id, level=level)
            bom_lines = data['components']
            lines = []
            for bom_line in bom_lines:
                lines.append({
                    'name': bom_line['prod_name'],
                    'type': 'bom',
                    'quantity': bom_line['prod_qty'],
                    'uom': bom_line['prod_uom'],
                    'prod_cost': bom_line['prod_cost'],
                    'bom_cost': bom_line['total'],
                    'level': bom_line['level'],
                    'code': bom_line['code'],
                    'child_bom': bom_line['child_bom'],
                    'prod_id': bom_line['prod_id']
                })
                if bom_line['child_bom'] and (unfolded or bom_line['child_bom'] in child_bom_ids):
                    line = self.env['mrp.bom.line'].browse(bom_line['line_id'])
                    lines += (get_sub_lines(line.child_bom_id, line.product_id.id, bom_line['prod_qty'], line, level + 1))
            if data['operations']:
                lines.append({
                    'name': _('Operations'),
                    'type': 'operation',
                    'quantity': data['operations_time'],
                    'uom': _('minutes'),
                    'bom_cost': data['operations_cost'],
                    'level': level,
                })
                for operation in data['operations']:
                    if unfolded or 'operation-' + str(bom.id) in child_bom_ids:
                        lines.append({
                            'name': operation['name'],
                            'type': 'operation',
                            'quantity': operation['duration_expected'],
                            'uom': _('minutes'),
                            'bom_cost': operation['total'],
                            'level': level + 1,
                        })
            return lines

        bom = self.env['mrp.bom'].browse(bom_id)
        product_id = product_id or bom.product_id.id or bom.product_tmpl_id.product_variant_id.id
        data = self._get_bom(bom_id=bom_id, product_id=product_id, line_qty=qty)
        pdf_lines = get_sub_lines(bom, product_id, qty, False, 1)
        data['components'] = []
        data['lines'] = pdf_lines
        return data
