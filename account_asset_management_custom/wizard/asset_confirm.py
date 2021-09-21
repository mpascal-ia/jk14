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




class AssetConfirmResults(models.TransientModel):
    _name = 'asset.confirm.results' 
    _description = 'Asset Confirm Results'
    @api.multi
    def action_confirm_asset(self):

        context = self.env.context
        active_ids = context.get('active_ids', [])
        active_model = context.get('active_model', '')
        asset_ids = self.env[active_model].browse(active_ids)
        a_ids = []
        for asset in asset_ids:
            a_ids.append(asset.id)
            asset.validate()
        context = self.env.context.copy()
        resource_id = self.env.ref("account_asset_management.account_asset_view_tree").id
        return {
            'name': _('Timesheet Synchronization: Actions Summary'),
            'view_type': 'form',
            'res_id': a_ids,
            'context': context,
            'view_mode': 'form',
            'views': [(resource_id, 'tree')],
            'res_model': 'account.asset',
            'type': 'ir.actions.act_window',
            'target': 'current',
        }
