from odoo import models, fields


class PurchaseRequest(models.Model):
    _name = 'purchase.request'
    _description = 'Purchase Request from Employee'

    name = fields.Char('Request Reference', required=True, copy=False,
                       default=lambda self: self.env['ir.sequence'].next_by_code('purchase.request'))
    requested_by = fields.Many2one('res.users', string='Requested By', default=lambda self: self.env.uid, readonly=True)
    department = fields.Many2one('hr.department', string='Department')
    date_request = fields.Datetime('Request Date', default=fields.Datetime.now)
    state = fields.Selection([('draft','Draft'),('to_procure','To Procure'),('cancel','Cancelled'),('done','Done')], default='draft')
    line_ids = fields.One2many('purchase.request.line','request_id',string='Request Lines')
    note = fields.Text('Notes')

    def action_send_to_procurement(self):
        for req in self:
            rfq_values = {'origin': req.name, 'state': 'draft', 'order_line': []}
            line_vals = []
            for line in req.line_ids:
                line_vals.append((0,0,{
                    'product_id': line.product_id.id if line.product_id else False,
                    'name': line.description or (line.product_id and line.product_id.display_name) or 'Product',
                    'product_qty': line.product_qty,
                    'product_uom': line.product_uom.id if line.product_uom else False,
                    'price_unit': 0.0,
                }))
            rfq_values['order_line'] = line_vals
            self.env['purchase.order'].create(rfq_values)
            req.state = 'to_procure'
        return True
