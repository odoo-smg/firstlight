# -*- coding: utf-8 -*-

from datetime import datetime

class FlspProductAutomation():

     # caller is the test case instance which calls this class to create testing objects
     def __init__(self, caller):
          self.caller = caller
     
     def create_product_tmpl(self, name, type, categ_id, uom_id, uom_po_id, tracking, standard_price, sale_line_warn, purchase_line_warn):
       return self.caller.env['product.template'].create(dict(
                        name=name,
                        type=type,
                        categ_id=categ_id,
                        uom_id=uom_id,
                        uom_po_id=uom_po_id,
                        tracking=tracking,
                        standard_price=standard_price,
                        sale_line_warn=sale_line_warn,
                        purchase_line_warn=purchase_line_warn,
                        ))
        
     def create_product(self, default_code, name, cost, onhand_qty):
          prod_template = self.create_product_tmpl(name, 'product', 8, 1, 1, 'none', cost, 'no-message', 'no-message')
          p = prod_template.product_variant_ids[0]
          p.default_code = default_code
          p.active = True

          self.caller.env['stock.quant'].create(dict(
                        product_id=p.id,
                        location_id=8,
                        quantity=onhand_qty,
                        reserved_quantity=0,
                        ))
          return p
        
     def create_typical_product(self, name_prefix, cost, onhand_qty):
          postfix = str(datetime.now())
          aName = name_prefix + '-' + postfix
          default_code = name_prefix + '-code-' + postfix
          return self.create_product(default_code, aName, cost, onhand_qty)
        
     def create_uom(self, name_prefix):
          postfix = str(datetime.now())
          aName = name_prefix + '-' + postfix
          return self.caller.env['uom.uom'].create({
                        'name': aName,
                        'category_id': 1,
                        'factor': 1,
                        'rounding': 0.01,
                        'uom_type': 'smaller',
               })
