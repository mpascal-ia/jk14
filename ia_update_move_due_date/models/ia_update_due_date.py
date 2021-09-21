# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError

class ProjectName(models.Model):
    _inherit = 'account.move'


    @api.multi
    def update_due_date(self):
        for record in self:
            if record.date:
                for line in record.line_ids:
                    line.date_maturity = record.date
            else:
                raise ValidationError(
                    _('Please Update the  Date field...'))