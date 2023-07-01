# -*- coding: utf-8 -*-
import logging
_logger = logging.getLogger(__name__)
from odoo import api, fields, models


class Picking(models.Model):
    _inherit = "stock.picking"
    
    @api.multi
    def _add_delivery_cost_to_so(self):
        pass            

    def get_barcode_view_state(self):
        pickings = super(Picking, self).get_barcode_view_state()
        for picking in pickings:
            for move_line_id in picking['move_line_ids']:
                move_line = self.env["stock.move.line"].browse(move_line_id['id'])
                if move_line and move_line.move_id and move_line.move_id.sale_line_id:
                    move_line_id["item_dsc"] = move_line.move_id.sale_line_id.name
                    if move_line.move_id.sale_line_id.rpp_image:
                        move_line_id["item_img"] = move_line.move_id.sale_line_id.image_url
        return pickings

    def action_print_labels(self):
        sale_lot_ids = self.env['stock.production.lot'].search([('sale_id', '=', self.sale_id.id)])
        return self.env['report'].get_action(sale_lot_ids.ids, 'spx_vesco.report_lot_barcode_assembly')

    @api.multi
    def send_to_shipper(self):
        res = super(Picking, self).send_to_shipper()
        self.force_picking_send()

    #@api.multi
    #def write(self, vals):
        #res = super(Picking, self).write(vals)
        #if 'date_done' in vals:
            #self.force_picking_send()
        #return res

    def action_picking_send(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('spx_vesco', 'email_template_picking')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict()
        ctx.update({
            'default_model': 'stock.picking',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "spx_vesco.mail_template_data_notification_email_stock_picking"
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    @api.multi
    def force_picking_send(self):
        for picking in self:
            email_act = picking.action_picking_send()
            if email_act and email_act.get('context'):
                email_ctx = email_act['context']
                email_ctx.update(default_email_from=picking.company_id.email)
                picking.with_context(email_ctx).message_post_with_template(email_ctx.get('default_template_id'),notif_layout="spx_vesco.mail_template_header_footer")
        return True
