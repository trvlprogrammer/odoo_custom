# -*- coding: utf-8 -*-
from datetime import date, datetime, timedelta
import logging

_logger = logging.getLogger(__name__)
from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT

class Q3dOrder(models.Model):
    _name = "q3d.order"
    _description = 'Q3D MES Order'

    name = fields.Char("Order Name")
    uuid = fields.Char("UUID")
    
    part_ids = fields.One2many('q3d.part', 'order_id', string='Parts')