# -*- coding: utf-8 -*-
from datetime import date, datetime, timedelta
import logging

_logger = logging.getLogger(__name__)
from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT

class Q3dInspection(models.Model):
    _name = "q3d.inspection"
    _description = 'Q3D Inspection'

    name = fields.Char("Inspection Name", required=True)
    sale_id = fields.Many2one('sale.order', 'Sales Order') # assigned by the RPP handler
    partner_id = fields.Many2one(related='sale_id.partner_id', comodel_name='res.partner', string='Customer')
    category = fields.Selection([('batch', 'Batch'),
                              ('order', 'Order'),
                              ('part', 'Part')], default='batch')
    
    batch_id = fields.Many2one('q3d.batch', 'Batch')
    task_id = fields.Many2one(related='batch_id.task_id', comodel_name="project.task")
    material_id = fields.Many2one(related='batch_id.material_id', comodel_name="product.product", string="Material")
    batch_machine_id = fields.Many2one(related='batch_id.machine_id', comodel_name="q3d.machine")
    machine_id = fields.Many2one(comodel_name="q3d.machine")
    user_id = fields.Many2one(comodel_name="res.users")
    
    date = fields.Date(string='Inspection Date')
    date_order = fields.Datetime(related='sale_id.date_order', string='Order Date')
    date_batch = fields.Datetime(related='batch_id.date_start', string='Batch Date Started')
    
    description = fields.Text('Description')
    note = fields.Char('Comment')
    