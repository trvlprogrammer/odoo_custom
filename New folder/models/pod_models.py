import logging
import os
_logger = logging.getLogger(__name__)

from datetime import datetime

from odoo import api, fields, models, _

class PODSalesOrder(models.Model):
    _inherit = "sale.order"

    commitment_date = fields.Datetime('Commitment Date', readonly=False, track_visibility='onchange')
    client_order_ref = fields.Char(string='Customer Reference', copy=False)

class VescoBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    def _desc(self): 
        for line in self:
            txt = ''
            if line.ref:
                txt = 'Ref: ' + line.ref
            if line.note:
                if txt:
                    txt += ' | '
                txt += 'Note: ' + line.note
            if not txt:
                txt = '|'
            line.name = txt

    name = fields.Char(compute=_desc, string="Calc. Label", required=True)


class Vesco_Invoice_Line(models.Model):
    _inherit = 'account.invoice.line'
    
    def _first_image(self): 
        for invoice in self:
            image = None

            if len(invoice.sale_line_ids) > 0:
                image = invoice.sale_line_ids[0].rpp_image
            else:
                _logger.error("There's no associated SO-Line")
            invoice.rpp_image = image

    rpp_image = fields.Binary(compute=_first_image, string="Product Image", store=True, related=False)




# Avoid Subscribing Customers to Document Status Updates
class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'
    _description = 'Email Thread'

    @api.multi
    def message_subscribe(self, partner_ids=None, channel_ids=None, subtype_ids=None, force=True):
        return False
    
           
class ProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    html_color_widget = fields.Char(string="html data for colored circle in qweb reports", compute='_compute_html_color')
    html_post_processing_widget = fields.Char(string="html data for post-processing circle in qweb reports", compute='_compute_post_circle')

    @api.one
    @api.depends('color')
    def _compute_html_color(self):
        if self.color:
            domain = [('rpp_colour', '=', self.color)]
            color_mapping = self.env['spx_vesco.rpp_colour']
            colors = color_mapping.search(domain)                        
            
            if len(colors) == 1:
                color = colors[:1]
            elif len(colors) > 1:
                _logger.error("There's ambitious mapping of RPP Colors")
                color = ids[:1]
            if len(colors) > 0:
                fill = color.fill_colour
                border = color.border_colour
                text = color.text_colour
                font_size = color.font_size
                code =''
                if color.color_code:
                    code = color.color_code
                self.html_color_widget = f'<div style = "border-radius: 50%; \
                                    margin: auto; \
                                    width: 77px; \
                                    height: 77px; \
                                    background: {fill}; \
                                    border: 4px solid {border}; \
                                    font-size: {font_size}px; \
                                    text-align: center; \
                                    line-height: 71px; \
                                    font-family: Arial; \
                                    color: {text}; \
                                    font-weight: bold;">{code}</div>'


    @api.one
    @api.depends('post_processing')
    def _compute_post_circle(self):
        if self.post_processing:
            domain = [('rpp_post_processing', '=', self.post_processing)]
            color_mapping = self.env['spx_vesco.rpp_post_processing']
            colors = color_mapping.search(domain)

            if len(colors) == 1:
                color = colors[:1]
            elif len(colors) > 1:
                _logger.error("There's ambitious mapping of RPP Post-Processing Codes")
                color = ids[:1]
            if len(colors) > 0:
                fill = color.fill_color
                border = color.border_color
                text = color.text_color
                font_size = color.font_size
                code =''
                if color.color_code:
                    code = color.color_code
                self.html_post_processing_widget = f'<div style = "border-radius: 50%; \
                                    margin: auto; \
                                    width: 77px; \
                                    height: 77px; \
                                    background: {fill}; \
                                    border: 4px solid {border}; \
                                    font-size: {font_size}px; \
                                    text-align: center; \
                                    line-height: 71px; \
                                    font-family: Arial; \
                                    color: {text}; \
                                    font-weight: bold;">{code}</div>'
