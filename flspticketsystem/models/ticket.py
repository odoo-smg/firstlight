# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError

class Ticket(models.Model):
    """
        Class_Name: Ticket
        Model_Name: flspticketsystem.ticket
        Purpose:    To help in the creation of the tickets
        Date:       sept/4th/friday/2020
        Updated:    Sept/22nd/Tuesday/2020
        Author:     Sami Byaruhanga
    """
    _name = 'flspticketsystem.ticket'
    _description = "Tickets"

    # User fields
    id = fields.Integer(index=True)
    start_date = fields.Date(string="Request date", default=fields.Date.today, required=True,
        help='Request date is set to default on today\'s date')
    requestor = fields.Many2one('res.users', string="Requested by", required=True, index=True,
        default=lambda self: self.env.user, help='Contact Developers if your name is not specified or information changed')
    priority = fields.Selection([('P', 'Preventing operation'), ('M', 'Must have'), ('N', 'Nice to have')], string="Priority",
        required=True, help='Set priority level where:\n* Preventing operation as extremely urgent \n* '
            ' Must have are key missing features in your system \n* '
            ' Nice to have are some suggested improvements for user interaction')
    category_id = fields.Many2one('flspticketsystem.category', ondelete='cascade', required=True,
        string="Category",  help='Choose the department/model your inquiring changes for')
    short_description = fields.Char(string="Short Description", size=80, required=True,
        help='Please provide a short description of the request')
    detailed_description = fields.Text(string="Detailed Description", required=True,
        help='Please provide a detailed description.\n "A problem well-stated is half-solved" - Charles Kettering')
    status = fields.Selection([('open', 'Open'), ('inprogress', 'In Progress'), ('close', 'Closed')],
        default='open', eval=True)

    # Admin related fields
    responsible = fields.Many2one('res.users', ondelete='set null', string="Responsible", index=True,
        domain=lambda self: [('groups_id', 'in', self.env.ref('flspticketsystem.group_flspticketsystem_manager').id)],
        help='Once responsible assigned, ticket status is updated to in progress and no user edit is possible')
    type = fields.Many2one('flspticketsystem.type', ondelete='cascade', string="Classification",
        help='Classify solution so we can reference for future debugging')
    complete_date = fields.Date(string="Completion Dates")
    analysis = fields.Text(string="Analysis")
    solution = fields.Text(string="Solution")
    color = fields.Integer() #related to kanban view
    send_user_email = fields.Boolean(default=True,
        help='Deactivate if you do not want to send user email upon creation of ticket')

#    attachment_ids = fields.Many2many('ir.attachment', 'ticket_attachment_rel' string='Attachments',
#        help='Attachments are linked to a document through model / res_id and to the message '
#             'through this field.')

    # Methods
    @api.model
    def create(self, values):
        """
            Purpose: Override create method, on creation an email is sent to the user if boolean is true in admin
             but if not its not sent upon creation
        """
        if values.get('send_user_email'):
            record = super(Ticket, self).create(values)
            body = '<p>Hi there, your ticket has been created with the following information:</p>'

            body += '<div style="padding-left: 30px; color:green;">'  # style = "text-align: center;"
            body += '<br/><p>Ticket ID: ' + str(record.id) + '<p>'
            body += '<p>Request date: ' + str(record.start_date) + ' <p>'
            body += '<p>Priority level: ' + str(
                dict(record._fields['priority'].selection).get(record.priority)) + ' <p>'
            body += '<p>Short description: ' + record.short_description + ' <p>'
            body += '</div>'

            body += '<br/> <p>Thank you!</p>'
            self.env['mail.mail'].create({
                'body_html': body,
                'subject': 'Request Open: Ticket ID-' + str(record.id),
                'email_to': 'ithelpdesk@smgrp.com',
                # self.responsible,  # will have to add the admin emails e.g iap@odoo.com
                'email_cc': False,
                'auto_delete': True,
            }).send()
            # record = super(Ticket, self).create(values)
        else:
            record = super(Ticket, self).create(values)
            # after fix emails here we will email it but up we will email it an user
        return record

    def button_assign(self):
        """
            Purpose: To call assign responsible wizard with context for the ticket
        """
        view_id = self.env.ref('flspticketsystem.assign_from_view').id
        name = 'Assign responsible'
        ticket_id = self.id
        return {
            'name': name,
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'flspticketsystem.assign',
            'view_id': view_id,
            'views': [(view_id, 'form')],
            'target': 'new',
            'context': {
                'default_ticket_id': ticket_id,
            }
        }

    def unlink(self):
        """
            Purpose: to prevent deleting of a ticket once in status inprogress and close
        """
        if self.status in ('inprogress'):
            raise UserError('You can not delete a ticket once In progress status')
        return super(Ticket, self).unlink()

    def button_close(self):
        """
            Purpose: To send an email as soon as ticket is closed and add completion date set
                    Only functional if the responsible field has been filled
        """
        today = fields.Date.today()
        if self.responsible:
            for r in self:
                r.write({'status': 'close'})
                r.complete_date = today

                body = '<p>Hi there, </p>'
                body += '<br/>'
                body += '<p>The ticket containing the following information has been closed:</p>'

                body += '<div style="padding-left: 30px; color: #9932CC">'
                body += '<br/><p>Ticket ID: ' + str(self.id) + '<p>'
                body += '<p>Request date: ' + str(self.start_date) + ' <p>'
                body += '<p>Priority level: ' + str(
                    dict(self._fields['priority'].selection).get(self.priority)) + ' <p>'
                body += '<p>Short description: ' + self.short_description + ' <p>'
                body += '<br/><p>Close date: ' + str(self.complete_date) + ' <p>'
                body += '<p>Solution: ' + str(self.solution) + ' <p>'
                body += '</div>'

                body += '<br/><p>Thank you!</p>'
                self.env['mail.mail'].create({
                    'body_html': body,
                    'subject': 'Request Closed: Ticket ID-' + str(self.id),
                    'email_from': 'ithelpdesk@smgrp.com',
                    'email_to': 'ithelpdesk@smgrp.com',  # self.requestor.login,
                    'auto_delete': True,
                }).send()






