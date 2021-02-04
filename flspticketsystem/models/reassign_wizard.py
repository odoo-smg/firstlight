# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ReAssign(models.TransientModel):
    """
        Class_Name: ReAssign
        Model_Name: flspticketsystem.assign
        Purpose:    To create a reassign model used in the wizard to RE-assign responsible
        Date:       Oct/6th/Tuesday/2020
        updated:
        Author:     Sami Byaruhanga
    """

    _name = 'flspticketsystem.reassign'
    _description = "Re assign"

    @api.model
    def default_get(self, fields):
        """
            Purpose: to get the default values from the ticket model and load in the wizard
        """
        res = super(ReAssign, self).default_get(fields)
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
            if 're_assign_date' in fields:
                res['assign_date'] = ticket.re_assign_date
            if 'analysis' in fields:
                res['analysis'] = ticket.analysis

        res = self._convert_to_write(res)
        return res

    # Assign fields
    ticket_id = fields.Many2one('flspticketsystem.ticket', string="Ticket")

    # Used in view form
    responsible = fields.Many2one('res.users', ondelete='cascade', string="Responsible", required='True',
        domain=lambda self: [('groups_id', 'in', self.env.ref('flspticketsystem.group_flspticketsystem_manager').id)],
        help='Once responsible assigned, ticket status is updated to in progress and no user edit is possible')

    analysis = fields.Text(string="Analysis", help='Enter what you want the assigned person to do with the ticket')
    short_description = fields.Char(string="Short Description", size=80, readonly=True, help='Was filled by user')

    # Used in assign button below to help in sending email
    re_assign_date = fields.Date(string="Re Assign Date")
    priority = fields.Selection([('P', 'Preventing operation'), ('M', 'Must have'), ('N', 'Nice to have')], string="Priority")

    # Methods
    def reassign(self):
        """
            Purpose: Button used in wizard to send the re-assigned email
        """
        # Here we are writing the info on the wizard on the ticket
        self.ensure_one()
        self.ticket_id.write({'analysis': self.analysis, })
        self.ticket_id.write({'responsible': self.responsible, })
        self.ticket_id.write({'status': 'inprogress', })
        self.ticket_id.write({'assign_date': self.re_assign_date, })

        self.env['flspautoemails.bpmemails'].send_email(self, 'TKT0004')
        return {'type': 'ir.actions.act_window_close'}








