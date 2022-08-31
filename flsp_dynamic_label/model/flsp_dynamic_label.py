# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import ValidationError

class FlspDynamicLabel(models.Model):
    """
        class_name: FlspDynamicLabel
        model_name: flsp.dynamic.label
        Purpose:    To create templates that will be called in the wizard to print report
        Date:       March.15th.2021.M
        Author:     Sami Byaruhanga
        Note:       Some of the logic and code is borrowed from external source
                    https://apps.odoo.com/apps/modules/13.0/label/
    """
    _name = 'flsp.dynamic.label'
    _description = "FLSP Dynamic Label"
    _rec_name = 'template_name'

    id = fields.Integer(index=True)
    template_name = fields.Char(string='Template Name', required=True)#, copy=False)
    #model_id = fields.Many2one("ir.model", "Model", required=True)#, copy='False')
    model_id = fields.Many2one("ir.model", "Model", required=True, ondelete='cascade')#, copy='False')
    template_code = fields.Text(string='Report Code', required=True)#, copy=False)
    created_by = fields.Many2one('res.users', string="Created By", default=lambda self: self.env.user)#, copy=False)
    create_date = fields.Date(string="Create date", default=fields.Date.today)#, copy=False)
    create_date = fields.Date(string="Create date", default=fields.Date.today)#, copy=False)
    purpose = fields.Text(string="Purpose")
    ref_ir_act_report = fields.Many2one("ir.actions.act_window", "Add to actions", readonly=True)

    dictionary = fields.Text(string="Dictionary")
    dic_preview = fields.Text(string='Dic preview')
    zpl_preview = fields.Text(string="Zpl Preview")

    action_exists = fields.Boolean(string='Action for model exists')

    @api.onchange('model_id')
    def onchange_model_id(self):
        """
        Purpose: To see if the model has a menu already
        """
        print('**************************Executing*******************')
        models = self.env['flsp.dynamic.label'].search([])
        models_ids = models.model_id
        if self.model_id:
            if self.model_id in models_ids:
                self.action_exists = True
                print('action exists')

    def create_action(self):
        """
        Purpose:    To add the wizard on action in the model
        """
        vals = {}
        action_obj = self.env["ir.actions.act_window"]
        for data in self.browse(self.ids):
            # button_name = ("Dynamic Label (%s)") % data.template_name
            button_name = ("Dynamic Label")
            vals["ref_ir_act_report"] = action_obj.create(
                {
                    "name": button_name,
                    "type": "ir.actions.act_window",
                    "res_model": "flsp.dynamic.label.wizard",
                    # "binding_view_types": "form",
                    "context": "{'flsp_dynamic_label_test' : %d}" % (data.id),
                    "view_mode": "form", #,tree",
                    "target": "new",
                    "binding_model_id": data.model_id.id,
                    "binding_type": "action",
                }
            )

        if self.action_exists:
            print('action exists')
        else:
            self.write({"ref_ir_act_report": vals.get("ref_ir_act_report", False).id})
            self.action_exists = True
        return True

    def unlink_action(self):
        """
        Purpose:    To remove the action from the model
        """
        self.action_exists = False
        for template in self:
            if template.ref_ir_act_report.id:
                template.ref_ir_act_report.unlink()
        return True

    @api.model
    def _rule_eval(self, rule, model=None, dict=None, save_log=False):
        if rule:
            context = {'model': model,
                       'dictionary': dict,
                       'self': self,
                       'object': self.id,
                       'pool': self.pool,
                       'cr': self._cr,
                       'uid': self._uid,
                       }
            try:
                safe_eval(rule,
                          context,
                          mode='exec',
                          nocopy=True)  # nocopy allows to return 'result'
            except Exception:
                if save_log:
                    pass
                else:
                    raise ValidationError("Wrong python code defined for zpl code" + self.template_name + ". Code:" + rule)
                return False
            return context.get('result', False)

    def update_zpl_preview(self):
        """
        Purpose:  To update the preview with the code the user entered so we can get the zpl preview
        """
        context = self._rule_eval(self.dic_preview, self)
        body_calc = self._rule_eval(self.template_code, self, context)
        # if body_calc:
        #     body = self._rule_eval(self.template_code, self, context)
        # print(body)
        self.zpl_preview = body_calc

        model = self.env['flsp.dynamic.label'].search([])
        for line in model:
            print(line.model_id)
        print(model.model_id)

    def return_zpl(self):
        """
        Purpose:    To be called in the wizard inorder to return the template
        Returns:    Zpl code
        """
        context = self._rule_eval(self.dictionary, self)
        body_calc = self._rule_eval(self.template_code, self, context)
        # if body_calc:
        #     body = self._rule_eval(self.template_code, self, context)
        return body_calc
