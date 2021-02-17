# -*- coding: utf-8 -*-
from odoo import models, fields, api

class FlspVersionControl(models.Model):
    """
        class_name: FlspVersionControl
        model_name: inherits the flspticketsytem.ticket
        Purpose:    To help in creating version control for the ticketing system
        Date:       Feb/02/2021/T
        Author:     Sami Byaruhanga
        Updated:    Feb/17th/W to use ir.mnodule.module table and increment version # for bug fixes using clock system
    """
    _inherit = "flspticketsystem.ticket"

    version_type = fields.Selection([('N', 'New Release'), ('B', 'Bug Fix/Improvement'), ('O', 'No coding related')], string='Type',
                                    default='O')
    version_description = fields.Text(string='Description')
    model_id = fields.Many2one('ir.module.module', string='Model', ondelete='cascade')
    version_num = fields.Char(string='Version #')
    # active = fields.Boolean(default=True)

    # ir_module_module.latest_version
    @api.onchange('model_id', 'version_type')
    def _change_version_num(self):
        """
            Purpose: To change the version number according to selection
        """
        latest_num = self.model_id.installed_version
        if self.version_type == 'N':
            self.version_num = latest_num
        elif self.version_type == 'B':
            print("working on bug fix")
            self._cr.execute(
                '''select max(tkt.version_num) from flspticketsystem_ticket as tkt
                inner  join ir_module_module as ir
                on     tkt.model_id = ir.id
                where  ir.name like '%''' + self.model_id.name + '''%' and tkt.status='close' ''')
            table = self._cr.fetchall()
            # print("---------------table fetch------------")
            # print(table) #result is string
            for line in table:
                if (line[0]) == None:
                    # print('type is none')
                    break
                value = line[0]
                # print("Value before modification-------------------")
                # print(value)
                first = int(value[:2])
                second = int(value[3])
                third = int(value[5])
                forth = int(value[7])
                forth += 1
                if forth > 9:
                    forth = 0
                    third += 1
                    if third >= 9:
                        third = 0
                        second += 1
                value = str(first) + "." + str(second) + "." + str(third) + "." + str(forth)
                print("*******value after modification")
                print(value)
                self.version_num = value
                # raise ValidationError("Please enter Forecast within the next 12 months only")
        # else:
        #     self.version_num = 13.01