##USEFUL ONCE I NEED A WIZARD FOR CLOSE
    # def button_close(self):
    #     """
    #         Purpose: To call close ticket wizard with context for the ticket
    #     """
    #     view_id = self.env.ref('flspticketsystem.close_from_view').id
    #     name = 'Close ticket'
    #     ticket_id = self.id
    #     return {
    #         'name': name,
    #         'type': 'ir.actions.act_window',
    #         'view_mode': 'form',
    #         'res_model': 'flspticketsystem.close',
    #         'view_id': view_id,
    #         'views': [(view_id, 'form')],
    #         'target': 'new',
    #         'context': {
    #             'default_ticket_id': ticket_id,
    #         }
    #     }


    # @api.onchange('responsible')
    # def _inprogress(self):
    #     """
    #         Purpose: To change status to in progress as soon as responsible is filled
    #     """
    #     if self.responsible:
    #         self.status = 'inprogress'

    # def unlink(self):
    #     """
    #         Purpose: to prevent deleting of a ticket once in status inprogress and close
    #     """
    #     for order in self:
    #         if order.status in ('inprogress'): #, 'close'):
    #             raise UserError(
    #                 'You can not delete a ticket once In progress status')
    #     return super(Ticket, self).unlink()

    # @api.model
    # def create(self, values):
    #     """
    #         Purpose: Override create method, on creation an email is sent to the user if boolean is true in admin
    #          but if not its not sent upon creation
    #     """
    #     if values.get('send_user_email'):
    #         body = '<p>Hi there, your ticket has been created with the following information.</p>'
    #         body += '  <br/> <p>Request date: '+ +'<p>'
    #         body += '  <br/> <p> Access all your tickets on link below<p>'
    #         body += '  <br/> <p> Access all your tickets on link below<p>'
    #         body += '<br/><br/><br/>'
    #         body += '<div style = "text-align: center;" >'
    #         body += '  <a href = "/web#action=635&model=flspticketsystem.ticket&view_type=list&cids=&menu_id=420" style = "background: #1abc9c; padding: 20px; text-decoration: none; color: #fff; border-radius: 5px; font-size: 16px;" class ="o_default_snippet_text">Access Tickets</a>'
    #         body += '  <br/><br/>'
    #         body += '</div>'
    #         body += '<p>Thank you!</p>'
    #         self.env['mail.mail'].create({
    #             'body_html': body,
    #             'subject': 'Ticket request Open',
    #             'email_to': 'ithelpdesk@smgrp.com', #self.responsible,  # will have to add the admin emails e.g iap@odoo.com
    #             'email_cc': False,
    #             'auto_delete': True,
    #         }).send()
    #         record = super(Ticket, self).create(values)
    #     else:
    #         record = super(Ticket, self).create(values)
    #         #after fix emails here we will email it but up we will email it an user
    #     return record

    # @api.model
    # def create(self, values):
    #     """
    #         Purpose: On creation an email is sent to the user and it team
    #     """
    #             # r.active = True
    #     # Code before create: send email on creation
    #     body = '<p>Hi there, your ticket has been created.</p>'
    #     body += '  <br/>'
    #     body += '<p>Thank you!</p>'
    #     self.env['mail.mail'].create({
    #         'body_html': body,
    #         'subject': 'Ticket request Open',
    #         'email_to': self.responsible,  #will have to add the admin emails
    #         'auto_delete': True,
    #     }).send()
    #
    #     record = super(Ticket, self).create(values)
    #     # Code after create
    #     return record

    ##Not needed yet but i limit the visibility to only the managers for reopening tickets
    # def button_reopen(self):
    #     for r in self:
    #         r.status = 'open'
    #         r.complete_date = 0
    #         # r.active = True
    #
    #         body = '<p>Hi there, </p>'
    #         body += '<br/>'
    #         body += '<p>The ticket containing the following description: ' + self.short_description + ' has been re-opened.</p>'
    #         body += '<br/><br/><br/>'
    #         body += '<br/><br/><br/>'
    #         body += '<div style = "text-align: center;" >'
    #         body += '<p>Can access tickets on link below</p>'
    #         body += '  <a href = "/web#action=630&amp;model=flspticketsystem.ticket&amp;view_type=list&amp;cids=1&amp;menu_id=ticket_menu" style = "background: #1abc9c; padding: 20px; text-decoration: none; color: #fff; border-radius: 5px; font-size: 16px;" class ="o_default_snippet_text">Access Tickets</a>'
    #         body += '  <br/><br/><br/>'
    #         body += '</div>'
    #         body += '<p>Thank you!</p>'
    #         self.env['mail.mail'].create({
    #             'body_html': body,
    #             'subject': 'Ticket request Opened',
    #             'email_to': self.requestor.login,
    #             'auto_delete': True,
    #         }).send()
