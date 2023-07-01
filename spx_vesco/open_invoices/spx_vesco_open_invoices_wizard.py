# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
     

import logging
_logger = logging.getLogger(__name__)

class Vesco_Invoice_Line(models.Model):
    _inherit = 'account.invoice'
    
    paid_by_date = fields.Monetary('Paid by Date')

class vesco_open_invoices(models.TransientModel):
    _name = "spx_vesco.open_invoices"
    
    to_date = fields.Date('As Of',required=True, default=fields.Datetime.now)

    @api.multi
    def customer_invoices(self):
        return self.open_invoices(True)

    @api.multi
    def vendor_bills(self):
        return self.open_invoices(False)


    def open_invoices(self, mode):
        domain = [('date_invoice','<=',self.to_date)]
        if mode:
            label = "Customer Invoices"
            #domain.extend([('type', 'in', ('x3', 'in_refund'))])
            domain.extend([('type', 'in', ('out_invoice', 'in_refund'))])
        else:
            label = "Vendor Bills"
            domain.extend([('type', 'in', ('in_invoice', 'out_refund'))])
        
        invoices = self.env['account.invoice'].search(domain)
        
        data = {}        
        data['date_to']=self.to_date
        
        #logger.error("Records: %s", records)
        record_set = []
        
        for inv in invoices:      
            total_paid_by_date = 0
            for payment in inv.payment_move_line_ids:
                payment_currency_id = False           
                amount_to_show = 0
                if payment.date <= self.to_date:                    
                    if inv.type in ('out_invoice', 'in_refund'):
                        amount = sum([p.amount for p in payment.matched_debit_ids if p.debit_move_id in inv.move_id.line_ids])
                        amount_currency = sum([p.amount_currency for p in payment.matched_debit_ids if p.debit_move_id in inv.move_id.line_ids])
                        if payment.matched_debit_ids:
                            payment_currency_id = all([p.currency_id == payment.matched_debit_ids[0].currency_id for p in payment.matched_debit_ids]) and payment.matched_debit_ids[0].currency_id or False
                
                    if inv.type in ('in_invoice', 'out_refund'):
                        amount = sum([p.amount for p in payment.matched_credit_ids if p.credit_move_id in inv.move_id.line_ids])
                        amount_currency = sum([p.amount_currency for p in payment.matched_credit_ids if p.credit_move_id in inv.move_id.line_ids])
                        if payment.matched_credit_ids:
                            payment_currency_id = all([p.currency_id == payment.matched_credit_ids[0].currency_id for p in payment.matched_credit_ids]) and payment.matched_credit_ids[0].currency_id or False
                            
                    if payment_currency_id and payment_currency_id == inv.currency_id:
                        amount_to_show = amount_currency
                    else:
                        amount_to_show = payment.company_id.currency_id.with_context(date=payment.date).compute(amount, inv.currency_id)
                total_paid_by_date += amount_to_show
                                    
            if total_paid_by_date != inv.amount_total:
                _logger.error("INV %s %s - %s|%s", inv.number, inv.date_invoice, total_paid_by_date, inv.amount_total)

            if total_paid_by_date < inv.amount_total:
                inv.paid_by_date = total_paid_by_date
                if inv.amount_total_signed < 0:
                    inv.paid_by_date = inv.paid_by_date * -1
                record_set.append(inv.id)
                
                
        tree_view_ref = self.env.ref('spx_vesco.open_invoices_tree', False)
        form_view_ref = self.env.ref('account.invoice_form', False)
        

        return {
            'name': "Open " + label + " on " + str(self.to_date),
            'view_mode': 'tree, form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'account.invoice',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': "[('id', 'in', %s)]" % record_set,            
            'views': [(tree_view_ref and tree_view_ref.id or False, 'tree'),
                      (form_view_ref and form_view_ref.id or False, 'form')],            
            'context': {}
        }        

    