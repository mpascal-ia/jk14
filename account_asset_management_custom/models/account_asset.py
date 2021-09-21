# -*- coding: utf-8 -*-
# Copyright 2009-2018 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import calendar
from datetime import date
from dateutil.relativedelta import relativedelta

from odoo import api, models, fields, _
from odoo.exceptions import UserError

class AccountAsset(models.Model):
    _inherit = 'account.asset'

    method_progress_factor = fields.Float(
         string='Degressive Factor', readonly=True,
         states={'draft': [('readonly', False)]}, default=0.0, digits=(16, 4))

    def _compute_depreciation_table(self):
        table = []
        if self.method_time in ['year', 'number'] \
                and not self.method_number and not self.method_end:
            return table
        company = self.company_id
        asset_date_start = self.date_start
        fiscalyear_lock_date = (
            company.fiscalyear_lock_date or fields.Date.to_date('1901-01-01'))
        depreciation_start_date = self._get_depreciation_start_date(
            self._get_fy_info(asset_date_start)['record'])
        depreciation_stop_date = self._get_depreciation_stop_date(
            depreciation_start_date)
        fy_date_start = asset_date_start
        while fy_date_start <= depreciation_stop_date:
            fy_info = self._get_fy_info(fy_date_start)
            table.append({
                'fy': fy_info['record'],
                'date_start': fy_info['date_from'],
                'date_stop': fy_info['date_to'],
                'init': False, #fiscalyear_lock_date >= fy_info['date_from'],
            })
            fy_date_start = fy_info['date_to'] + relativedelta(days=1)
        # Step 1:
        # Calculate depreciation amount per fiscal year.
        # This is calculation is skipped for method_time != 'year'.
        line_dates = self._compute_line_dates(
            table, depreciation_start_date, depreciation_stop_date)
        table = self._compute_depreciation_amount_per_fiscal_year(
            table, line_dates, depreciation_start_date, depreciation_stop_date
        )
        # Step 2:
        # Spread depreciation amount per fiscal year
        # over the depreciation periods.
        self._compute_depreciation_table_lines(
            table, depreciation_start_date, depreciation_stop_date,
            line_dates)

        return table
    
    
    def _compute_depreciation_amount_per_fiscal_year(
            self, table, line_dates, depreciation_start_date,
            depreciation_stop_date):
        digits = self.env['decimal.precision'].precision_get('Account')
        fy_residual_amount = self.depreciation_base
        i_max = len(table) - 1
        asset_sign = self.depreciation_base >= 0 and 1 or -1
        day_amount = 0.0
        if self.days_calc:
            days = (depreciation_stop_date - depreciation_start_date).days + 1
            day_amount = self.depreciation_base / days

        for i, entry in enumerate(table):
            year_amount  = 0.0
            if self.method_time == 'year':
                year_amount = self._compute_year_amount(
                    fy_residual_amount, depreciation_start_date,
                    depreciation_stop_date, entry)
                if self.method_period == 'year':
                    period_amount = year_amount
                elif self.method_period == 'quarter':
                    period_amount = year_amount / 4
                elif self.method_period == 'month':
                    period_amount = year_amount / 12
                if i == i_max:
                    if self.method in ['linear-limit', 'degr-limit']:
                        fy_amount = fy_residual_amount - self.salvage_value
                    else:
                        fy_amount = fy_residual_amount
                else:
                    firstyear = i == 0 and True or False
                    fy_factor = self._get_fy_duration_factor(
                        entry, firstyear)
                    fy_amount = year_amount * fy_factor
                if asset_sign * (fy_amount - fy_residual_amount) > 0:
                    fy_amount = fy_residual_amount
                period_amount = round(period_amount, 8)
                fy_amount = round(fy_amount, 8)
            else:
                fy_amount = False
                if self.method_time == 'number':
                    number = self.method_number
                else:
                    number = len(line_dates)
                period_amount = round(self.depreciation_base / number, digits)
            entry.update({
                'period_amount': period_amount,
                'fy_amount': fy_amount,
                'day_amount': day_amount,
                'year_amount':year_amount,
            })
            if self.method_time == 'year':
                fy_residual_amount -= fy_amount
                if round(fy_residual_amount, digits) == 0:
                    break
        i_max = i
        table = table[:i_max + 1]
        return table

    def _get_first_period_amount(self, table, entry, depreciation_start_date,
                                 line_dates):
        """
        Return prorata amount for Time Method 'Year' in case of
        'Prorata Temporis'
        """
        amount = entry.get('period_amount')
        if self.prorata and self.method_time == 'year':
            dates = [x for x in line_dates if x <= entry['date_stop']]
            month = dates[0].month 
            first_date=dates[0] + relativedelta( days=1)
            days = (dates[len(dates) - 1] - first_date).days + 1

            full_periods = len(dates) -1
            amount = entry['fy_amount'] - amount * full_periods
            if entry['year_amount'] > 0.0:
                if self.method == 'linear' and self.date_start.day ==1:
                   amount = entry['year_amount']/12
                else:
                   amount = entry['fy_amount'] - (entry['year_amount']/365)*days
                
        return amount

    def _compute_depreciation_table_lines(self, table, depreciation_start_date,
                                          depreciation_stop_date, line_dates):

        digits = self.env['decimal.precision'].precision_get('Account')
        asset_sign = 1 if self.depreciation_base >= 0 else -1
        i_max = len(table) - 1
        remaining_value = self.depreciation_base
        depreciated_value = 0.0

        for i, entry in enumerate(table):

            lines = []
            fy_amount_check = 0.0
            fy_amount = entry['fy_amount']
            li_max = len(line_dates) - 1
            prev_date = max(entry['date_start'], depreciation_start_date)
            for li, line_date in enumerate(line_dates):
                line_days = (line_date - prev_date).days + 1
                if round(remaining_value, digits) == 0.0:
                    break

                if (line_date > min(entry['date_stop'],
                                    depreciation_stop_date) and not
                        (i == i_max and li == li_max)):
                    prev_date = line_date
                    break
                else:
                    prev_date = line_date + relativedelta(days=1)

                if self.method == 'degr-linear' \
                        and asset_sign * (fy_amount - fy_amount_check) < 0:
                    break

                if i == 0 and li == 0:
                    if entry.get('day_amount') > 0.0:
                        amount = line_days * entry.get('day_amount')
                    else:
                        amount = self._get_first_period_amount(
                            table, entry, depreciation_start_date, line_dates)
                        amount = round(amount, digits)
                else:
                    if entry.get('day_amount') > 0.0:
                        amount = line_days * entry.get('day_amount')
                    else:
                        amount = entry.get('period_amount')

                # last year, last entry
                # Handle rounding deviations.
                if i == i_max and li == li_max:
                    amount = remaining_value
                    remaining_value = 0.0
                else:
                    remaining_value -= amount
                fy_amount_check += amount
                if amount>0.61 and amount < 1.8:
                    i =1
                line = {
                    'date': line_date,
                    'days': line_days,
                    'amount': amount,
                    'depreciated_value': depreciated_value,
                    'remaining_value': remaining_value,
                }
                lines.append(line)
                depreciated_value += amount

            # Handle rounding and extended/shortened FY deviations.
            #
            # Remark:
            # In account_asset_management version < 8.0.2.8.0
            # the FY deviation for the first FY
            # was compensated in the first FY depreciation line.
            # The code has now been simplified with compensation
            # always in last FT depreciation line.
            if self.method_time == 'year' and not entry.get('day_amount'):
                if round(fy_amount_check - fy_amount, digits) != 0:
                    diff = fy_amount_check - fy_amount
                    amount = amount - diff
                    remaining_value += diff
                    # lines[-1].update({
                    #   # 'amount': amount,
                    #     'remaining_value': remaining_value,
                    # })
                    depreciated_value -= diff

            if not lines:
                table.pop(i)
            else:
                entry['lines'] = lines
            line_dates = line_dates[li:]

        for i, entry in enumerate(table):
            if not entry['fy_amount']:
                entry['fy_amount'] = sum(
                    [l['amount'] for l in entry['lines']])

    
    def _get_fy_duration(self, fy, option='days'):
        """Returns fiscal year duration.

        @param option:
        - days: duration in days
        - months: duration in months,
                    a started month is counted as a full month
        - years: duration in calendar years, considering also leap years
        """
        fy_date_start = fy.date_from
        fy_date_stop = fy.date_to
        days = (fy_date_stop - fy_date_start).days + 1
        months = (fy_date_stop.year - fy_date_start.year) * 12  \
            + (fy_date_stop.month - fy_date_start.month) + 1
        if option == 'days':
            return days
        elif option == 'months':
            return months
        elif option == 'years':
            year = fy_date_start.year
            # if year==2023:
            #     i =1
            cnt = fy_date_stop.year - fy_date_start.year + 1
            for i in range(cnt):
                cy_days = calendar.isleap(year) and 365  or 365
                if i == 0:  # first year
                    if fy_date_stop.year == year:
                        duration = (fy_date_stop - fy_date_start).days + 1
                    else:
                        duration = (
                            date(year, 12, 31) - fy_date_start).days + 1
                    factor = float(duration) / cy_days
                elif i == cnt - 1:  # last year
                    duration = (
                        fy_date_stop - date(year, 1, 1)).days + 1
                    if calendar.isleap(year) and fy_date_stop.month >2:
                        duration-=1                    
                    factor += float(duration) / cy_days
                else:
                    factor += 1.0
                year += 1
            return factor
    @api.multi
    def compute_depreciation_board(self):
        for asset in self:
            if asset.depreciation_line_ids.filtered(lambda r: r.move_check == True and r.remaining_value != 0.0):
               raise UserError(
                        _("Recompute is not allowed.Some depreciation lines are posted"))
        res = super(AccountAsset, self).compute_depreciation_board()
        return res

    @api.model
    def _xls_active_fields(self):
        """
        Update list in custom module to add/drop columns or change order
        """
        return [
            'account', 'name', 'code', 'date_start','date_remove',
            'depreciation_base', 'salvage_value','value_depreciated',
            'fy_start_value', 'fy_depr', 'fy_end_value',
            'fy_end_depr',
            'method','method_progress_factor', 'method_number', 'prorata'
        ]

    
    @api.model
    def _xls_asset_template(self):
        """
        Template updates

        """
        return {}

    
    @api.model
    def _xls_active_template(self):
        """
        Template updates

        """
        return {}

    