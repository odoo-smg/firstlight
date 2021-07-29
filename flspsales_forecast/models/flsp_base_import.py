from odoo import models
import logging
_logger = logging.getLogger(__name__)

class FLSPImport(models.TransientModel):
    _inherit = 'base_import.import'

    def parse_preview(self, options, count=50):
        # update the count with 50 
        return super(FLSPImport, self).parse_preview(options, count)
    