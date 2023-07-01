# -*- coding: utf-8 -*-
from datetime import date, datetime, timedelta
import logging

_logger = logging.getLogger(__name__)
from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT

class Q3dPart(models.Model):
    _name = "q3d.part"
    _description = 'Q3D MES Part'

    name = fields.Char("Part Name")
    uuid = fields.Char("UUID")
    order_id = fields.Many2one("q3d.order", 'Q3D Order')
    
    volume = fields.Float()
    volume_box = fields.Float()
    width = fields.Float()
    depth = fields.Float()
    height = fields.Float()
    bounding_box = fields.Char("WDH")    
        
    image_filename = fields.Char("Image Filename")
    image_url = fields.Char("Image", compute='_compute_url')
    ddd_url = fields.Char("3D", compute='_compute_ddd_url')
    ddd_filename = fields.Char("3D Filename")       
    qty = fields.Integer("Quantity", help="Ordered Quantity")

    @api.depends('image_filename')
    def _compute_url(self):
        for item in self:
            if item.image_filename:
                item.image_url = 'https://static.simpleasmagic.com/img/'+item.image_filename
                
    @api.depends('ddd_filename')
    def _compute_ddd_url(self):
        for item in self:
            if item.ddd_filename:
                item.ddd_url = 'https://static.simpleasmagic.com/stl/'+item.ddd_filename
