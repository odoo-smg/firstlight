# -*- coding: utf-8 -*-
from odoo import models, fields, api

class FlspVersionControl(models.Model):
    """
        class_name: FlspVersionControl
        model_name: inherits the flspticketsytem.ticket
        Purpose:    To help in creating version control for the ticketing system
        Date:       Feb/02/2021/T
        Author:     Sami Byaruhanga
    """
    _inherit = "flspticketsystem.ticket"

    version_type = fields.Selection([('N', 'New Release'), ('B', 'Bug Fix/Improvement'), ('O', 'No coding related')], string='Type',
                                    default='O')
    version_description = fields.Text(string='Description') #add domain bassed off selection other than O
    model_id = fields.Many2one('ir.model', string='Model', ondelete='cascade')
    version_num = fields.Float(string='Version #')
    # active = fields.Boolean(default=True)

    @api.onchange('version_type')
    def _change_version_num(self):
        """
            Purpose: To change the version number according to selection
        """
        if self.version_type == 'N':
            self.version_num = 13.01
        elif self.version_type == 'B':
            # print("working on bug control")
            self._cr.execute(
                '''select max(tkt.version_num) from flspticketsystem_ticket as tkt
                inner  join ir_model as ir
                on     tkt.model_id = ir.id
                where  ir.name like '%''' + self.model_id.name + '''%' and tkt.status='close' ''')
            table = self._cr.fetchall()
            # print("--printing table fetch")
            # print(table)
            for line in table:
                if (line[0]) == None:
                    print('type is none')
                    break
                value = float(line[0])
                version = value
                self.version_num = version+.01
                # print("###New version num######")
                # print(self.version_num)
                # raise ValidationError("Please enter Forecast within the next 12 months only")
        else:
            self.version_num = 13.01

