# -*- coding: utf-8 -*-
from datetime import date, datetime, timedelta
import logging

_logger = logging.getLogger(__name__)
from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT

class Q3d_Batch(models.Model):
    _name = "q3d.batch"
    _description = 'Q3D Batch'
    _inherit = ['base.kanban.abstract', 'portal.mixin', 'mail.thread', 'mail.activity.mixin', 'rating.mixin']
    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'name'
    _order = "priority desc, sequence, id desc"

    name = fields.Char("Batch Name")
    scan_id = fields.Many2one("q3d.batch.scan")    
    qty_orders = fields.Integer("Orders", compute="_compute_quantities")
    qty_parts = fields.Integer("Parts")
    qty_items = fields.Integer("Items")
    qty_files = fields.Integer("Files", help="including spare items")
    
    ## Quantities 
    @api.depends('step_ids', 'step_ids.qty_lot', 'step_ids.lot_id', 'step_ids.lot_id.qty_lot')
    def _compute_quantities(self):
        for batch in self:
            orders = []
            parts = 0
            items = 0
            files = 0
            volume = 0.0
            vol_box = 0.0
            for step in batch.step_ids:
                parts = parts + 1
                items = items + step.qty_lot
                files = files + step.qty_found
                volume = volume + step.volume
                vol_box = vol_box + step.volume_box
                if step.order_id and step.order_id.id not in orders:
                    orders.append(step.order_id.id)
            batch.qty_orders = len(orders)
            batch.qty_parts = parts
            batch.qty_items = items
            batch.qty_files = files
            batch.volume = volume
            batch.volume_box = vol_box
    
    date_due_min = fields.Date(string="Min Due Date")
    date_start = fields.Datetime('Started at')
    date_planned = fields.Datetime("Planned at")
    date_group = fields.Date("Planned Date")
    date_end = fields.Datetime('Finished at')
        
    volume = fields.Float("Volume")
    volume_box = fields.Float("Bounding Box Volume")
    
    hours = fields.Integer("Hours to Print")
    comment = fields.Text(string='Comment')

    ##  Duplicate  from Task model
    active = fields.Boolean(default=True)
    task_id = fields.Many2one("project.task")
    color = fields.Integer(related='task_id.color')
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
    ], default='0', index=True, string="Priority")
    sequence = fields.Integer(string='Sequence', index=True, default=10,
                              help="Gives the sequence order when displaying a list of tasks.")
    description = fields.Html(string='Description')
    # In the domain of displayed_image_id, we couln't use attachment_ids because a one2many is represented as a list of commands so we used res_model & res_id
    displayed_image_id = fields.Many2one('ir.attachment',
                                         domain="[('res_model', '=', 'project.task'), ('res_id', '=', id), ('mimetype', 'ilike', 'image')]",
                                         string='Cover Image')
    date_deadline = fields.Date(string='Deadline', index=True, copy=False, track_visibility='onchange')
    tag_ids = fields.Many2many('project.tags', string='Tags')    

    kanban_state = fields.Selection([
        ('normal', 'Grey'),
        ('done', 'Green'),
        ('blocked', 'Red')], string='Kanban State',
        copy=False, default='normal', required=True)
    kanban_state_label = fields.Char(compute='_compute_kanban_state_label', string='Kanban State Label',
                                     track_visibility='onchange')    
    task_detail = fields.Char("Readable Task Name", compute='_compute_task_name')
    task_code = fields.Char("Task Code", related='task_id.task_code')
    task_codename = fields.Char("Task Code", compute='_compute_task_codename', store=True)
    task_sorted = fields.Boolean("Task Sorter", related='task_id.sort_flag')
    stage_code = fields.Char("Stage Code", related='stage_id.stage_code')
    stage_codename = fields.Char("Stage Code", compute='_compute_stage_codename', store=True)
    material_code = fields.Char(related="material_id.q3d_code")
    mapping_ratio = fields.Integer("Mapping Confidence Ratio")
    mapping_notes = fields.Text(string='Mapping Notes')
    
    mapped_at = fields.Datetime('Mapped at')
    exported_at = fields.Datetime('Exported at')
    export_toggle = fields.Boolean("Export")
    rescan_toggle = fields.Boolean("Rescan")
    folders = fields.Char("Folders", help="Serialized list of processed folders to look for")       

    user_id = fields.Many2one('res.users', 'Operator')

    ## PA2: Introduced hierarchy
    parent_id = fields.Many2one(
        comodel_name='q3d.batch',
        string='Parent Batch',
    )
    child_ids = fields.One2many('q3d.batch', 'parent_id', 'Child Batches')
    parent_path = fields.Char(index=True)

    ## Redundant stuff
    project_id = fields.Many2one("project.project", related="task_id.project_id", store=True)
    material_id = fields.Many2one("product.product", string="Material", required=True)
    machine_id = fields.Many2one("q3d.machine")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('valid', 'Validated'),
        ('progress', 'Processing'),
        ('done', 'Complete'),
        ('cancel', 'Cancelled')
    ], default='draft', store=True)

    step_ids = fields.One2many("q3d.step", "batch_id")
    iframe = fields.Many2one('q3d.sorter', string='Iframe')


    @api.depends('stage_id', 'kanban_state')
    def _compute_kanban_state_label(self):
        for batch in self:
            if batch.kanban_state == 'normal':
                batch.kanban_state_label = batch.stage_id.legend_normal
            elif batch.kanban_state == 'blocked':
                batch.kanban_state_label = batch.stage_id.legend_blocked
            else:
                batch.kanban_state_label = batch.stage_id.legend_done

    def _datetime_now(self):
        sd = datetime.now()  # + timedelta(hours=3)
        return sd.strftime(DATETIME_FORMAT)                

        ## Vital Attributes
    @api.depends('task_id', 'task_id.name', 'task_id.project_id', 'task_id.project_id.name')
    def _compute_task_name(self):
        for batch in self:
            result = ''
            if batch.task_id:
                result = batch.task_id.name or ''
                if batch.task_id.project_id:
                    result += ' : ' + batch.task_id.project_id.name or ''
            batch.task_detail = result
            
    @api.depends('task_id', 'task_id.task_code')
    def _compute_task_codename(self):
        for batch in self:
            result = ''
            if batch.task_id:
                result = batch.task_id.task_code
            batch.task_codename = result
            
    @api.depends('stage_id', 'stage_id.stage_code')
    def _compute_stage_codename(self):
        for batch in self:
            result = ''
            if batch.stage_id:
                result = batch.stage_id.stage_code
            batch.stage_codename = result
    
    def get_sorter(self):
        self.ensure_one()
        return {
            'name': _('Completion'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'q3d.sorter',
            'type': 'ir.actions.act_window',
            'res_id': self.iframe.id,
            'context': {'form_view_initial_mode': 'edit', 'force_detailed_view': 'true'}
        }        


class Q3d_Batch_Scan(models.Model):
    _name = "q3d.batch.scan"
    _description = 'Q3D Batch Scan'    
    
    type=fields.Char()
    name=fields.Char()
    alignment=fields.Char()
    coord_x=fields.Float()
    coord_y=fields.Float()
    coord_z=fields.Float()
    coord_x2=fields.Float()
    coord_y2=fields.Float()
    coord_z2=fields.Float()
    normal_x=fields.Float()
    normal_y=fields.Float()
    normal_z=fields.Float()
    trimming_x=fields.Float()
    trimming_y=fields.Float()
    trimming_z=fields.Float()
    dir_x=fields.Float()
    dir_y=fields.Float()
    dir_z=fields.Float()
    length=fields.Float()
    width=fields.Float()
    radius=fields.Float()
    radius2=fields.Float()
    angle=fields.Float()
    orientation=fields.Float()
    edge_radius=fields.Float()
    num_points=fields.Float()
    tol_x_lower=fields.Float()
    tol_x_upper=fields.Float()
    deviation_x=fields.Float()
    tol_y_lower=fields.Float()
    tol_y_upper=fields.Float()
    deviation_y=fields.Float()
    tol_z_lower=fields.Float()
    tol_z_upper=fields.Float()
    deviation_z=fields.Float()
    tol_all_lower=fields.Float()
    tol_all_upper=fields.Float()
    deviation_all=fields.Float()
    tol_normal_lower=fields.Float()
    tol_normal_upper=fields.Float()
    deviation_normal=fields.Float()
    tol_trimming_lower=fields.Float()
    tol_trimming_upper=fields.Float()
    deviation_trimming=fields.Float()
    tol_inplane_lower=fields.Float()
    tol_inplane_upper=fields.Float()
    deviation_inplane=fields.Float()
    tol_length_lower=fields.Float()
    tol_length_upper=fields.Float()
    deviation_length=fields.Float()
    tol_width_lower=fields.Float()
    tol_width_upper=fields.Float()
    deviation_width=fields.Float()
    tol_diameter_lower=fields.Float()
    tol_diameter_upper=fields.Float()
    deviation_diameter=fields.Float()
    tol_angle_lower=fields.Float()
    tol_angle_upper=fields.Float()
    deviation_angle=fields.Float()
    tol_xy_lower=fields.Float()
    tol_xy_upper=fields.Float()
    deviation_xy=fields.Float()
    tol_xz_lower=fields.Float()
    tol_xz_upper=fields.Float()
    deviation_xz=fields.Float()
    tol_yz_lower=fields.Float()
    tol_yz_upper=fields.Float()
    deviation_yz=fields.Float()
    coord_x3=fields.Float()
    coord_y3=fields.Float()
    coord_z3=fields.Float()
    tol_diameter2_lower=fields.Float()
    tol_diameter2_upper=fields.Float()
    deviation_diameter2=fields.Float()