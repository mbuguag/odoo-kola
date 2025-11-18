from odoo import models, fields, api


class PurchaseRfqBidLine(models.Model):
    _name = 'purchase.rfq.bid.line'
    _description = 'RFQ Bid Line Items'

    bid_id = fields.Many2one('purchase.rfq.bid', string='Bid Reference', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    product_qty = fields.Float(string='Quantity', required=True, default=1.0)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure', required=True)
    price_unit = fields.Float(string='Unit Price', required=True, default=0.0)
    price_subtotal = fields.Monetary(string='Subtotal', compute='_compute_subtotal', store=True, currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency', related='bid_id.currency_id', store=True)
    notes = fields.Text('Notes')

    @api.depends('product_qty', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.price_subtotal = line.product_qty * line.price_unit

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.product_uom = self.product_id.uom_po_id
            self.price_unit = self.product_id.standard_price or 0.0
