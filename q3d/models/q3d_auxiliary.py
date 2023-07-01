# -*- coding: utf-8 -*-
from datetime import date, datetime, timedelta
import logging

_logger = logging.getLogger(__name__)
from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT

class Q3DSorter(models.Model):
    _name = 'q3d.sorter'
    _description = 'Q3D Sorter Auxiliary View'
    _rec_name = 'name'
    
    name = fields.Char()
    iframe = fields.Char(string='Iframe Link')
    iframe_web = fields.Html(string='Iframe Presentation', sanitize=False, compute='compute_iframe_web')

    def compute_iframe_web(self):
        for record in self:
            if record.iframe:
                record.iframe_web = '<div><iframe style="display:block; border:none; height:calc(100vh - 140px); width:100%;" src="' + record.iframe + '"/></div>'
            else:
                record.iframe_web = ''


class Q3DStage(models.Model):
    _name = "q3d.stage"
    _description = "Q3D MES Stage (obsolete) in favor of employing project.task"
    _order = 'sequence'

    name = fields.Char(string='Step Name', translate=True)
    task_id = fields.Many2one('project.task', 'Production Phase Update')
    weight = fields.Integer(string='Completion Weight', translate=False)
    delta = fields.Integer(string='Completion Delta', translate=False)
    error_msg = fields.Char(string='Completion Error Message', translate=True)
    sequence = fields.Integer(string="Sequence", default=10)
    responsible = fields.Many2one(comodel_name='res.users', string='Responsible',
                                  help="if not set, queried from today's calendar events by step name. if not found, queried from 05-11 January 2020. if not found, defaults to the Sales Person on the corresponding order.")
    machine_ids = fields.One2many("q3d.machine", "stage_id")

    _sql_constraints = [
        ('weight_uniq', 'unique (weight)',
         'The weight of stage must be unique! See q3d.stage model definition')
    ]


class Q3DKanbanStage(models.Model):
    _inherit = 'base.kanban.stage'
    _description = 'Q3D Kanban Stage Code'

    stage_code = fields.Char('Stage Code', help='Auxiliary Code for using in Programmatic Filters')
    
            
class Q3DProduct(models.Model):
    _inherit = 'product.product'
    _description = 'Q3D Product Code'

    q3d_code = fields.Char('Q3D Code', help='Short Code for Displaying on Q3D Views')    