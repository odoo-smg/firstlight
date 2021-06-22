# -*- coding: utf-8 -*-

from datetime import datetime

class FlspMrpAutomation():

     # caller is the test case instance which calls this class to create testing objects
     def __init__(self, caller):
          self.caller = caller
        
     def create_bom(self, product):
          return self.caller.env['mrp.bom'].create({
                        'code': product.name + "_bom",
                        'active': True,
                        'type': 'normal',
                        'product_tmpl_id': product.product_tmpl_id.id,
                        'product_id': product.id,
                        'product_qty': 1,
                        'product_uom_id': 1,
                        'ready_to_produce': 'asap',
               })
        
     def create_bom_lines(self, bom, bom_lines):
          for line in bom_lines:
               self.caller.env['mrp.bom.line'].create({
                        'product_id': line["product_id"],
                        'product_qty': line["qty"],
                        'product_uom_id': 1,
                        'bom_id': bom.id,
               })
