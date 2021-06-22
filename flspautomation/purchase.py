# -*- coding: utf-8 -*-

from datetime import datetime

class FlspPurchaseAutomation():

     # caller is the test case instance which calls this class to create testing objects
     def __init__(self, caller):
          self.caller = caller
        
     def create_simple_purchase_order(self, name_prefix):
          postfix = str(datetime.now())
          aName = name_prefix + '-' + postfix
          return self.caller.env['purchase.order'].create({
                        'name': aName,
                        'date_order': datetime.now(),
                        'partner_id': 9, # 9 for 'Wood Corner'
                        'currency_id': 4, # 4 for CAD
                        'company_id': 1, # 1 for 'My Company'
                        'picking_type_id': 1, # 1 for 'Receipts'
               })
        
     def create_simple_purchase_order_line(self, name_prefix, order_id, product, product_qty, price_unit=1):
          postfix = str(datetime.now())
          aName = name_prefix + '-' + postfix
          return self.caller.env['purchase.order.line'].create({
                        'name': aName,
                        'order_id': order_id, 
                        'product_id': product.id, 
                        'product_qty': product_qty,
                        'price_unit': price_unit,
                        'product_uom': product.uom_id.id,
                        'product_uom_qty': product.uom_id.id,
                        'date_planned': datetime.now(),
               })
