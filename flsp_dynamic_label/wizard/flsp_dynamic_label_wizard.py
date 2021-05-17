# -*- coding: utf-8 -*-
from odoo import models, fields, api

class FlspDynamicLabelWizard(models.TransientModel):
    """
        class_name: FlspDynamicLabelWizard
        model_name: flsp.dynamic.label.wizard
        Purpose:    To call wizard to select the template to print
        Date:       March.15th.2021.M
        Author:     Sami Byaruhanga
        Note:       Some of the logic and code is borrowed from external source
                    https://apps.odoo.com/apps/modules/13.0/label/
    """
    _name = 'flsp.dynamic.label.wizard'
    _description = "FLSP Dynamic Label Wizard"

    template_name = fields.Many2one('flsp.dynamic.label', 'Template Name', required=True)
    result = fields.Text(string='ZPL result')
    active_model = fields.Integer(string='active model')
    list_models = fields.Char(string='list of models')

    def print_report(self):
        """
            Purpose:    To call return_zpl from flsp.dynamic.label, Save the output as results
            Returns:    Txt file on the system with the label information
        """
        template = self.template_name
        zpl_output = template.return_zpl()
        self.result = zpl_output

        # print(self.env.context.get('active_id'))
        # print(self._context)
        return self.env.ref('flsp_dynamic_label.dynamic_label').report_action(self)

    @api.onchange('template_name')
    def getting_domain(self):
        active_model = self.env.context.get('active_model')
        # self.active_model = str(active_model)
        # print(active_model)
        for line in self.env['ir.model'].search([]):
            if active_model in line.model:
                self.active_model = line.id
                break

        list_of_models = self.list_of_models()
        self.list_models = list_of_models


    def list_of_models(self):
        models = self.env['flsp.dynamic.label'].search([])
        list_of_models = []
        for line in models:
            list_of_models.append(line.model_id.id)
        return list_of_models