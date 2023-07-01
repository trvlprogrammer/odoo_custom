# -*- coding: utf-8 -*-
from datetime import date, datetime, timedelta
import logging
_logger = logging.getLogger(__name__)
from odoo import api, fields, models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT

    
class Q3d_Defect(models.Model):
    _name = "q3d.defect"
    _description = "Defects Associated with a Step"
    
    name = fields.Char(compute='_compute_name')
    lot_id = fields.Many2one('stock.production.lot', 'Part Lot', required=True)
    step_id = fields.Many2one('q3d.step', 'Step', required=True)
    reason_id = fields.Many2one('q3d.defect.reason', 'Defect Type')
    qty_defect = fields.Integer(string="Defect Quantity")
    
    @api.depends('reason_id', 'reason_id.name')
    def _compute_name(self):
        for record in self:
            if record.reason_id:
                record.name = record.reason_id.name    
    

class Q3d_DefectReason(models.Model):
    _name = "q3d.defect.reason"
    _description = "Defect Type"
    
    name = fields.Char(string='Defect Name')
    legitimate = fields.Boolean(default=False)
        