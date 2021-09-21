# -*- coding:utf-8 -*-
##############################################################################
#    Copyright (C) Ioppolo and Associates (I&A) 2018 (<http://ioppolo.com.au>).
##############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class AccountInvoice(models.Model):
    _inherit = 'account.invoice.line'
    _description = 'update the records'


    @api.model
    def create(self,vals):
        res = super(AccountInvoice,self).create(vals)
        for record in self:
            if record.invoice_id.x_studio_imported_invoice_1:
                if record.x_studio_analytic_tag_id:
                    tag_ids = record.x_studio_analytic_tag_id.split(',')
                    print("record.x_studio_analytic_tag_id",record.x_studio_analytic_tag_id)
                    print("record.x_studio_analytic_tag_id",type(record.x_studio_analytic_tag_id))
                    record.analytic_tag_ids = (6,0,[tag_ids])
                    record._onchange_invoice_line_ids()
        return res

