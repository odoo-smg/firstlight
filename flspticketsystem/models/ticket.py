# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Ticket(models.Model):
    """
        Class_Name: Ticket
        Model_Name: flspticketsystem.ticket
        Purpose:    To help in the creation of the tickets
        Date:       sept/4th/friday/2020
        Author:     Sami Byaruhanga
    """
    _name = 'flspticketsystem.ticket'
    _description = "Tickets"

    id = fields.Integer(index=True)
    start_date = fields.Date(string="Request date", default=fields.Date.today, required=True,
        help='Request date is set to default on todays date')
    requestor = fields.Many2one('res.users', string="Requestor", required=True, index=True,
        help='Enter your user name')

    priority = fields.Selection([('P', 'Preventing operation'), ('M', 'Must have'), ('N', 'Nice to have')], string="Priority",
         required=True, help='Set priority level where:\n* Preventing operation as extremely urgent \n* '
            ' Must have are key missing features in operation \n* '
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
        help='Once responsible assigned, ticket status is updated to in progress and no user edit is possible')
    complete_date = fields.Date(string="Completion Dates")
    analysis_solution = fields.Text(string="Analysis/Solution")
    color = fields.Integer()

    email_user_on_ticket_creation = fields.Boolean(default=True,
        help='Deactivate if you do not want to send user email upon creation of ticket') #will have to be used as email to user on open

    # @api.onchange('email_user')
    @api.model
    def create(self, values):
        """
            Purpose: On creation an email is sent to the user if boolean is true in admin
             but if not its not sent upon creation
        """
        if values.get('email_user_on_ticket_creation'):
            body = '<p>Hi there, your ticket has been created.</p>'
            body += '  <br/> <p> Access all your tickets on link below<p>'
            body += '<br/><br/><br/>'
            body += '<div style = "text-align: center;" >'
            body += '  <a href = "/web#action=635&model=flspticketsystem.ticket&view_type=list&cids=&menu_id=420" style = "background: #1abc9c; padding: 20px; text-decoration: none; color: #fff; border-radius: 5px; font-size: 16px;" class ="o_default_snippet_text">Access Tickets</a>'
            body += '  <br/><br/>'
            body += '</div>'
            body += '<p>Thank you!</p>'
            self.env['mail.mail'].create({
                'body_html': body,
                'subject': 'Ticket request Open',
                'email_to': 'ithelpdesk@smgrp.com', #self.responsible,  # will have to add the admin emails e.g iap@odoo.com
                'email_cc': False,
                'auto_delete': True,
            }).send()
            record = super(Ticket, self).create(values)
        else:
            record = super(Ticket, self).create(values)
        return record

    @api.onchange('responsible')
    def _inprogress(self):
        """
            Purpose: To change status to in progress as soon as responsible is filled
        """
        if self.responsible:
            self.status = 'inprogress'

    # Button for updating the status and the completion date accordingly
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
                body += '<p>The ticket containing the following description: ' + self.short_description + ' has been solved.</p>'
                body += '<br/> <p> Access all your tickets on link below<p>'
                body += '<br/><br/>'
                body += '<div style = "text-align: center;" >'
                body += '  <a href = "/web#action=635&model=flspticketsystem.ticket&view_type=list&cids=&menu_id=420" style = "background: #1abc9c; padding: 20px; text-decoration: none; color: #fff; border-radius: 5px; font-size: 16px;" class ="o_default_snippet_text">Access Tickets</a>'
                body += '  <br/><br/><br/>'
                body += '</div>'
                body += '<p>Thank you!</p>'
                self.env['mail.mail'].create({
                    'body_html': body,
                    'subject': 'Ticket request Closed',
                    'email_from': 'ithelpdesk@smgrp.com',
                    'email_to': self.requestor.login,
                    'auto_delete': True,
                }).send()

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

    ##Not needed yet but i limit the visibility to only the managers
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
