# purchase_order_ext.py
from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    # Add date_sent field to match what the inherited view expects
    date_sent = fields.Datetime(
        string='Date Sent',
        copy=False,
        help='Date when the RFQ/PO was sent to the vendor'
    )

    vendor_ids = fields.Many2many(
        comodel_name='res.partner',
        relation='purchase_order_vendor_rel',
        column1='order_id',
        column2='partner_id',
        string='Assigned Vendors',
        domain=[('supplier_rank', '>', 0)]
    )

    vendor_line_ids = fields.One2many(
        comodel_name='rfq.vendor.line',
        inverse_name='order_id',
        string='RFQ Vendors'
    )

    rfq_bid_count = fields.Integer(
        string='Bids Count',
        compute='_compute_rfq_bid_count'
    )

    rfq_bid_ids = fields.One2many(
        comodel_name='purchase.rfq.bid',
        inverse_name='rfq_id',
        string='Supplier Bids'
    )

    @api.depends('rfq_bid_ids')
    def _compute_rfq_bid_count(self):
        for rec in self:
            rec.rfq_bid_count = len(rec.rfq_bid_ids or [])

    def action_view_rfq_bids(self):
        self.ensure_one()
        action = self.env.ref('purchase_rfq_ext.action_purchase_rfq_bid_tree').read()[0]
        action['domain'] = [('rfq_id', '=', self.id)]
        return action

    def action_select_bid_and_create_po(self, bid_id):
        bid = self.env['purchase.rfq.bid'].browse(bid_id)
        if not bid.exists():
            return False
        bid.state = 'accepted'
        po_vals = {
            'partner_id': bid.vendor_id.id,
            'origin': self.name or self.origin or False,
            'currency_id': self.currency_id.id,
            'order_line': [],
        }
        line_vals = []
        for bline in bid.product_lines:
            line_vals.append((0, 0, {
                'product_id': bline.product_id.id,
                'name': bline.product_id.display_name or bline.product_id.name,
                'product_qty': bline.product_qty,
                'product_uom': bline.product_uom.id,
                'price_unit': bline.price_unit,
            }))
        po_vals['order_line'] = line_vals
        new_po = self.env['purchase.order'].create(po_vals)
        return new_po