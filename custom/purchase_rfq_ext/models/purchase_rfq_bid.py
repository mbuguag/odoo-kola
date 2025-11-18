from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PurchaseRfqBid(models.Model):
    _name = 'purchase.rfq.bid'
    _description = 'Supplier Bid for RFQ'
    _order = 'create_date desc'

    name = fields.Char(string='Bid Reference', copy=False, readonly=True)
    rfq_id = fields.Many2one('purchase.order', string='RFQ', required=True, ondelete='cascade')
    vendor_id = fields.Many2one('res.partner', string='Vendor', required=True, domain=[('supplier_rank', '>', 0)])
    price = fields.Float(string='Bid Price')
    currency_id = fields.Many2one('res.currency', string='Currency', related='rfq_id.currency_id', store=True)
    notes = fields.Text('Notes')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('rejected', 'Rejected'),
        ('accepted', 'Accepted'),
    ], default='draft', string='Status')
    product_lines = fields.One2many('purchase.rfq.bid.line', 'bid_id', string='Bid Lines')
    user_id = fields.Many2one('res.users', string='Submitted By', default=lambda self: self.env.user)

    @api.model_create_multi
    def create(self, vals_list):
        # Correct way to handle sequence in create method
        for vals in vals_list:
            if not vals.get('name'):
                vals['name'] = self.env['ir.sequence'].next_by_code('purchase.rfq.bid') or '/'
        return super().create(vals_list)

    @api.constrains('vendor_id', 'rfq_id')
    def _check_vendor_unique(self):
        for rec in self:
            existing = self.search([
                ('rfq_id', '=', rec.rfq_id.id),
                ('vendor_id', '=', rec.vendor_id.id),
                ('id', '!=', rec.id)
            ])
            if existing:
                raise ValidationError('This vendor already submitted a bid for this RFQ.')

    def action_submit(self):
        for rec in self:
            rec.state = 'submitted'
            rec.rfq_id.message_post(body=f"Bid {rec.name} submitted by {rec.vendor_id.name}")

    def action_accept(self):
        for rec in self:
            rec.state = 'accepted'
            # Reject other bids
            other_bids = self.search([
                ('rfq_id', '=', rec.rfq_id.id),
                ('id', '!=', rec.id),
                ('state', '!=', 'rejected')
            ])
            other_bids.write({'state': 'rejected'})
            # Create purchase order
            new_po = rec.rfq_id.action_select_bid_and_create_po(rec.id)
            if new_po:
                rec.message_post(body=f"Bid accepted and Purchase Order {new_po.name} created.")