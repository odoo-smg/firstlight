from odoo import models, fields, api


class Contacts(models.Model):
    _name = 'flsp.contact'
    _description = "Customer Contacts"
    _check_company_auto = True

    def _get_default(self):
        current_id = self._context.get('partner_id')
        return current_id

    sequence = fields.Integer('Sequence', default=1, help="The first in the sequence is the default one.")
    partner_id = fields.Many2one('res.partner', string='Customer', required=True, default=_get_default, readonly=True)
    name = fields.Char(string="Name", required=True)
    job_position = fields.Char(string="Job Position")
    email = fields.Char(string="Email")
    phone = fields.Char(string="Phone")
    notes = fields.Text(string="Notes")
