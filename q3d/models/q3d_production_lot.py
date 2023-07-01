# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

import re, os, logging

from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)


def add_business_days(from_date, add_days):
    business_days_to_add = add_days
    current_date = from_date
    while business_days_to_add > 0:
        current_date += timedelta(days=1)
        weekday = current_date.weekday()
        if weekday >= 5:  # sunday = 6
            continue
        business_days_to_add -= 1
    return current_date


class ProductionLot(models.Model):
    _inherit = 'stock.production.lot'
    _order = 'create_date DESC'

    sale_line_id = fields.Many2one('sale.order.line', 'Sales Order Line', store=True) # assigned by the RPP handler
    sale_id = fields.Many2one('sale.order', 'Sales Order', store=True) # assigned by the RPP handler
    step_ids = fields.One2many('q3d.step', 'lot_id', string='Production Log')
    defect_ids = fields.One2many('q3d.defect', 'lot_id', string='Defects')
    partner_id = fields.Many2one(related='sale_id.partner_id', comodel_name='res.partner', string='Customer')
    shipping_id = fields.Many2one(related='sale_id.partner_shipping_id', comodel_name='res.partner', string='Shipping Address')
    price_unit = fields.Float(related='sale_line_id.price_unit')
    description = fields.Text(related='sale_line_id.name')
    comment = fields.Text("Comment")
    non_conformities = fields.Text(string="Non conformities", track_visibility=True)

    date_order = fields.Datetime(related='sale_id.date_order') # 2Fix: Calculated (for searching)
    date_commitment = fields.Datetime(related='sale_id.commitment_date')
    date_due = fields.Date(string="Due Date", store=True) # assigned by the RPP handler arbitrarily (+9 days)
    ordered_qty = fields.Float(string="Ordered Quantity", related="sale_line_id.product_uom_qty")
    rpp_image = fields.Binary(related='sale_line_id.rpp_image')
    image_url = fields.Char('Image Url', related='sale_line_id.image_url')

    @api.depends('sale_line_id', 'sale_line_id.rpp_filename')
    def _compute_partname(self):
        for lot in self:
            if lot.sale_line_id and lot.sale_line_id.rpp_filename:
                lot.partname = lot.sale_line_id.rpp_filename.replace(" ", "_")

    image_filename = fields.Char("Image Filename", related="sale_line_id.image_filename")
    ddd_filename = fields.Char("3D Filename", related="sale_line_id.ddd_filename")
    image_url = fields.Char("Image Filename", related="sale_line_id.image_url")
    ddd_url = fields.Char("3D Filename", related="sale_line_id.ddd_url")
    
    storage_name = fields.Char(related="sale_line_id.storage_name")
    partname = fields.Char("Adapted Partname", compute='_compute_partname', store=True) # 
    filename = fields.Char('RPP Filename', related='sale_line_id.filename') #

    qty_total = fields.Integer("Total Quantity", help="Integer Value") # 2Fix: compute = assigned by the RPP handler
    qty_lot = fields.Integer("Lot Quantity") # assigned by the RPP handler
    qty_file = fields.Integer("File Quantity", help="Mapped Quantity Filled by the WatchDog")
    qty_defect = fields.Integer("Defect Quantity") # 2Fix: compute based on ALL defects of all associated steps

    redo = fields.Boolean("Redo", help="Indicates whether this lot is a redo")
    former_lot_id = fields.Many2one('stock.production.lot', 'Former Lot', help="references the original lot the repeat is based on")

    ttp = fields.Integer("Time to Print", help="Workdays Left to Produce the Item")

    color = fields.Char(related="sale_line_id.rpp_colour")
    post_processing = fields.Char(related="sale_line_id.rpp_post_processing_services")

    state = fields.Selection([('unassigned', 'Unassigned'),
                              ('partial', 'Partially Assigned'),
                              ('assigned', 'Assigned'),
                              ('done', 'Done')], default='unassigned')

    rpp_volume = fields.Float(related="sale_line_id.rpp_vol")
    rpp_vol_box = fields.Float(related='sale_line_id.rpp_vol_box')
    rpp_wdh = fields.Char(related="sale_line_id.rpp_wdh")

    volume = fields.Float(related='sale_line_id.rpp_vol')
    volume_box = fields.Float(related='sale_line_id.rpp_vol_box')
    bounding_box = fields.Char(related="sale_line_id.rpp_wdh")

    material_code = fields.Char(related="product_id.q3d_code")
    init_code = fields.Char("Init Code")
    file_mapped = fields.Boolean("File Mapped", help="Exclude from further searching file-mapping-wise (Used by the WatchDog)")
    mapped_filename = fields.Char(string='Mapped File Name')
