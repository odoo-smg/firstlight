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

     def create_typical_stock_picking(self, name_prefix, product, location_id, location_dest_id, picking_type_id=1, product_uom_id=1, product_uom_qty=4):
          stock_picking =  self.create_stock_picking(location_id.id, location_dest_id.id, picking_type_id)
          stock_move =  self.create_stock_move(name_prefix, product.id, stock_picking.location_id.id, stock_picking.location_dest_id.id, stock_picking.id)
          move_line =  self.create_stock_move_line(stock_move.location_id, stock_move.location_dest_id, stock_picking.id, product_uom_id, product_uom_qty)

          return stock_picking

     def create_stock_picking(self, location_id, location_dest_id, purchase_order, picking_type_id=1):
          return self.caller.env['stock.picking'].create({
                        'move_type': 'direct',
                        'location_id': location_id,
                        'location_dest_id': location_dest_id,
                        'picking_type_id': picking_type_id,
                        'origin': purchase_order.name,
               })

     def create_stock_move(self, name_prefix, product_id, location_id, location_dest_id, picking_id, product_uom_qty, purchase_line_id=False):
          postfix = str(datetime.now())
          aName = name_prefix + '-' + postfix
          return self.caller.env['stock.move'].create({
                        'name': aName,
                        'company_id': 1,
                        'date': datetime.now(),
                        'date_expected': datetime.now(),
                        'product_id': product_id,
                        'product_uom_qty': product_uom_qty,
                        'product_uom': 1,
                        'location_id': location_id,
                        'location_dest_id': location_dest_id,
                        'procure_method': 'make_to_stock',
                        'picking_id': picking_id,
                        'purchase_line_id': purchase_line_id,
               })

     def create_stock_move_line(self, location_id, location_dest_id, picking_id, product, product_uom_qty):
          return self.caller.env['stock.move.line'].create({
                        'company_id': 1,
                        'date': datetime.now(),
                        'location_id': location_id,
                        'location_dest_id': location_dest_id,
                        'picking_id': picking_id,
                        'product_id': product.id,
                        'product_uom_id': product.uom_id.id,
                        'product_uom_qty': product_uom_qty,
               })
