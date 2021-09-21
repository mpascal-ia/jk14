# -*- coding: utf-8 -*-
from odoo import models, fields, api


class FollowupReportSearch(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    @api.multi
    def _asset_difference_search(self, account_type, operator, operand):
        if operator not in ('<', '=', '>', '>=', '<='):
            return []
        if type(operand) not in (float, int):
            return []
        sign = 1
        if account_type == 'payable':
            sign = -1
        res = self._cr.execute('''
               SELECT partner.id
               FROM res_partner partner
               LEFT JOIN account_move_line aml ON aml.partner_id = partner.id
               JOIN account_move move ON move.id = aml.move_id
               RIGHT JOIN account_account acc ON aml.account_id = acc.id
               WHERE acc.internal_type = %s
                 AND NOT acc.deprecated AND acc.company_id = %s
                 AND move.state = 'posted'
               GROUP BY partner.id
               HAVING %s * COALESCE(SUM(aml.amount_residual), 0) ''' + operator + ''' %s''',
                               (account_type, self.env.user.company_id.id, sign, operand))
        res = self._cr.fetchall()
        if not res:
            return [('id', '=', '0')]
        return [('id', 'in', [r[0] for r in res])]
