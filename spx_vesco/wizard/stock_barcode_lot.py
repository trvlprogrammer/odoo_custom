from odoo import models


class StockBarcodeLot(models.TransientModel):
    _inherit = "stock_barcode.lot"

    def on_barcode_scanned(self, barcode):
        lot_id = self.env["stock.production.lot"].search(
            [("name", "=", barcode), ("product_id", "=", self.product_id.id)]
        )
        if lot_id.sale_line_id:
            suitable_line = self.stock_barcode_lot_line_ids.filtered(
                lambda l: l.move_line_id.move_id.sale_line_id == lot_id.sale_line_id
            )
            if suitable_line:
                vals = dict(
                    lot_name=barcode,
                    qty_done=suitable_line[0].qty_done + 1
                )
                suitable_line[0].update(vals)
                return
        return super(StockBarcodeLot, self).on_barcode_scanned(barcode)
