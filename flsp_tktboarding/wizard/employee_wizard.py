# -*- coding: utf-8 -*-

from odoo import models, fields, api


class EmployeeWizard(models.TransientModel):
    """
        Class_Name: EmloyeeWizard
        Model_Name: "flsp_tktboarding_wizard"
        Purpose:    To help in the creation of the tickets for employee boarding
        Date:       April.22nd.2021.Thursday
        Author:     Sami Byaruhanga
    """
    _name = "flsp.tktboarding.wizard"
    _description = "FLSP Ticket Boarding Wizard"

    plan = fields.Many2one('hr.plan', string='Boarding Type', ondelete='cascade', required=True)
    tickets = fields.Many2many('flspticketsystem.boarding', ondelete='cascade', string="Ticket To create",
                             domain="[('boarding', '=', plan)]", required=True,)

    @api.onchange('plan')
    def add_tickets(self):
        """"
            Purpose:    Adding the tickets to create with on change method
        """
        tkts = self.env['flspticketsystem.boarding'].search([('boarding', '=', self.plan.id)])
        if self.plan:
            self.tickets = [(6, 0, tkts.ids)]

    def create_ticket(self):
        """
            Purpose:    To create the ticket for the boarding process
        """
        active_id = self.env.context.get('active_id')
        employee = self.env['hr.employee'].search([('id', '=', active_id)])
        for record in self.tickets:
            self.env['flspticketsystem.ticket'].create({
                'priority': 'M',
                'category_id': record.category_id.id,
                'short_description': record.short_description + " for " + employee.name,
                'detailed_description': record.detailed_description,
            })

