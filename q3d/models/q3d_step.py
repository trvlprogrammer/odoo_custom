# -*- coding: utf-8 -*-
from datetime import date, datetime, timedelta
import logging
_logger = logging.getLogger(__name__)
from odoo import api, fields, models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT


class Q3d_step(models.Model):
    _name = "q3d.step"
    _description = "Production Step"
    _rec_name = 'name'
    _order = 'date_start DESC'

    def _datetime_now(self):
        sd = datetime.now() # + timedelta(hours=3)
        return sd.strftime(DATETIME_FORMAT)

    lot_id = fields.Many2one('stock.production.lot', 'Part Lot')
    task_id = fields.Many2one('project.task', 'Stage', compute='_compute_task', store=True)
    task_override_id = fields.Many2one('project.task', 'Stage Override')
    task_name = fields.Char(related='batch_id.task_id.name')
    task_codename = fields.Char(related='batch_id.task_codename')

    order_id = fields.Many2one(related='lot_id.sale_id')
    order_name = fields.Char(related='lot_id.sale_id.name')

    stage_id = fields.Many2one('q3d.stage', 'Stage (obsolete)')
    next_id = fields.Many2one('q3d.batch', 'Next Batch Id')
    next_name = fields.Char(related='next_id.name')
    date_start = fields.Datetime('Started at', default=_datetime_now)
    date_end = fields.Datetime('Finished at')

    # 3D Dispatcher Update
    batch_id = fields.Many2one('q3d.batch', 'Batch')
    defect_ids = fields.One2many('q3d.defect', 'step_id', string='Defects')
    
    quantity = fields.Integer("Legacy Quantity", help="Legacy. Ambiguous. Get rid of it.")
    qty_mapped = fields.Integer("Mapped Qty", help="Mapped Quantity Filled by the WatchDog (redundancy)") # (2Fix: check whether it update the original field this way)
    qty_found = fields.Integer("Found Quantity")
    qty_defect = fields.Integer("Defect Quantity") # 2Fix: compute based on associated defects
    qty_total = fields.Integer(related='lot_id.qty_total')
    qty_lot = fields.Integer(related='lot_id.qty_lot')
    
    ttp = fields.Integer(related='lot_id.ttp')
    redo = fields.Boolean(related='lot_id.redo')
    
    rpp_volume = fields.Float(related='lot_id.sale_line_id.rpp_vol')    
    rpp_vol = fields.Float(related='lot_id.sale_line_id.rpp_vol')
    rpp_wdh = fields.Char(related="lot_id.sale_line_id.rpp_wdh")
    
    volume = fields.Float(related='lot_id.sale_line_id.rpp_vol')
    volume_box = fields.Float(related='lot_id.sale_line_id.rpp_vol_box')
    bounding_box = fields.Char(related="lot_id.sale_line_id.rpp_wdh")    
    
    color = fields.Char(string='Color')
    state = fields.Char(string='State') # except for those of Batch, there should be Damaged state
    sequence = fields.Integer(related='stage_id.sequence', readonly=True)
    responsible = fields.Many2one('res.users', 'Responsible', help="Deprecated. Filled by the RPP Handler based on the Calendar Stencil") # 2Fix: Filled by the RPP Handler
    operator = fields.Many2one('res.users', 'Responsible', related='batch_id.user_id')
    rpp_image = fields.Binary(related='lot_id.sale_line_id.rpp_image')
    image_url = fields.Char('Image Url', related='lot_id.sale_line_id.image_url')
    
    name = fields.Char(related='lot_id.name')
    display_name = fields.Char(related='lot_id.display_name')
    material_code = fields.Char(related='lot_id.product_id.q3d_code')
    partname = fields.Char(related='lot_id.partname')
    mapped_filename = fields.Char(related='lot_id.mapped_filename')
    mapping_ratio = fields.Integer("Mapping Confidence Ratio")

    # We store generic attributes of the part on the SO.Line level
    image_filename = fields.Char("Image Filename", related="lot_id.sale_line_id.image_filename")
    ddd_filename = fields.Char("3D Filename", related="lot_id.sale_line_id.ddd_filename")
    storage_name = fields.Char(related="lot_id.sale_line_id.storage_name")
    image_url = fields.Char("Image Filename", related="lot_id.sale_line_id.image_url")
    ddd_url = fields.Char("3D Filename", related="lot_id.sale_line_id.ddd_url")
    

    
    @api.depends('batch_id', 'batch_id.task_id', 'task_override_id')
    def _compute_task(self):
        for step in self:
            if step.task_override_id:
                step.task_id = step.task_override_id
            else:
                step.task_id = step.batch_id.task_id    
