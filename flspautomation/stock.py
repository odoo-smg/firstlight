# -*- coding: utf-8 -*-

from datetime import datetime

class FlspStockAutomation():

     # caller is the test case instance which calls this class to create testing objects
     def __init__(self, caller):
          self.caller = caller
        
     def create_location(self, name_prefix, complete_name, usage, parent_location_id):
          postfix = str(datetime.now())
          aName = name_prefix + '-' + postfix
          return self.caller.env['stock.location'].create({
                        'name': aName,
                        'complete_name': complete_name,
                        'usage': usage,
                        'location_id': parent_location_id,
                        'active': True,
               })
        
     def create_lot(self, name_prefix, product_id):
          postfix = str(datetime.now())
          aName = name_prefix + '-' + postfix
          return self.caller.env['stock.production.lot'].create({
                        'name': aName,
                        'product_id': product_id,
                        'company_id': 1,
               })

     def create_stock_quant(self, product_id, location_id, lot_id, package_id, quantity):
          return self.caller.env['stock.quant'].create({
                        'product_id': product_id,
                        'location_id': location_id,
                        'lot_id': lot_id,
                        'package_id': package_id,
                        'quantity': quantity,
               })

     def create_package(self, name_prefix):
          postfix = str(datetime.now())
          aName = name_prefix + '-' + postfix
          return self.caller.env['stock.quant.package'].create({
                        'name': aName,
               })

     def create_move_line(self, product_id, location_id, lot_id, package_id):
          return self.caller.env['stock.move.line'].create({
                        'company_id': 1,
                        'product_uom_id': product_id,
                        'product_uom_qty': lot_id,
                        'date': package_id,
                        'location_id': location_id,
                        'location_dest_id': package_id,
               })
