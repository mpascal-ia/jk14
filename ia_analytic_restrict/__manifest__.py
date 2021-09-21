# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name' : ' Restrict Analytic creation',
    'version' : '1.0',
    'summary': 'Restrict Analytic creation only to the Configuration page',
    'description': """
Remove the ability to create analytic accounts and tags from all records except the configuration screen.
    """,
    'category': 'Accounting',
    'sequence': 20,
    'website' : 'https://ioppolo.com.au',
    'depends' : ['account','analytic'],
    'demo' : [],
    'data' : [
        'views/analytic_restrict.xml',
    ],
    'test' : [],
    'auto_install': False,
    'installable': True,
}
