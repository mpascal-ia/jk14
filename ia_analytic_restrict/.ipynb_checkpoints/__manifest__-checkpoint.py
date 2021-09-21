# -*- coding: utf-8 -*-
# Copyright 2009-2018 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name' : ' Restrict Analytic Tag creation',
    'version' : '1.0',
    'summary': 'Restrict Analytic Tag creation only to the Configuration page',
    'description': """
Remove the ability to create analytic tags from all records except the configuration screen.
    """,
    'category': 'Accounting',
    'website' : 'https://ioppolo.com.au',
    'depends' : ['account'],
    'data': [
        'views/analytic_restict.xml',
    ],
    'installable': True,
}