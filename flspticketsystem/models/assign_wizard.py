# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Assign(models.TransientModel):
    """
        Class_Name: Assign
        Model_Name: flspticketsystem.assign
        Purpose:    To create an assign model used in the wizard to assign responsible
        Date:       sept/21st/Monday/2020
        Author:     Sami Byaruhanga
    """

    _name = 'flspticketsystem.assign'
    _description = "Assign"

    @api.model
    def default_get(self, fields):
        """
            Purpose: to get the default values from the ticket model and load in the wizard
        """
        res = super(Assign, self).default_get(fields)
        ticket_id = self.env.context.get('active_id') or self.env.context.get('default_ticket_id')
        if ticket_id:
            ticket = self.env['flspticketsystem.ticket'].browse(ticket_id)
        if ticket.exists():
            if 'ticket_id' in fields:
                res['ticket_id'] = ticket.id
            if 'short_description' in fields:
                res['short_description'] = ticket.short_description
            if 'priority' in fields:
                res['priority'] = ticket.priority

        res = self._convert_to_write(res)
        return res

    # Assign fields
    ticket_id = fields.Many2one('flspticketsystem.ticket', string="Ticket")

    # Used in view form
    responsible = fields.Many2one('res.users', ondelete='cascade', string="Responsible", required='True',
        domain=lambda self: [('groups_id', 'in', self.env.ref('flspticketsystem.group_flspticketsystem_manager').id)],
        help='Once responsible assigned, ticket status is updated to in progress and no user edit is possible')
    analysis = fields.Text(string="Analysis", required='True', help='Enter what you want the assigned person to do with the ticket')
    short_description = fields.Char(string="Short Description", size=80, readonly=True, help='Was filled by user')
    # urgency = fields.Selection([('A', 'As soon as possible'), ('B', 'With in 1-3 days'), ('C', 'Whenever time permits')],
    #     string="Urgency level", help='Let Assigned know how long he has to complete the ticket')

    # Used in assign button below to help in sending email
    assign_date = fields.Date(string="Assign Date")
    priority = fields.Selection([('P', 'Preventing operation'), ('M', 'Must have'), ('N', 'Nice to have')], string="Priority")

    # Methods
    def assign(self):
        """
            Purpose: Button used in wizard to send the assigned email only if responsible field is filled
        """
        # Here we are writing the info on the wizard on the ticket
        self.ensure_one()
        self.ticket_id.write({'analysis': self.analysis, })
        self.ticket_id.write({'responsible': self.responsible, })
        self.ticket_id.write({'status': 'inprogress', })

        today = fields.Date.today()
        assign_date = today
        body = '<p>Hi there, </p>'
        body += '<br/>'
        body += '<p>The ticket containing the following information has been assigned to you:</p>'

        body += '<div style="padding-left: 30px; color:red; ">'
        body += '<br/><p>Ticket ID: ' + str(self.ticket_id.id) + '<p>'
        body += '<p>Assign date: ' + str(assign_date) + ' <p>'
        body += '<p>Priority level: ' + str(
            dict(self._fields['priority'].selection).get(self.priority)) + ' <p>'
        body += '<p>Short description: ' + self.short_description + ' <p>'
        body += '<p>Analysis: ' + str(self.analysis) + ' <p>'
        # body += '<p>Urgency Level: ' + str(
        #     dict(self._fields['urgency'].selection).get(self.urgency)) + ' <p>'
        body += '</div>'

        body += '<br/><p>Thank you!</p>'
        self.env['mail.mail'].create({
            'body_html': body,
            'subject': 'Assigned: Ticket ID-' + str(self.ticket_id.id),
            'email_from': 'ithelpdesk@smgrp.com',
            'email_to': 'ithelpdesk@smgrp.com',  # self.requestor.login,
            'auto_delete': True,
        }).send()

        return {'type': 'ir.actions.act_window_close'}








