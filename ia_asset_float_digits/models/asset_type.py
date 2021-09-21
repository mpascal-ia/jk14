from odoo import models,fields
from odoo.addons import decimal_precision as dp

class AssetType(models.Model):
    _inherit = 'account.asset.category'

    method_progress_factor = fields.Float('Degressive Factor',digits=dp.get_precision('asset_decimal'))



class AssetAsset(models.Model):
    _inherit = 'account.asset.asset'

    method_progress_factor = fields.Float(string='Degressive Factor', readonly=True, default=0.3,
                                          states={'draft': [('readonly', False)]},digits=dp.get_precision('asset_decimal'))

