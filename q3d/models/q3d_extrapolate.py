# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta
#from scipy import interpolate
import logging

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT

_logger = logging.getLogger(__name__)



class Q3d_WeeklyProductionExtrapolate(models.Model):
    _name = "q3d.weekly_production_extrapolate"
    
    x_week = fields.Integer(string='Week')
    x_volume = fields.Float(digits=(32, 32), string='Volume')



class Q3DBiSQLView(models.Model):
    _inherit = 'bi.sql.view'
    
    def extrapolate_production_data(self):        
        x = []
        y = []
                
        _logger = logging.getLogger(__name__)
        
        #for week in range(23,29):
            #data = self.env['x_bi_sql_view.weekly_volume'].search(
                #[('x_week', '=', week)], limit=1)
            #if data:
                #x.append(week)
                #y.append(data.x_volume)
                #_logger.error("x: "+ str(week) + " | y: " + str(data.x_volume))
        #f = interpolate.CubicSpline(x, y, extrapolate='periodic')
        
        #self.env['q3d.weekly_production_extrapolate'].search([]).unlink()
        
        #for week in range(29,35):
            #addon = {
                #'x_week': week,
                #'x_volume': f(week),
            #}
            
            #_logger.error("x: "+ str(week) + " | y: " + str(f(week)))
            
            
            #self.env['q3d.weekly_production_extrapolate'].create(addon)




    
