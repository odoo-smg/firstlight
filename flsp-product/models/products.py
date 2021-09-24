# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions
from odoo.exceptions import ValidationError
from datetime import date, datetime
import logging
_logger = logging.getLogger(__name__)

class Smgproduct(models.Model):
    _inherit = 'product.template'
    _check_company_auto = True

    @api.model
    def _default_nextprefix(self):
        flsp_default_part_init = self.env['res.config.settings'].get_flsp_part_init()
        self._cr.execute("select max(default_code) as code from product_product where default_code like '"+flsp_default_part_init+"%' and length(default_code) = 10 ")
        retvalue = self._cr.fetchall()
        returned_registre = retvalue[0]
        return self._get_next_prefix(returned_registre[0])

    @api.model
    def _next_default_code(self):
        flsp_default_part_init = self.env['ir.config_parameter'].sudo().get_param('product.template.flsp_part_init')[:1]
        self._cr.execute("select max(default_code) as code from product_product where default_code like '"+flsp_default_part_init+"%' and length(default_code) = 10 ")
        retvalue = self._cr.fetchall()
        returned_registre = retvalue[0]
        next_prefix = self._get_next_prefix(returned_registre[0])
        next_suffix = '000'
        return flsp_default_part_init+next_prefix+'-'+next_suffix

    # Change description and set it as mandatory
    default_code = fields.Char(string="Internal Reference", readonly=True)
    # Change default Can be Sold to False
    sale_ok = fields.Boolean('Can be Sold', default=False)

    # New fields to compose the part number
    legacy_code = fields.Char(string="Legacy Part #")
    flsp_part_prefix = fields.Char(string="Part # Prefix", default=_default_nextprefix)
    flsp_part_suffix = fields.Char(string="Part # Suffix", default="000")

    # New fields for sales approval
    flsp_min_qty = fields.Integer(string="Min. Qty Sale", default=1)

    attachment_ids = fields.Many2many('ir.attachment', 'product_attachment_rel','drawing_id', 'attachment_id',
        string='Attachments',
        help='Attachments are linked to a document through model / res_id and to the message '
             'through this field.')

    # Account review enforcement
    #    if (self.env.uid != 8):
    flsp_acc_valid   = fields.Boolean(string="Accounting Validated", readonly=True, copy=False)

    standard_price = fields.Float(
        'CAD$ Cost', compute='_compute_standard_price',
        inverse='_set_standard_price', search='_search_standard_price',
        digits='Product Price', groups="base.group_user",
        help="""In Standard Price & AVCO: value of the product (automatically computed in AVCO).
        In FIFO: value of the last unit that left the stock (automatically computed).
        Used to value the product when the purchase cost is not known (e.g. inventory adjustment).
        Used to compute margins on sale orders.""")

    flsp_usd_cost = fields.Float(
        'USD$ Cost', compute='_compute_flsp_usd_cost',
        digits='Product Price', groups="base.group_user",
        help="""Converted cost to USD$""")

    flsp_pref_cost = fields.Float('Preferred Cost', digits='Product Price')
    flsp_best_cost = fields.Float('Optimistic Cost', digits='Product Price')
    flsp_worst_cost = fields.Float('Pessimistic Cost', digits='Product Price')

    flsp_usd_pref_cost = fields.Float('Preferred USD Cost', digits='Product Price', compute='_compute_flsp_usd_cost')
    flsp_usd_best_cost = fields.Float('Optimistic USD Cost', digits='Product Price', compute='_compute_flsp_usd_cost')
    flsp_usd_worst_cost = fields.Float('Pessimistic USD Cost', digits='Product Price', compute='_compute_flsp_usd_cost')

    @api.depends('standard_price', 'flsp_pref_cost', 'flsp_best_cost', 'flsp_worst_cost')
    def _compute_flsp_usd_cost(self):
        us_currency_id = self.env['res.currency'].search([('name', '=', 'USD')], limit=1).id
        usd_rate = self.env['res.currency.rate'].search([('currency_id', '=', us_currency_id)],limit=1)
        for each in self:
            each.flsp_usd_cost = each.standard_price * usd_rate.rate
            each.flsp_usd_pref_cost = each.flsp_pref_cost * usd_rate.rate
            each.flsp_usd_best_cost = each.flsp_best_cost * usd_rate.rate
            each.flsp_usd_worst_cost = each.flsp_worst_cost * usd_rate.rate



    # constraints to validate code and description to be unique
    _sql_constraints = [
        ('default_code_name_check_flsp6',
         'CHECK(name != default_code)',
         "The Name of the product should not be the product code"),

        ('default_code_unique_flsp6',
         'UNIQUE(default_code)',
         "The Product Code must be unique"),

        #('name_unique_flsp6',
        # 'UNIQUE(name)',
        # "The Product name must be unique"),
    ]

    def button_acc_valid(self):
        prd_prd = self.env['product.product'].search([('product_tmpl_id', '=', self.id)])
        if prd_prd:
            prd_prd.flsp_acc_valid = True
        return self.write({'flsp_acc_valid': True})

    def button_acc_valid_off(self):
        prd_prd = self.env['product.product'].search([('product_tmpl_id', '=', self.id)])
        if prd_prd:
            prd_prd.flsp_acc_valid = False
        return self.write({'flsp_acc_valid': False})

    @api.model
    def _get_next_prefix(self, currpartnum):
        flsp_default_part_init = self.env['res.config.settings'].get_flsp_part_init()
        retvalue = ''
        if not currpartnum:
            currpartnum = '00001'
        if (currpartnum[0:1]!=flsp_default_part_init):
            retvalue = '00001'
        else:
            retvalue = ('00000'+str(int(currpartnum[1:6])+1))[-5:]
        return retvalue


    @api.onchange('flsp_part_suffix')
    def flsp_part_suffix_onchange(self):
        flsp_default_part_init = self.env['ir.config_parameter'].sudo().get_param('product.template.flsp_part_init')[:1]
        if not(self.flsp_part_suffix):
            suffix = '000'
        else:
            suffix = self.flsp_part_suffix
        if not(self.flsp_part_prefix):
            prefix = '00000'
        else:
            prefix = self.flsp_part_prefix
        return_val = flsp_default_part_init+('00000' + prefix.replace("_", ""))[-5:] + '-' + ('000' + suffix.replace("_", ""))[-3:]
        self.default_code = return_val
        return {
            'value': {
                'default_code': return_val
            },
        }

    @api.onchange('flsp_part_prefix')
    def flsp_part_prefix_onchange(self):
        flsp_default_part_init = self.env['ir.config_parameter'].sudo().get_param('product.template.flsp_part_init')[:1]
        if not(self.flsp_part_suffix):
            suffix = '000'
        else:
            suffix = self.flsp_part_suffix
        if not(self.flsp_part_prefix):
            prefix = '00000'
        else:
            prefix = self.flsp_part_prefix
        return_val = flsp_default_part_init+('00000' + prefix.replace("_", ""))[-5:] + '-' + ('000' + suffix.replace("_", ""))[-3:]
        self.default_code = return_val
        return {
            'value': {
                'default_code': return_val
            },
        }

    #Modified Apr.7th.2021.W by Sami to account for wheather the product has default values
    def copy(self, default=None):
        flsp_default_part_init = self.env['ir.config_parameter'].sudo().get_param('product.template.flsp_part_init')[:1]
        default = dict(default or {})

        # Useful for Products with default values set in this case flsp-eco-reject
        if default:
            prefix = '00000'
            self._cr.execute(
                "select max(CAST(flsp_part_suffix AS INT)) as suffix from product_template where active ='false'")
            table = self._cr.fetchall()
            for line in table:
                if type(line[0]) == int:
                    suf = str(line[0] + 1) + ""
                else:
                    suf = '0'
            suffix = suf
            default['default_code'] = '9'+prefix+'-'+suffix
            default['flsp_part_suffix'] = suffix
            default['flsp_part_prefix'] = prefix
            return super(Smgproduct, self).copy(default)

        else:
            # PREFIX INFORMATION
            if not(self.flsp_part_prefix):
                prefix = '00000'
            else:
                prefix = self.flsp_part_prefix

            # SUFFIX INFORMATION
            self._cr.execute(
                "select max(flsp_part_suffix) as suffix from product_template where flsp_part_prefix like '" + self.flsp_part_prefix + "%'")
                # "select max(flsp_part_suffix) as suffix from product_template where flsp_part_prefix like '" + self.flsp_part_prefix + "%' and length(default_code) = 10 ")
            table = self._cr.fetchall()
            for line in table:
                value = int(line[0])
            suf = value

            if not(self.flsp_part_suffix):
                suffix = '000'
            else:
                # suffix = str(int(self.flsp_part_suffix)+1)+""
                suffix = str(suf+1)+""

            suffix = ('000'+str(int(suffix)))[-3:]
            default_init = self.default_code[:1]

            default['default_code'] = default_init+prefix+'-'+suffix
            default['flsp_part_suffix'] = suffix
            default['flsp_part_prefix'] = prefix
            if 'flsp_plm_valid' in self.env['product.template']._fields:
                default['flsp_plm_valid'] = False
            return super(Smgproduct, self).copy(default)


    @api.constrains('name') #,'flsp_part_prefix')
    def _constraint_only_unique_name(self):
        """
            Date:    Nov/19th/2020/Thursday
            Purpose: To create only unique names
                     To raise exception if name is used but prefix don't match
	    Modified:Apr/7th/W to account for whether the product is active
            Author: Sami Byaruhanga
        """
        self._cr.execute('''
            SELECT id pdct_id, name, flsp_part_prefix, default_code, active from product_template

        ''')

        res = self._cr.fetchall() #returns all
        for line in res:
            if line[4]: #accoung for whether the product is active
                if self.name == line[1] and self.flsp_part_prefix != line[2]:
                    raise ValidationError('Name already used on product with default code: ' + line[3] +
                                      '\nTo use this name you must use the matching Part # Prefix: ' + line[2] +
                                      ' and increment the Part # Suffix'
                                      )

    @api.model
    def flspCostUpdate(self):
        """
         Date:    Sep/23th/2021
         Purpose: create a routine to recalculate the cost of finished products based on BOM.
            - Preferred vendor cost.
            - Best Case scenario - best price on product vendor price list
            - Worst Case scenario - worst price on product vendor price list
         Author:  Alexandre Sousa
        """
        _logger.info("Starting 'flsp_scenario_update' for all products with price list.")
        self.flsp_scenario_update()

        _logger.info("Starting 'recalculateCost()' for finished products.")

        finished_products = self.env['product.product'].search([]).filtered(lambda p: p.bom_count > 0)
        #_logger.info("The products to calculate: " + str(finished_products.mapped('display_name')))

        try:
            # finished_products.calculate_bom_cost()
            self.update_scenario_bom_cost(finished_products)
            _logger.info("'recalculateCost()' done.")
            # finished_products.notify_recalculateCost()
        except BomLoop2Exception as e:
            _logger.info("'recalculateCost()' stopped due to the exception!")
            # prods_in_loop = self.browse(e.prods)
            # prods_in_loop.notify_recalculateCost(e)

    # Simialr to method action_bom_cost() in \mrp_account\models\product.py
    # the products exclude ones with "valuation == 'real_time'" in method action_bom_cost(), but no need to filter them out in our schedule
    def update_scenario_bom_cost(self, products):
        # get all boms for the products
        boms_to_recompute = self.env['mrp.bom'].search(
            ['|', ('product_id', 'in', products.ids), '&', ('product_id', '=', False),
             ('product_tmpl_id', 'in', products.mapped('product_tmpl_id').ids)])

        # In Dynamic Programming, costMap is used to map products which have been calculated this time to its cost
        # key: product.id
        # value: product.standard_price
        costMap = {}

        for product in products:
            print('Calculating product: ' + product.display_name)
            prod_price = costMap.get(product.id)
            if not prod_price:
                a_ret = self.update_scenario_price_from_bom(product, costMap, boms_to_recompute)
                print('   calculated returned: 0...: ' + str(a_ret[0])+'  1...:'+ str(a_ret[1])+'  2...:'+ str(a_ret[2])+'  3...:'+ str(a_ret[3]))
                costMap[product.id] = a_ret
                prod_price = a_ret
            else:
                print('   saved else where - returned: 0...: ' + str(prod_price[0])+'  1...:'+ str(prod_price[1])+'  2...:'+ str(prod_price[2])+'  3...:'+ str(prod_price[3]))



            # set standard_price with the cost
            if prod_price:
                product.standard_price = prod_price[0]
                product.flsp_pref_cost = prod_price[1]
                product.flsp_best_cost = prod_price[2]
                product.flsp_worst_cost = prod_price[3]
            else:
                _logger.info(
                    "Skip to reset the price because the BoM cost is 0 for product " + str(product.display_name))

    def update_scenario_price_from_bom(self, product, costMap, boms_to_recompute=False):
        product.ensure_one()
        bom = self.env['mrp.bom']._bom_find(product=product)

        # for given product, use prod_depended_list with product ids to detect loop based on bom dependency
        prod_depended_list = []

        return self.update_scenario_bom_price(product, bom, costMap, prod_depended_list, boms_to_recompute=boms_to_recompute)

    def update_scenario_bom_price(self, product, bom, costMap, prod_depended_list, boms_to_recompute=False):

        prod_price = costMap.get(product.id)
        if prod_price:
            return prod_price

        product.ensure_one()
        if not bom:
            prod_price = [0, 0, 0, 0]
            costMap[product.id] = prod_price
            return prod_price
        if not boms_to_recompute:
            boms_to_recompute = []

        if product.id in prod_depended_list:
            # if bom exists in the list, there is a loop
            # 1) stop the calculation; 2) send notification out with the loop
            posOfLoop = prod_depended_list.index(product.id)
            exp_msg = "A loop of products with BoMs exists, please check the products with ids for details: " + str(
                prod_depended_list[posOfLoop:])
            _logger.warning(exp_msg)
            raise BomLoop2Exception(exp_msg, prod_depended_list[posOfLoop:])
        else:
            # add the bom in the tail of the list
            prod_depended_list.append(product.id)

        # calculate the cost based on the bom
        totals = [0, 0, 0, 0]
        for opt in bom.routing_id.operation_ids:
            duration_expected = (
                    opt.workcenter_id.time_start +
                    opt.workcenter_id.time_stop +
                    opt.time_cycle)
            totals[0] += (duration_expected / 60) * opt.workcenter_id.costs_hour
        for line in bom.bom_line_ids:
            print(' ->child: '+line.product_id.display_name + ' -  qty: '+str(line.product_qty) + ' std: '+str(line.product_id.standard_price)+ ' pref: '+str(line.product_id.flsp_pref_cost)+' best: '+str(line.product_id.flsp_best_cost)+'  worst: '+str(line.product_id.flsp_worst_cost))
            if line._skip_bom_line(product):
                print('************** skiping....')
                continue

            # Compute recursive if line has `child_line_ids`
            if line.child_bom_id and line.child_bom_id in boms_to_recompute:
                child_total = self.update_scenario_bom_price(line.product_id, line.child_bom_id, costMap, prod_depended_list,
                                                                  boms_to_recompute=boms_to_recompute)
                print('   child bom returned : 0...: ' + str(child_total[0])+'  1...:'+ str(child_total[1])+'  2...:'+ str(child_total[2])+'  3...:'+ str(child_total[3]))

                totals[0] += line.product_id.uom_id._compute_price(child_total[0], line.product_uom_id) * line.product_qty
                totals[1] += line.product_id.uom_id._compute_price(child_total[1], line.product_uom_id) * line.product_qty
                totals[2] += line.product_id.uom_id._compute_price(child_total[2], line.product_uom_id) * line.product_qty
                totals[3] += line.product_id.uom_id._compute_price(child_total[3], line.product_uom_id) * line.product_qty
            else:
                totals[0] += line.product_id.uom_id._compute_price(line.product_id.standard_price,
                                                               line.product_uom_id) * line.product_qty
                totals[1] += line.product_id.uom_id._compute_price(line.product_id.flsp_pref_cost,
                                                                   line.product_uom_id) * line.product_qty
                totals[2] += line.product_id.uom_id._compute_price(line.product_id.flsp_best_cost,
                                                                   line.product_uom_id) * line.product_qty
                totals[3] += line.product_id.uom_id._compute_price(line.product_id.flsp_worst_cost,
                                                                   line.product_uom_id) * line.product_qty
                print('   no bom using : 0...: ' + str(totals[0]) + '  1...:' + str(totals[1]) + '  2...:' + str(totals[2]) + '  3...:' + str(totals[3]))
        bom_price = [0, 0, 0, 0]
        bom_price[0] = bom.product_uom_id._compute_price(totals[0] / bom.product_qty, product.uom_id)
        bom_price[1] = bom.product_uom_id._compute_price(totals[1] / bom.product_qty, product.uom_id)
        bom_price[2] = bom.product_uom_id._compute_price(totals[2] / bom.product_qty, product.uom_id)
        bom_price[3] = bom.product_uom_id._compute_price(totals[3] / bom.product_qty, product.uom_id)
        costMap[product.id] = bom_price

        # no loop found, remove the bom from the tail of the list
        prod_depended_list.pop()

        return bom_price



    def flsp_scenario_update(self):
        current_date = date.today()
        # current_date_str = str(current_date)[0:10]

        products = self.env['product.template'].search([]) #.filtered(lambda p: p.type == "product")
        for product in products:
            flsp_pref_cost = False
            flsp_best_cost = product.standard_price
            flsp_worst_cost = product.standard_price
            price_list = self.env['product.supplierinfo'].search([('product_tmpl_id', '=', product.id)])
            for price in price_list:
                exchange_rate = self.env['res.currency.rate'].search([('currency_id', '=', price.currency_id.id)], limit=1)
                uom_price = price.product_uom._compute_price(price.price, product.uom_id)
                # if price.product_uom.id != product.uom_id.id:
                #    print('Product '+product.display_name+'    price: '+str(price.price) + '    converted: '+str(uom_price))
                if exchange_rate:
                    if exchange_rate.rate > 0:
                        curr_value = uom_price / exchange_rate.rate
                    else:
                        curr_value = uom_price
                else:
                    curr_value = 0
                if price.date_start and price.date_end:
                    if price.date_start <= current_date and current_date <= price.date_end:
                        if not flsp_pref_cost:
                            flsp_pref_cost = curr_value
                        if curr_value < flsp_best_cost:
                            flsp_best_cost = curr_value
                        if curr_value > flsp_worst_cost:
                            flsp_worst_cost = curr_value
                else:
                    if not flsp_pref_cost:
                        flsp_pref_cost = curr_value
                    if curr_value < flsp_best_cost or flsp_best_cost <= 0:
                        flsp_best_cost = curr_value
                    if curr_value > flsp_worst_cost:
                        flsp_worst_cost = curr_value

            if flsp_pref_cost:
                product.flsp_pref_cost = flsp_pref_cost
                product.flsp_best_cost = flsp_best_cost
                product.flsp_worst_cost = flsp_worst_cost
            else:
                product.flsp_pref_cost = product.standard_price
                product.flsp_best_cost = product.standard_price
                product.flsp_worst_cost = product.standard_price

class BomLoop2Exception(Exception):
    def __init__(self, msg, prods):
        self.msg = msg
        self.prods = prods
