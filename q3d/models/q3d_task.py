import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class Project(models.Model):
    _inherit = 'project.project'

    def get_q3d_batches(self):
        self.ensure_one()
        return {
            'name': _('Completion'),
            'view_type': 'kanban',
            'view_mode': 'kanban,list,form,calendar,pivot,graph,activity',
            'res_model': 'q3d.batch',
            'type': 'ir.actions.act_window',
            'context': {
                'search_default_project_id': self.id
            }
        }


class ProjectTask(models.Model):
    _inherit = 'project.task'

    next_task_id = fields.Many2one("project.task", compute='_compute_next_task')
    prev_task_id = fields.Many2one("project.task", compute='_compute_prev_task')    

    qty_2do = fields.Integer("Quantity 2Do")
    qty_wip = fields.Integer("Quantity In Progress")
    stage_sequence = fields.Integer(related='stage_id.sequence')
    ttp_range = fields.Char("TTP Range")
    #kanban_state State
    #tag_ids Tags
    #description
    #operators
    #operator_ids = fields.Many2many(
        #comodel_name='res.users',
        #relation='q3d.batch',
        #column1='task_id',
        #column2='user_id',
        #string='Operators')

    batch_ids = fields.One2many('q3d.batch', 'task_id', string='Batches')


    @api.depends('predecessor_task_ids')
    def _compute_prev_task(self):
        for task in self:
            result = None
            if task.predecessor_task_ids:
                result = task.predecessor_task_ids[0].task_id
            task.prev_task_id = result

    @api.depends('successor_task_ids')
    def _compute_next_task(self):
        for task in self:
            result = None
            if task.successor_task_ids:
                result = task.successor_task_ids[0].related_task_id
            task.next_task_id = result    

    def get_q3d_batches(self):
        self.ensure_one()
        return {
            'name': _('Completion'),
            'view_type': 'kanban',
            'view_mode': 'kanban,list,form,calendar,pivot,graph,activity',
            'res_model': 'q3d.batch',
            'type': 'ir.actions.act_window',
            'context': {
                'search_default_task_id': self.id
            }
        }
