# -*- coding: utf-8 -*-
import base64
import requests
import json
# import unirest # odoo11 commented due to it is missing in python3 

import time
from datetime import datetime, timedelta
from dateutil import relativedelta

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, Warning, UserError

from odoo import tools

import logging
_logger = logging.getLogger(__name__)


class WizAccountAssetReport(models.TransientModel):
    _name = 'wiz.account.asset.report'
    _description = 'Results from the synchronize timesheet'

    @api.multi
    def _get_default_fiscal_year_id(self):
        return self.env['account.fiscal.year'].search([('company_id', '=', self.env.user.company_id.id)], order="id desc", limit=1).id

    # TODO: add support for all date range types
    date_start = fields.Date(string='Start Date',required=True)
    date_end = fields.Date(string='End Date',required=True)
    fiscal_year_id = fields.Many2one('account.fiscal.year',string='Fiscal Year', default =_get_default_fiscal_year_id)

    @api.onchange('fiscal_year_id')
    def _onchange_fiscal_year_id(self):
        if self.fiscal_year_id:
            self.date_start = self.fiscal_year_id.date_from
            self.date_end = self.fiscal_year_id.date_to

    # @api.multi
    def xls_export(self):
        self.ensure_one()
        asset_obj = self.env['account.asset']       
        domain = [('date_start', '<=', self.date_end),('state','!=','draft'),'|',
             ('date_remove', '=', False),
             ('date_remove', '>=', self.date_start)]
        assets = asset_obj.search(domain)
        if not assets:
            raise UserError(
                _('No records found for your selection!'))
        
        datas = {'ids': [self.id],'date_start':self.date_start,'date_end':self.date_end,'dynamic_report': True}
        return self.env.ref('account_asset_management_custom.action_asset_report_excel').report_action(self, data= datas, config=False)
