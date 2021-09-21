# -*- coding: utf-8 -*-
# Copyright 2009-2018 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'I&A Assets Management Customization',
    "version": "1.0",
    'license': 'AGPL-3',
    "category": "Ioppolo & Associates",
    "author": "Ioppolo & Associates",
    "website": "http://www.ioppolo.com.au/",
    'depends': ['account_accountant','account_asset_management', 'report_xlsx_helper'],
    'data': [
        'wizard/wiz_account_asset_report.xml',
        'report/report_asset.xml',
        'wizard/asset_confirm_view.xml',
        'views/account_asset_view.xml',
    ],
    'installable': True,
}
