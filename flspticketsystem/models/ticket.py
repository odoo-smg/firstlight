# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError

class Ticket(models.Model):
    """
        Class_Name: Ticket
        Model_Name: flspticketsystem.ticket
        Purpose:    To help in the creation of the tickets
        Date:       sept/4th/friday/2020
        Updated:    Oct/6th/Tuesday/2020
        Author:     Sami Byaruhanga
    """
    _name = 'flspticketsystem.ticket'
    _description = "Tickets"
    # _rec_name = 'id'
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
        readonly=True, help='Once responsible assigned, ticket status is updated to in progress and no user edit is possible')
    type = fields.Many2one('flspticketsystem.type', ondelete='cascade', string="Classification",
        help='Classify solution so we can reference for future debugging')
    complete_date = fields.Date(string="Completion Dates", readonly=True)
    analysis = fields.Text(string="Analysis")
    solution = fields.Text(string="Solution")
    color = fields.Integer() #related to kanban view
    send_user_email = fields.Boolean(default=True,
        help='Deactivate if you do not want to send user email upon creation of ticket')

    attachment_ids = fields.Many2many('ir.attachment', string='Attachments',
        help='Add any attachments that will help in solving your request')

    # attachment_ids = fields.Binary(string="Attachments", attachment=True)

    assign_date = fields.Date(string="Assign Date")
    re_assign_date = fields.Date(string="Re Assign Date")

    # trying many2many
    share = fields.Many2many('res.users', string="Share Ticket with",
        domain=lambda self: [('groups_id', 'in', self.env.ref('flspticketsystem.group_flspticketsystem_user').id)],)

    # Methods
    @api.model
    def create(self, values):
        """
            Purpose: Override create method, on creation an email is sent to the user if boolean is true in admin
             but if not its not sent upon creation
        """
        if values.get('send_user_email'):
            record = super(Ticket, self).create(values)
            self.env['flspautoemails.bpmemails'].send_email(record, 'TKT0001')
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
                self.env['flspautoemails.bpmemails'].send_email(self, 'TKT0003')

    def button_re_assign(self):
        """
            Purpose: To call re-assign wizard with context for the ticket
        """
        view_id = self.env.ref('flspticketsystem.re_assign_from_view').id
        name = 'Re-Assign responsible'
        ticket_id = self.id
        return {
            'name': name,
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'flspticketsystem.reassign',
            'view_id': view_id,
            'views': [(view_id, 'form')],
            'target': 'new',
            'context': {
                'default_ticket_id': ticket_id,
            }
        }
    #
    # def name_get(self):
    #     return [(self.id, "%s (%s)" % (list.short_description, list.id)) for list in self]













