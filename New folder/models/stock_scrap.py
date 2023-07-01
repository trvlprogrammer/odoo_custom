# -*- coding: utf-8 -*-

from odoo import api, fields, models


class StockScrap(models.Model):
    _inherit = 'stock.scrap'

    @api.onchange('production_id')
    def _onchange_production_id(self):
        if self.production_id:
            self.location_id = self.production_id.move_raw_ids.filtered(lambda x: x.state not in ('done', 'cancel')) and self.production_id.location_src_id.id or self.production_id.location_dest_id.id,

            if self.production_id.assembly_id:
                lot_ids = self.production_id.assembly_id.assigned_lot_ids.mapped('lot_id').ids
                return {
                    'domain': {
                        'lot_id': [('product_id', '=', self.production_id.product_id.id), ('id', 'in', lot_ids)]
                    },
                    'value': {
                        'product_id': self.production_id.product_id.id,
                        'product_uom_id': self.production_id.product_id.uom_id.id,
                    }
                }
