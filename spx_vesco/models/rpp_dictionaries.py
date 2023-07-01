# -*- coding: utf-8 -*-
from datetime import date, datetime, timedelta
import logging
_logger = logging.getLogger(__name__)
from odoo import api, fields, models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT


class VescoMailMessage(models.Model):
    _inherit = "mail.message"
    
    @api.depends('tracking_value_ids')
    def _tracking_summary(self):
        for msg in self:
            msg.tracking_summary = ""
            for track in msg.sudo().tracking_value_ids:
                msg.tracking_summary += '<div><strong>'+ str(track.field)+':</strong> ' + (track.old_value_char or '') + (track.old_value_text or '') +' &rarr; '+ (track.new_value_char or '') + (track.new_value_text or '')+'</div>';
        
    tracking_summary = fields.Text("Tracking Summary", compute="_tracking_summary", store=False)


class VescoRPPMaterial(models.Model):
    _name = "spx_vesco.rpp_material"
    _description = "RPP Material -> Product Mapping"

    name = fields.Char(string='RPP Material', translate=False, required=True)
    rpp_mapped_product = fields.Many2one('product.product', 'Mapped Product', required=True)
    rpp_delivered_product = fields.Many2one('product.product', 'Mapped Product (invoiced on delivery)', required=True)
    


class VescoRPPSalesperson(models.Model):
    _name = "spx_vesco.rpp_salesperson"
    _description = "RPP Salesperson -> Salesperson Mapping"

    name = fields.Char(string='RPP Salesperson', translate=False, required=True)
    rpp_mapped_user = fields.Many2one('res.users', 'Mapped Salesperson', required=True)
    
    
class VescoRPPPT(models.Model):
    _name = "spx_vesco.rpp_payment_terms"
    _description = "RPP Payment Method -> Payment Terms Mapping"
    _rec_name = 'rpp_payment_method'
    _order = 'rpp_payment_method'

    rpp_payment_method = fields.Char(string='RPP Payment Method', translate=False, required=True)
    invoice_ordered = fields.Boolean('Invoice Ordered', description = 'In other words, it requires pre-payment. First off, it lets us invoice the order before delivery.')
    payment_term_id = fields.Many2one(comodel_name='account.payment.term', string='Mapped Payment Term', required=True)
        
        
class VescoRPPPartStatus(models.Model):
    _name = "spx_vesco.rpp_part_status"
    _description = "RPP Part Status -> Production Step Mapping"
    _rec_name = 'rpp_part_status'
    _order = 'sequence'
        
    rpp_part_status = fields.Char(string='RPP Part Status', translate=False, required=True)
    
    stage_id = fields.Many2one(
        comodel_name='q3d.stage',
        string='Mapped Production Stage') #PA-FIXME:, required=True)
    
    task_id = fields.Many2one(
        comodel_name='project.task',
        string='Mapped Production Task')
    
    sequence = fields.Integer(related="stage_id.sequence", readonly=True)
    
    @api.depends('stage_id')
    def _compute_step(self):
        for stat in self:
            stat.prod_step_int = stat.stage_id.id
    
    prod_step_int = fields.Integer("Prod Step Id Workaround", compute='_compute_step')
    
    
    
class VescoRPPColor(models.Model):
    _name = "spx_vesco.rpp_colour"
    _description = "RPP Color Formatting"
    _rec_name = 'rpp_colour'    
    _order = 'rpp_colour'

    rpp_colour = fields.Char(string='RPP Color', translate=False, required=True)
    
    fill_colour = fields.Char(string='Fill Color', translate=False, default='#FFFFFF')
    border_colour = fields.Char(string='Border Color', translate=False, default='#000000')
    text_colour = fields.Char(string='Text Color', translate=False, default='#000000')
    font_size = fields.Integer(string='Font Size', translate=False, default=36)
    color_code = fields.Char(string='Color Code', translate=False, default='XX')


class VescoRPPPostProcessing(models.Model):
    _name = "spx_vesco.rpp_post_processing"
    _description = "RPP Post Processing Circle Formatting"
    _rec_name = 'rpp_post_processing'    
    _order = 'rpp_post_processing'

    rpp_post_processing = fields.Char(string='RPP Post Processing Code', translate=False, required=True)

    fill_color = fields.Char(string='Fill Color', translate=False, default='#FFFFFF')
    border_color = fields.Char(string='Border Color', translate=False, default='#000000')
    text_color = fields.Char(string='Text Color', translate=False, default='#000000')
    font_size = fields.Integer(string='Font Size', translate=False, default=36)
    color_code = fields.Char(string='Color Code', translate=False, default='XX')
