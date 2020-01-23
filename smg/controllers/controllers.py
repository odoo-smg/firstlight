# -*- coding: utf-8 -*-
# from odoo import http


# class Smg(http.Controller):
#     @http.route('/smg/smg/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/smg/smg/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('smg.listing', {
#             'root': '/smg/smg',
#             'objects': http.request.env['smg.smg'].search([]),
#         })

#     @http.route('/smg/smg/objects/<model("smg.smg"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('smg.object', {
#             'object': obj
#         })
