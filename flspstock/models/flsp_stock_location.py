from odoo import models, api
from odoo.exceptions import ValidationError

class flspStockLocation(models.Model):
    _inherit = 'stock.location'

    @api.constrains('complete_name')
    def _constraint_only_unique_complete_name(self):
        """
            Date:    Mar/16th/2021/Tuesday
            Purpose: To create only unique "complete name" (complete name = Parent Location / Location Name)
                     To raise exception if the complete name exists
            Assumption: There may be duplicated complete names existing in database, so _sql_constraints would not work
            Author: Perry He
        """
        self._cr.execute("SELECT complete_name FROM stock_location WHERE complete_name = %s", (self.complete_name,))
        res = self._cr.fetchall()  # returns all
        if res:
            raise ValidationError('Please use another Location Name. The Name already exists: ' + self.complete_name)

    def copy(self, default=None):
        """
            Date:    Mar/16th/2021/Tuesday
            Purpose: To add string "(copy)" in Location Name when to click "Duplicate" button for given Location;
                    This method lets "Duplicate" button work when "_constraint_only_unique_complete_name" takes effect;
                    The behavior works in the same way as for Model "ProductTemplate";
            Author: Perry He
        """
        if default is None:
            default = {}
        if 'name' not in default:
            default['name'] = ("%s (copy)") % self.name
        return super(flspStockLocation, self).copy(default=default)