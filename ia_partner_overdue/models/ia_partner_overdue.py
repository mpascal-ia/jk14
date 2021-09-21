from odoo import models,fields,api
from datetime import datetime
from datetime import date, timedelta

class PartnerOverdue(models.Model):

    _inherit = 'res.partner'

    over_due_compute = fields.Float("Overdue Days",compute="_cal_field")
    over_due_compute1 = fields.Float("Overdue Days", related="over_due_compute",store=True)


    @api.onchange('over_due_compute')
    def _compute_fieldvalue(self):
        for each in self:
            each.over_due_compute1 = each.over_due_compute
            each.write({'over_due_compute1': each.over_due_compute})

    def _cal_field(self):
        for record in self:
            account = self.env["account.invoice"].search([('partner_id.name','=',record.name),
                                                          ('date_due','<',date.today()),
                                                          ('state','=','open')])

            count = 0
            lis=[]
            pro=[]
            for s in account:
                val = date.today().strftime('%Y-%m-%d')
                sal = datetime.strptime(val, '%Y-%m-%d')

                value = s.date_due.strftime('%Y-%m-%d')
                sal1 = datetime.strptime(value, '%Y-%m-%d')

                final = sal - sal1
                lis.append(final.days)

            lis.sort(key=int)
            if len(lis) != 0:
                a = lis[-1]
                record.over_due_compute1 = a
                record.over_due_compute = a
                record.update({'over_due_compute': a})
                record.update({'over_due_compute1': a})
                record.write({'over_due_compute1': record.over_due_compute})
                count = 1

            if (count == 0):
                record.write({'over_due_compute1': record.over_due_compute})
            # self.write({'over_due_compute1': self.over_due_compute})

