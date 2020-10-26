# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class KsFilePreview(http.Controller):
    # Controller: Get the file details
    @http.route(['/get/record/details'], type='json', auth="public", methods=['POST'], website=True)
    def get_record_data(self, res_id=False, model=False, size=False, res_field=False, **kw):
        """
        to search the attachment files using res_id, model and res_field
        :param res_id: current res id
        :param model: current model
        :param size: file size(int)
        :param res_field: string
        :param kw: empty
        :return: dictionary of file name, id and mimetype
        """
        data_file = None
        if res_id and model and res_field and size:
            # Using query as unable to find the data
            query = """select id from ir_attachment 
                where res_model=%s and 
                res_id=%s and 
                res_field=%s"""
            request.env.cr.execute(query, (model, res_id, res_field,))
            # request.env['ir.attachment'].sudo().search([('res_model', '=', model), ('res_id', '=', res_id), ('res_field', '=', res_field)])
            attachment_ids = request.env.cr.fetchall()
            if attachment_ids:
                attachment_ids = [t[0] for t in attachment_ids]
                datas = request.env['ir.attachment'].sudo().browse(attachment_ids)
                if datas and len(datas) == 1:
                    return {
                        'name': datas.name or datas.dispay_name,
                        'id': datas.id,
                        'type': datas.mimetype,
                    }
                elif datas:
                    if size[-2:] in ('Kb', 'kb'):
                        div = 1024
                    elif size[-2:] in ('Mb', 'mb'):
                        div = 1024 * 1024
                    elif size[-5:] in ('bytes', 'Bytes'):
                        div = 1
                        size = size[:-3]
                    else:
                        return data_file

                    for d in datas:
                        if float(size[:-3]) == round(d.file_size / div, 2):
                            data_file = {
                                'name': d.name or d.dispay_name,
                                'id': d.id,
                                'type': d.mimetype,
                            }
                            break
        return data_file
