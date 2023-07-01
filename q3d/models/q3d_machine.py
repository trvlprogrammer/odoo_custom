# -*- coding: utf-8 -*-
from datetime import date, datetime, timedelta
import logging

_logger = logging.getLogger(__name__)
from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT

class Q3dMachine(models.Model):
    _name = "q3d.machine"
    _description = 'Q3D MES Machine'

    name = fields.Char("Machine Name", required=True)
    suffix = fields.Char("Suffix", required=True)
    hours = fields.Integer("Production Time (Hours)")
    material_id = fields.Many2one("product.product", string="Material", required=True)
    by_default = fields.Boolean("By Default", default=False) #2Fix: No idea what it is for
    batch_ids = fields.One2many("q3d.batch", "machine_id")
    stage_id = fields.Many2one("q3d.stage", 'Production Step')
    material_ids = fields.Many2many("product.product", relation='q3d_machine_materials', string="Applicable Materials")

