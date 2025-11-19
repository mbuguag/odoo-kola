# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

try:
    from odoo.addons.portal.controllers.portal import CustomerPortal
except ImportError:
    CustomerPortal = object


class VendorRfqPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'vendor_rfq_count' in counters:
            partner = request.env.user.partner_id
            values['vendor_rfq_count'] = request.env['purchase.order'].sudo().search_count([
                ('vendor_ids', 'in', partner.id)
            ])
        return values

    @http.route(['/my/rfqs'], type='http', auth='user', website=True)
    def portal_my_rfqs(self, **kwargs):
        partner = request.env.user.partner_id
        rfqs = request.env['purchase.order'].sudo().search([
            ('vendor_ids', 'in', partner.id)
        ])

        return request.render('purchase_rfq_ext.portal_my_rfqs', {
            'rfqs': rfqs,
            'page_name': 'purchase_rfq',
        })

    @http.route(['/my/rfqs/<int:rfq_id>/submit-bid'], type='http', auth='user', website=True, methods=['GET', 'POST'])
    def portal_submit_rfq_bid(self, rfq_id, **post):
        partner = request.env.user.partner_id
        rfq = request.env['purchase.order'].sudo().browse(rfq_id)

        # Security: vendor must be assigned to RFQ
        if partner not in rfq.vendor_ids:
            return request.render('website.404')

        if request.httprequest.method == 'POST':
            bid_vals = {
                'rfq_id': rfq.id,
                'vendor_id': partner.id,
                'product_lines': [],
            }

            # Create lines from POST
            product_ids = post.getlist('product_id')
            qtys = post.getlist('qty')
            prices = post.getlist('price')

            lines = []
            for pid, qty, price in zip(product_ids, qtys, prices):
                lines.append((0, 0, {
                    'product_id': int(pid),
                    'product_qty': float(qty),
                    'product_uom': request.env['product.product'].sudo().browse(int(pid)).uom_id.id,
                    'price_unit': float(price),
                }))
            bid_vals['product_lines'] = lines

            request.env['purchase.rfq.bid'].sudo().create(bid_vals)

            return request.redirect('/my/rfqs')

        return request.render('purchase_rfq_ext.portal_submit_rfq_bid', {
            'rfq': rfq,
            'partner': partner,
        })