# -*- coding: utf-8 -*-

from odoo import models, fields, api
#View# relates to view
#test# means testing some thing out
# addons aka refinements
class Category(models.Model):
    _name = 'flspticketsystem.category'
    _description = "Category"

    name = fields.Char(string="Category", required=True)
    description = fields.Text() ##might have to delete this



class Ticket(models.Model):
    _name = 'flspticketsystem.ticket'
    _description = "Tickets"

    # 100 --> ID auto generated
    id = fields.Integer(index=True)

    # 100 --> Default today as start date
    start_date = fields.Date(default=fields.Date.today)

    # 100 --> Link to the category table
    category_id = fields.Many2one('flspticketsystem.category', ondelete='cascade', string="Category", required=True)

#    # 90 -->Add 3 priority levels with different colors
    priority = fields.Selection([('P', 'Preventing operation'), ('M', 'Must have'), ('N', 'Nice to have')], string="Priority", required=True)

    # 100 --> 80 char short description and unlimited detailed
    short_description = fields.Char(string="Short Description", required=True, size=80)
    detailed_description = fields.Text(string="Detailed Description", required=True)

    # 100 --> Status linked to the completion dates
    status = fields.Selection([('open', 'Open'), ('close', 'Closed')], default='open')
    complete_date = fields.Date(string="Completion Dates")
    # active = fields.Boolean(default=True) #i don't think i need active coz status is enough

    # 100 --> Text field for Admin
    analysis_solution = fields.Text(string="Analysis/Solution")
    color = fields.Integer() ##for KANBAN VIEW, will have to find a way to color code based off module



    # 80 -->Access to me and Alex and limit user to see only there tickets
    # responsible = fields.Char(string="Responsible", index=True)#test#quick check wat index it
                                                            #Can only be filled by ERP team
    responsible = fields.Many2one('res.users',
        ondelete='set null', string="Responsible", index=True) ##not sure why many2one here. Better option to jst have erp team???


    #button for updating the status and the completion date accordingly
    def button_close(self):
        today = fields.Date.today()
        for r in self:
            r.write({'status': 'close'})
            # r.complete_date = fields.Date.today()
            r.complete_date = today
            # r.active = False

        body = '<p>Hi there, </p>'
        body += '<br/>'
        body += '<p>this is my test.</p>'
        body += '<br/><br/><br/>'
        body += '<br/><br/><br/>'
        body += '</div>'
        body += '<p>Well done!</p>'
        self.env['mail.mail'].create({
            'body_html': body,
            'subject': 'My change on status',
            'email_to': "alexandresousa@smartrendmfg.com",
            'auto_delete': True,
        }).send()



    def button_reopen(self):
        for r in self:
            r.status = 'open'
            r.complete_date = 0
            # r.active = True


    # def action_quotation_send(self):
    #     ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
    #     self.ensure_one()
    #     template_id = self._find_mail_template()
    #     lang = self.env.context.get('lang')
    #     template = self.env['mail.template'].browse(template_id)
    #     if template.lang:
    #         lang = template._render_template(template.lang, 'flspticketsystem.ticket', self.ids[0])
    #     ctx = {
    #         'default_model': 'flspticketsystem.ticket',
    #         'default_res_id': self.ids[0],
    #         'default_use_template': bool(template_id),
    #         'default_template_id': template_id,
    #         'default_composition_mode': 'comment',
    #         'mark_so_as_sent': True,
    #         'custom_layout': "mail.mail_notification_paynow",
    #         'proforma': self.env.context.get('proforma', False),
    #         'force_email': True,
    #         'model_description': self.with_context(lang=lang).type_name,
    #     }
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'view_mode': 'form',
    #         'res_model': 'mail.compose.message',
    #         'views': [(False, 'form')],
    #         'view_id': False,
    #         'target': 'new',
    #         'context': ctx,
    #     }
    #
    # def _find_mail_template(self, force_confirmation_template=False):
    #     template_id = False
    #
    #     if force_confirmation_template or (self.status == 'close' and not self.env.context.get('proforma', False)):
    #         template_id = int(self.env['ir.config_parameter'].sudo().get_param('sale.default_confirmation_template'))
    #         template_id = self.env['mail.template'].search([('id', '=', template_id)]).id
    #         if not template_id:
    #             template_id = self.env['ir.model.data'].xmlid_to_res_id('sale.mail_template_sale_confirmation',
    #                                                                     raise_if_not_found=False)
    #     if not template_id:
    #         template_id = self.env['ir.model.data'].xmlid_to_res_id('sale.email_template_edi_sale',
    #                                                                 raise_if_not_found=False)
    #
    #     return template_id
























