# -*- coding: utf-8 -*-
import logging
import os
_logger = logging.getLogger(__name__)

from datetime import datetime

from odoo import api, fields, models, _


class Vesco_SO_Line(models.Model):
    _inherit = 'sale.order.line'

    custom_info = fields.Char(string='Custom Info', translate=False, readonly=False)
    rpp_image = fields.Binary(string='Product Image', related=False)

    rpp_sequence = fields.Integer(string="RPP Line Number", readonly=True)
    rpp_part_status = fields.Char(string='rpp_part_status', translate=False, readonly=True)
    rpp_build_status = fields.Char(string='rpp_build_status', translate=False, readonly=True)
    rpp_height = fields.Char(string='rpp_height', translate=False, readonly=True)
    rpp_width = fields.Char(string='rpp_width', translate=False, readonly=True)
    rpp_depth = fields.Char(string='rpp_depth', translate=False, readonly=True)
    rpp_volume = fields.Char(string='rpp_volume', translate=False, readonly=True)
    rpp_surface_area = fields.Char(string='rpp_surface_area', translate=False, readonly=True)
    rpp_shrink_wrap_volume = fields.Char(string='rpp_shrink_wrap_volume', translate=False, readonly=True)
    rpp_unit = fields.Char(string='rpp_unit', translate=False, readonly=True)
    rpp_request_message = fields.Char(string='rpp_request_message', translate=False, readonly=True)
    rpp_custom_part_name = fields.Char(string='rpp_custom_part_name', translate=False, readonly=True)
    rpp_orientation = fields.Char(string='rpp_orientation', translate=False, readonly=True)
    rpp_service_id = fields.Char(string='rpp_service_id', translate=False, readonly=True)
    rpp_service_name = fields.Char(string='rpp_service_name', translate=False, readonly=True)
    rpp_technology = fields.Char(string='rpp_technology', translate=False, readonly=True)
    rpp_machine = fields.Char(string='rpp_machine', translate=False, readonly=True)
    rpp_material = fields.Char(string='rpp_material', translate=False, readonly=True)
    rpp_material_group = fields.Char(string='rpp_material_group', translate=False, readonly=True)
    rpp_colour = fields.Char(string='Colour', translate=False, readonly=True)
    rpp_colour_group = fields.Char(string='rpp_colour_group', translate=False, readonly=True)
    rpp_layer_thickness = fields.Char(string='rpp_layer_thickness', translate=False, readonly=True)
    rpp_resolution = fields.Char(string='rpp_resolution', translate=False, readonly=True)
    rpp_post_processing_services = fields.Char(string='Post Processing', translate=False, readonly=True)
    rpp_production_time = fields.Char(string='rpp_production_time', translate=False, readonly=True)
    rpp_colour_code = fields.Char(string='rpp_colour_code', translate=False, readonly=True)
    rpp_infill = fields.Char(string='rpp_infill', translate=False, readonly=True)
    
    def _compute_partid_shell(self):
        domain = [('sale_line_id', '=', False), ('name', 'like', 'VOR-')]
        lots = self.env['stock.production.lot'].search(domain)
        for lot in lots:
            order_name = lot.name.rsplit('-',1)[0]
            order_sequence = lot.name.rsplit('-',1)[1]
            so_domain = [('name', '=', order_name)]
            sos = self.env['sale.order'].search(so_domain)
            so_id = 0
            if len(sos) > 0:
                so_id = sos[0].id
                sol_domain = [('order_id', '=', so_id), ('rpp_sequence', '=', int(order_sequence))]
                sols = self.env['sale.order.line'].search(sol_domain)
                sol_id = 0
                if len(sols) > 0:
                    sol = sols[0]
                    sol_id = sol.id
                    sol.rpp_partid = lot.name
                if sol_id > 0:
                    lot.sale_id = so_id
                    lot.sale_line_id = sol_id

    rpp_filename = fields.Char(string='RPP Filename', translate=False, readonly=True, help='Original filename of the 3D Model')
    filename = fields.Char(string='Filename', compute='_compute_filename', help='Somewhat adapted original filename of the 3D Model')
    @api.depends('rpp_filename')
    def _compute_filename(self):
        for item in self:
            if item.rpp_filename:
                item.filename = os.path.basename(item.rpp_filename)

    rpp_vol = fields.Float(string='RPP Volume', compute='_compute_volume', store=True)
    rpp_vol_box = fields.Float("B.Box Volume", compute = '_compute_volume_box', store=True)
    rpp_wd = fields.Float(string='Width', compute='_compute_width', store=True)
    rpp_dp = fields.Float(string='Depth', compute='_compute_depth', store=True)
    rpp_ht = fields.Float(string='Height', compute='_compute_height', store=True)
    rpp_wdh = fields.Char("RPP WDH", compute='_compute_bounding')

    q3d_volume = fields.Float()

    # Q3D Measurements
    volume = fields.Float()
    volume_box = fields.Float()
    width = fields.Float('Width')
    depth = fields.Float('Depth')
    height = fields.Float('Height')
    bounding_box = fields.Char("WDH")

    image_filename = fields.Char("Image Filename")
    image_url = fields.Char("Image", compute='_compute_url')
    ddd_url = fields.Char("3D", compute='_compute_ddd_url')
    ddd_filename = fields.Char("3D Filename")
    storage_name = fields.Char("Storage Name", help="Physical storage (server), containing the part's data")
    # partid. Index is for the dashboard to work faster (join by)
    rpp_partid = fields.Char('rpp_partid', translate=False, readonly=True, index=True)

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


    @api.depends('rpp_height', 'rpp_width', 'rpp_depth')
    def _compute_bounding(self):
        for item in self:
            if item.rpp_width and item.rpp_depth and item.rpp_height:
                item.rpp_wdh = str(round(float(item.rpp_width),1)) + "x" +str(round(float(item.rpp_depth),1)) + "x" + str(round(float(item.rpp_height),1)) + " mm²"

    @api.depends('rpp_shrink_wrap_volume')
    def _compute_volume_box(self):
        for item in self:
            if item.rpp_shrink_wrap_volume:
                item.rpp_vol_box = round(float(item.rpp_shrink_wrap_volume),2)

    @api.depends('rpp_volume')
    def _compute_volume(self):
        for item in self:
            if item.rpp_volume:
                item.rpp_vol = round(float(item.rpp_volume),2)

    @api.depends('rpp_height')
    def _compute_height(self):
        for item in self:
            if item.rpp_height:
                item.rpp_ht = round(float(item.rpp_height),2)

    @api.depends('rpp_width')
    def _compute_width(self):
        for item in self:
            if item.rpp_width:
                item.rpp_wd = round(float(item.rpp_width),2)

    @api.depends('rpp_depth')
    def _compute_depth(self):
        for item in self:
            if item.rpp_depth:
                item.rpp_dp = round(float(item.rpp_depth),2)
            
    @api.depends('rpp_filename')
    def _compute_filename(self):
        for item in self:
            if item.rpp_filename:
                item.filename = os.path.basename(item.rpp_filename)
