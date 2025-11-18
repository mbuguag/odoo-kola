from odoo import models, fields


class PurchaseRequestLine(models.Model):
    _name = 'purchase.request.line'
    _description = 'Lines for Purchase Request'

    request_id = fields.Many2one('purchase.request', string='Request', ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product')
    description = fields.Text(string='Description')
    product_qty = fields.Float(string='Quantity', default=1.0)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure')
