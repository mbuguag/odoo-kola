from odoo import models, fields, api


class RfqVendorLine(models.Model):
    _name = 'rfq.vendor.line'
    _description = 'RFQ Vendor Line'

    order_id = fields.Many2one('purchase.order', string='RFQ', required=True, ondelete='cascade')
    partner_id = fields.Many2one('res.partner', string='Vendor', domain=[('supplier_rank','>',0)], required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    state = fields.Selection([('draft','Draft'),('sent','Sent'),('responded','Responded')], default='draft')
    date_sent = fields.Datetime('Date Sent')
    date_responded = fields.Datetime('Date Responded')
    note = fields.Text('Note')

    @api.model
    def create(self, vals):
        rec = super().create(vals)
        if rec.state == 'sent' and not rec.date_sent:
            rec.date_sent = fields.Datetime.now()
        return rec
