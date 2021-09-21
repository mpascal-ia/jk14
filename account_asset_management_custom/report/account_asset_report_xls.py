# Copyright 2009-2018 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from odoo import models, _
from odoo.exceptions import UserError
from odoo.tools.translate import translate
from datetime import datetime
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)
IR_TRANSLATION_NAME = 'account.asset.report'
import xlwt
class AssetReportCustom(models.AbstractModel):
    _name = 'report.account_asset_management_custom.asset_report_xls'
    _inherit = 'report.report_xlsx.abstract'

    def _(self, src):
        lang = self.env.context.get('lang', 'en_US')
        val = translate(
            self.env.cr, IR_TRANSLATION_NAME, 'report', lang, src) or src
        return val

    def _get_ws_params(self, wb, data, wiz):
        self.assets = self.env['account.asset'].search([])
       # s1 = self._get_acquisition_ws_params(wb, data, wiz)
        s2 = self._get_active_ws_params(wb, data, wiz)
        #s3 = self._get_removal_ws_params(wb, data, wiz)
        return [s2]
    def fy_end_value(self, data, asset):
            if datetime.strptime(data['date_end'],"%Y-%m-%d").date()==asset.date_start:
                line = self.env['account.asset.line'].search([('line_date','=',data['date_end']),('asset_id','=',asset['id'])], order='id DESC', limit = 1)
            else:
                line = self.env['account.asset.line'].search([('line_date','<=',data['date_end']),('asset_id','=',asset['id'])], order='id DESC', limit = 1)
            if line:
                return line.remaining_value
            else:
                return 0.0
    def fy_start_value(self, data, asset):
            date_start = data['date_start']
            date_end = data['date_end']

            if datetime.strptime(date_start,"%Y-%m-%d").date()< asset.date_start:
                date_start = asset.date_start
                if datetime.strptime(data['date_end'],"%Y-%m-%d").date()==asset.date_start:
                    line = self.env['account.asset.line'].search([('line_date','=',date_start),('asset_id','=',asset['id'])], order='id ASC', limit = 1)
                    
                elif datetime.strptime(data['date_start'],"%Y-%m-%d").date()<= asset.date_start and datetime.strptime(data['date_end'],"%Y-%m-%d").date()>=asset.date_start:
                    line = self.env['account.asset.line'].search([('line_date','=',date_start),('asset_id','=',asset['id'])], order='id ASC', limit = 1)
                else:
                    line = self.env['account.asset.line'].search([('line_date','<=',date_start),('asset_id','=',asset['id'])], order='id DESC', limit = 1)


            else:
                line = self.env['account.asset.line'].search([('line_date','<=',date_start),('asset_id','=',asset['id'])], order='id DESC', limit = 1)

            
            if line:
                if line.type == 'create':
                    return line.amount
                else:
                    return line.remaining_value
            else:
                return 0.0
    def fy_depreciated_value(self, data, asset):
            line = self.env['account.asset.line'].search([('line_date','<=',data['date_end']),('asset_id','=',asset['id'])], order='id DESC', limit = 1)
            if line:
                return line.depreciated_value
            else:
                return 0.0
    def _get_asset_template(self):

        asset_template = {
            'account': {
                        'header': {
                            'type': 'string',
                            'value': self._('Account'),
                        },
                        'asset': {
                            'type': 'string',
                            'value': self._render(
                                "asset.profile_id.account_asset_id.code"),
                        },
                        'totals': {
                            'type': 'string',
                            'value': self._('Totals'),
                        },
                        'width': 20,
                    },
            'name': {
                        'header': {
                            'type': 'string',
                            'value': self._('Name'),
                        },
                        # 'asset_view': {
                        #     'type': 'string',
                        #     'value': self._render("asset.name"),
                        # },
                        'asset': {
                            'type': 'string',
                            'value': self._render("asset.name"),
                        },
                        'width': 40,
                    },
            'code': {
                        'header': {
                            'type': 'string',
                            'value': self._('Reference'),
                        },
                        # 'asset_view': {
                        #     'type': 'string',
                        #     'value': self._render("asset.code or ''"),
                        # },
                        'asset': {
                            'type': 'string',
                            'value': self._render("asset.code or ''"),
                        },
                        'width': 20,
                        },
            'date_start': {
                            'header': {
                                'type': 'string',
                                'value': self._('Asset Start Date'),
                            },
                            'asset_view': {},
                            'asset': {
                                'value': self._render(
                                    "asset.date_start and "
                                    "datetime.strptime(str(asset.date_start),'%Y-%m-%d').strftime('%d/%m/%Y') "
                                    "or None"),
                                'format': self.format_tcell_date_left,
                            },
                            'width': 20,
                            },
            'date_remove': {
                                'header': {
                                    'type': 'string',
                                    'value': self._('Asset Removal Date'),
                                },
                                'asset': {
                                    'value': self._render(
                                        "asset.date_remove and "
                                        "datetime.strptime(str(asset.date_remove),'%Y-%m-%d').strftime('%d/%m/%Y') "
                                        "or None"),
                                    'format': self.format_tcell_date_left,
                                },
                                'width': 20,
                            },
            'depreciation_base': {
                                'header': {
                                    'type': 'string',
                                    'value': self._('Depreciation Base'),
                                    'format': self.format_theader_yellow_right,
                                },
                                'asset_view': {
                                    'type': 'formula',
                                    'value': self._render("asset_formula"),
                                    'format': self.format_theader_blue_amount_right,
                                },
                                'asset': {
                                    'type': 'number',
                                    'value': self._render("asset.depreciation_base"),
                                    'format': self.format_tcell_amount_right,
                                },
                                'totals': {
                                    'type': 'number',
                                    'value': self._render('asset_total_formula'),
                                    'format': self.format_theader_yellow_amount_right,
                                },
                                'width': 18,
                            },
            'salvage_value': {
                                'header': {
                                    'type': 'string',
                                    'value': self._('Salvage Value'),
                                    'format': self.format_theader_yellow_right,
                                },
                                'asset_view': {
                                    'type': 'formula',
                                    'value': self._render("salvage_formula"),
                                    'format': self.format_theader_blue_amount_right,
                                },
                                'asset': {
                                    'type': 'number',
                                    'value': self._render("asset.salvage_value"),
                                    'format': self.format_tcell_amount_right,
                                },
                                'totals': {
                                    'type': 'number',
                                    'value': self._render('salvage_total_formula'),
                                    'format': self.format_theader_yellow_amount_right,
                                },
                                'width': 18,
                 },
            #   'value_residual': {
            #                         'header': {
            #                             'type': 'string',
            #                             'value': self._('Residual Value'),
            #                             'format': self.format_theader_yellow_right,
            #                         },
            #                         'asset_view': {
            #                             'type': 'formula',
            #                             'value': self._render("value_residual_formula"),
            #                             'format': self.format_theader_blue_amount_right,
            #                         },
            #                         'asset': {
            #                             'type': 'number',
            #                             'value': self._render("asset.value_residual"),
            #                             'format': self.format_tcell_amount_right,
            #                         },
            #                         'totals': {
            #                             'type': 'number',
            #                             'value': self._render('value_residual_total_formula'),
            #                             'format': self.format_theader_yellow_amount_right,
            #                         },
            #                         'width': 18,
            #                     },
             'value_depreciated': {
                                    'header': {
                                        'type': 'string',
                                        'value': self._('Total Depreciated Value'),
                                        'format': self.format_theader_yellow_right,
                                    },
                                    'asset_view': {
                                        'type': 'formula',
                                        'value': self._render("value_depreciated_formula"),
                                        'format': self.format_theader_blue_amount_right,
                                    },
                                    'asset': {
                                        'type': 'number',
                                        'value': self._render("value_depreciated"),
                                        'format': self.format_tcell_amount_right,
                                    },
                                    'totals': {
                                        'type': 'number',
                                        'value': self._render('value_depreciated_total_formula'),
                                        'format': self.format_theader_yellow_amount_right,
                                    },
                                    'width': 18,
                                },
            'fy_start_value': {
                            'header': {
                                'type': 'string',
                                'value': self._('FY Start Value'),
                                'format': self.format_theader_yellow_right,
                            },
                            'asset_view': {
                                'type': 'formula',
                                'value': self._render("fy_start_formula"),
                                'format': self.format_theader_blue_amount_right,
                            },
                            'asset': {
                                'type': 'number',
                                'value': self._render("fy_start_value"),
                                'format': self.format_tcell_amount_right,
                            },
                            'totals': {
                                'type': 'number',
                                'value': self._render('fy_start_total_formula'),
                                'format': self.format_theader_yellow_amount_right,
                            },
                            'width': 18,
                        },
            'fy_depr': {
                                    'header': {
                                        'type': 'string',
                                        'value': self._('FY Depreciation'),
                                        'format': self.format_theader_yellow_right,
                                    },
                                    'asset_view': {
                                        'type': 'formula',
                                        'value': self._render("fy_diff_formula"),
                                        'format': self.format_theader_blue_amount_right,
                                    },
                                    'asset': {
                                        'type': 'number',
                                        'value': self._render("fy_depr"),
                                        'format': self.format_tcell_amount_right,
                                    },
                                    'totals': {
                                        'type': 'number',
                                        'value': self._render('fy_diff_formula'),
                                        'format': self.format_theader_yellow_amount_right,
                                    },
                                    'width': 18,
                                },
            'fy_end_value': {
                                'header': {
                                    'type': 'string',
                                    'value': self._('FY End Value'),
                                    'format': self.format_theader_yellow_right,
                                },
                                'asset_view': {
                                    'type': 'formula',
                                    'value': self._render("fy_end_formula"),
                                    'format': self.format_theader_blue_amount_right,
                                },
                                'asset': {
                                    'type': 'number',
                                    'value': self._render("fy_end_value"),
                                    'format': self.format_tcell_amount_right,
                                },
                                'totals': {
                                    'type': 'number',
                                    'value': self._render('fy_end_total_formula'),
                                    'format': self.format_theader_yellow_amount_right,
                                },
                                'width': 18,
                            },
            'fy_end_depr': {
                'header': {
                    'type': 'string',
                    'value': self._('Tot. Depreciation'),
                    'format': self.format_theader_yellow_right,
                },
                'asset_view': {
                    'type': 'formula',
                    'value': self._render("total_depr_formula"),
                    'format': self.format_theader_blue_amount_right,
                },
                'asset': {
                    'type': 'number',
                    'value': self._render("total_depr_formula"),
                    'format': self.format_tcell_amount_right,
                },
                'totals': {
                    'type': 'number',
                    'value': self._render('total_depr_formula_1'),
                    'format': self.format_theader_yellow_amount_right,
                },
                'width': 18,
            },
            'method': {
                'header': {
                    'type': 'string',
                    'value': self._('Comput. Method'),
                    'format': self.format_theader_yellow_center,
                },
                'asset': {
                    'type': 'string',
                    'value': self._render("asset.method or ''"),
                    'format': self.format_tcell_center,
                },
                'width': 20,
            },
            'method_progress_factor': {
                'header': {
                    'type': 'string',
                    'value': self._('Degressive Factor'),
                    'format': self.format_theader_yellow_center,
                },
                'asset': {
                    'type': 'string',
                    'value': self._render("method_progress_factor"),
                    'format': self.format_tcell_center,
                },
                'width': 20,
            },
            'method_number': {
                'header': {
                    'type': 'string',
                    'value': self._('Number of Years'),
                    'format': self.format_theader_yellow_center,
                },
                'asset': {
                    'type': 'number',
                    'value': self._render("asset.method_number"),
                    'format': self.format_tcell_integer_center,
                },
                'width': 20,
            },
            'prorata': {
                'header': {
                    'type': 'string',
                    'value': self._('Prorata Temporis'),
                    'format': self.format_theader_yellow_center,
                },
                'asset': {
                    'type': 'boolean',
                    'value': self._render("asset.prorata"),
                    'format': self.format_tcell_center,
                },
                'width': 20,
            },
           
        }
        asset_template.update(
            self.env['account.asset']._xls_asset_template())

        return asset_template

   

    def _get_active_ws_params(self, wb, data, wiz):

        active_template = self._get_asset_template()
        active_template.update(
            self.env['account.asset']._xls_active_template())
        wl_act = self.env['account.asset']._xls_active_fields()
        title = self._get_title(wiz, 'active', data)
        title_short = self._get_title(wiz, 'active', data)
        sheet_name = title_short[:31].replace('/', '-')

        return {
            'ws_name': 'Asset Report',
            'generate_ws_method': '_active_report',
            'title': title,
            'wanted_list': wl_act,
            'col_specs': active_template,
        }

    
    def _get_title(self, wiz, report, data):      
        return 'Asset Reports From '+str(datetime.strptime(str(data.get('date_start',False)),'%Y-%m-%d').strftime('%d/%m/%Y')) + " To "+str(datetime.strptime(str(data.get('date_end',False)),'%Y-%m-%d').strftime('%d/%m/%Y'))

    def _report_title(self, ws, row_pos, ws_params, data, wiz):
        return self._write_ws_title(ws, row_pos, ws_params)

    def _view_add(self, acq, assets):
        # parent = self.assets.filtered(lambda r: acq.parent_id == r)
        # if parent and parent not in assets:
        #     self._view_add(parent, assets)
        assets.append(acq)

   
    
    def _active_report(self, workbook, ws, ws_params, data, wiz):

        ws.set_portrait()
        ws.fit_to_pages(1, 0)
        ws.set_header(self.xls_headers['standard'])
        ws.set_footer(self.xls_footers['standard'])
        wl_act = ws_params['wanted_list']
        if 'account' not in wl_act:
            raise UserError(_(
                "The 'account' field is a mandatory entry of the "
                "'_xls_active_fields' list !"))
        self._set_column_width(ws, ws_params)

        row_pos = 0
        row_pos = self._report_title(ws, row_pos, ws_params, data, wiz)

        # if not wiz.date_range_id.type_id.fiscal_year:
        #     raise UserError(_(
        #         "The current version of the asset mangement reporting "
        #         "module supports only fiscal year based reports."
        #     ))
        #fy = wiz.date_range_id
        
        actives = self.env['account.asset'].search([('date_start', '<=', data.get('date_end', False)),('state','!=','draft'),'|',
             ('date_remove', '=', False),
             ('date_remove', '>=', data.get('date_start', False))], order='date_start ASC')

        

        row_pos = self._write_line(
            ws, row_pos, ws_params, col_specs_section='header',
            default_format=self.format_theader_yellow_left)

        ws.freeze_panes(row_pos, 0)

        row_pos_start = row_pos
        depreciation_base_pos = 'depreciation_base' in wl_act and \
            wl_act.index('depreciation_base')
        salvage_value_pos = 'salvage_value' in wl_act and \
            wl_act.index('salvage_value')
        fy_start_value_pos = 'fy_start_value' in wl_act and \
           wl_act.index('fy_start_value')
        fy_end_value_pos = 'fy_end_value' in wl_act and \
            wl_act.index('fy_end_value')
        value_residual_pos = 'value_residual'  in wl_act and \
            wl_act.index('value_residual')
        value_depreciated_pos = 'value_depreciated'  in wl_act and \
            wl_act.index('value_depreciated')
        fy_depr_pos = 'fy_depr'  in wl_act and \
            wl_act.index('fy_depr')
        acts = self.assets.filtered(lambda r: r in actives)
        acts_and_parents = []
        for act in acts:
            self._view_add(act, acts_and_parents)

        entries = []
        for asset_i, asset in enumerate(acts_and_parents):
            entry = {}
            entry['asset'] = asset
            entries.append(entry)
        fy_start_total_formula_1 =0.0
        fy_end_total_formula_1 = 0.0
        asset_total_formula_1 = 0.0
        salvage_total_formula_1 = 0.0
        total_depr_formula_1 =0.0
        value_residual_total_formula_1=0.0
        value_depreciated_total_formula_1=0.0
        fy_diff_formula_1 = 0.0
        for entry in entries:
            asset = entry['asset']
            asset_total_formula_1+=asset.depreciation_base
            salvage_total_formula_1+=asset.salvage_value
            value_depreciated =asset.depreciation_base
            asset['date_start'] = str(asset['date_start'])
            fy_start_value_cell = self._rowcol_to_cell(
                row_pos, fy_start_value_pos)
            fy_end_value_cell = self._rowcol_to_cell(
                row_pos, fy_end_value_pos)
            fy_depr_cell = self._rowcol_to_cell(
                row_pos, fy_depr_pos)
            value_depreciated_cell  = self._rowcol_to_cell(
                row_pos, value_depreciated_pos)
            fy_diff_formula = fy_start_value_cell + '-' + fy_end_value_cell
            total_depr_formula = fy_depr_cell + '+' + value_depreciated_cell

           
            fy_start_value = self.fy_start_value( data, asset)
            value_depreciated = value_depreciated - fy_start_value
            fy_end_value = self.fy_end_value( data, asset)
            asset_total_formula_1
            fy_start_total_formula_1+=fy_start_value
            fy_end_total_formula_1+=fy_end_value
            fy_diff_formula_1 +=(fy_start_value - fy_end_value)         
            value_residual_total_formula_1+=asset.value_residual
          #  total_depr_formula = (fy_start_value - fy_end_value) + value_depreciated #L self.fy_depreciated_value(data, asset)
            value_depreciated_total_formula_1+=value_depreciated
            total_depr_formula_1 =total_depr_formula 
            row_pos = self._write_line(
                ws, row_pos, ws_params, col_specs_section='asset',
                render_space={
                    'asset': asset,
                    'value_depreciated':value_depreciated,                 
                    'fy_start_value':fy_start_value,
                    'fy_end_value':fy_end_value,
                    'fy_depr': fy_start_value - fy_end_value,
                    'fy_diff_formula': fy_diff_formula,
                    'total_depr_formula': value_depreciated +(fy_start_value - fy_end_value),
                    'method_progress_factor': asset.method !='linear' and  str(asset.method_progress_factor *100)+'%' or '',
                    },
                default_format=self.format_tcell_left)

        # asset_total_formula = self._rowcol_to_cell(row_pos_start,
        #                                            depreciation_base_pos)
        # salvage_total_formula = self._rowcol_to_cell(row_pos_start,
        #                                              salvage_value_pos)
        # fy_start_total_formula = self._rowcol_to_cell(row_pos_start,
        #                                               fy_start_value_pos)
        # fy_end_total_formula = self._rowcol_to_cell(row_pos_start,
        #                                             fy_end_value_pos)
        fy_start_value_cell = self._rowcol_to_cell(row_pos, fy_start_value_pos)
        fy_end_value_cell = self._rowcol_to_cell(row_pos, fy_end_value_pos)
        depreciation_base_cell = self._rowcol_to_cell(row_pos,
                                                      depreciation_base_pos)
        fy_diff_formula = fy_start_value_cell + '-' + fy_end_value_cell
        total_depr_formula = depreciation_base_cell + '-' + fy_end_value_cell
        fy_depr_cell = self._rowcol_to_cell(
                row_pos, fy_depr_pos)
        value_depreciated_cell  = self._rowcol_to_cell(
            row_pos, value_depreciated_pos)
        total_depr_formula = fy_depr_cell + '+' + value_depreciated_cell
        row_pos = self._write_line(
            ws, row_pos, ws_params, col_specs_section='totals',
            render_space={
                'asset_total_formula': asset_total_formula_1,
                'salvage_total_formula': salvage_total_formula_1,
                'fy_start_total_formula': fy_start_total_formula_1,
                'fy_end_total_formula': fy_end_total_formula_1,
                'fy_diff_formula': fy_diff_formula_1,               
                'value_residual_total_formula': value_residual_total_formula_1,
                'value_depreciated_total_formula':value_depreciated_total_formula_1,
                'total_depr_formula_1' :value_depreciated_total_formula_1+fy_diff_formula_1
            },
            default_format=self.format_theader_yellow_left)

    