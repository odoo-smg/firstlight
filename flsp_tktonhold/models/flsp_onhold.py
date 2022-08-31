# -*- coding: utf-8 -*-
from odoo import models, fields, api

class FlspTktOnhold(models.Model):
    """
        class_name: FlspTktOnhold
        model_name: inherits the flspticketsytem.ticket
        Purpose:    To help in creating onhold for the ticket model
        Date:       Feb/03/2021/W
        Author:     Sami Byaruhanga
    """
    _inherit = "flspticketsystem.ticket"

    # Developers section
    tkt_eta = fields.Date(string='Ticket ETA')
    other_notes = fields.Text(string='Other Notes')
    # OnHold fields
    status = fields.Selection(selection_add=[('onhold', 'On Hold')], ondelete={"onhold": "set default"})
    reason = fields.Text(string='OnHold reason', tracking=True)
    onhold_date = fields.Date(string="OnHold Date")
    onhold_user = fields.Many2one('res.users', ondelete='cascade', string="OnHold by")

    def button_onhold(self):
        """
            Purpose: To call onhold wizard with context for the ticket
        """
        view_id = self.env.ref('flsp_tktonhold.flsp_tktonhold_from_view').id
        name = 'Put ticket OnHold'
        ticket_id = self.id
        return {
            'name': name,
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'flspticketsystem.onhold',
            'view_id': view_id,
            'views': [(view_id, 'form')],
            'target': 'new',
            'context': {
                'default_ticket_id': ticket_id,
            }
        }

    @api.depends('status')
    def button_remove_hold(self):
        """
            Purpose: To remove from hold
        """
        for line in self:
            if line.status == 'onhold':
                if line.responsible:
                    line.write({'status': 'inprogress'})
                    self.env['flspautoemails.bpmemails'].send_email(self, 'TKT0006')
                else:
                    line.write({'status': 'open'})
                    self.env['flspautoemails.bpmemails'].send_email(self, 'TKT0006')


class OnHold(models.TransientModel):
    """
        Class_Name: OnHold
        Model_Name: flspticketsystem.onhold
        Purpose:    To create a onhold model used in the wizard to put ticket on hold
        Date:       Feb/3rd/Wednesday/2021
        Author:     Sami Byaruhanga
    """

    _name = 'flspticketsystem.onhold'
    _description = "OnHold"

    @api.model
    def default_get(self, fields):
        """
            Purpose: to get the default values from the ticket model and load in the wizard
        """
        res = super(OnHold, self).default_get(fields)
        ticket_id = self.env.context.get('active_id') or self.env.context.get('default_ticket_id')
        if ticket_id:
            ticket = self.env['flspticketsystem.ticket'].browse(ticket_id)
        if ticket.exists():
            if 'ticket_id' in fields:
                res['ticket_id'] = ticket.id
            # if 'reason' in fields:
            #     res['reason'] = ticket.reason

        res = self._convert_to_write(res)
        return res
    ticket_id = fields.Many2one('flspticketsystem.ticket', string="Ticket")

    # Used in view form
    reason = fields.Text(string="Reason", help='Enter reason to put ticket on hold', required=True)
    onhold_date = fields.Date(string="OnHold Date", default=fields.Date.today)
    onhold_user = fields.Many2one('res.users', ondelete='cascade', string="OnHold user", required=True,
        default=lambda self: self.env.user,)

    def onhold(self):
        """
            Purpose: Button used in wizard put ticket onhold
        """
        # Here we are writing the info on the wizard on the ticket
        self.ensure_one()
        self.ticket_id.write({'reason': self.reason, })
        self.ticket_id.write({'onhold_date': self.onhold_date,})
        self.ticket_id.write({'onhold_user': self.onhold_user,})
        self.ticket_id.write({'status': 'onhold', })

        self.env['flspautoemails.bpmemails'].send_email(self, 'TKT0005')
        return {'type': 'ir.actions.act_window_close'}
