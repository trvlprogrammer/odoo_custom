# -*- coding: utf-8 -*-
#################################################################################
##    Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    You should have received a copy of the License along with this program.
#    If not, see <https://store.webkul.com/license.html/>
#################################################################################
from odoo import models, fields, api, _
AmountOption=[
    ('fixed', 'Fixed Amount'),
    ('percentage', '%  of Product Price')
]
class ProductPackaging(models.Model):
    _inherit = 'product.packaging'
    _rec_name='display_name'
    @api.one
    @api.depends('package_carrier_type','name')
    def _complete_name(self):
        name = self.name
        if self.package_carrier_type:
            name +=  " [%s]" % (self.package_carrier_type)
        self.display_name = name
    @api.model
    def get_cover_amount(self,amount):
        if self.cover_amount_option == 'fixed':
            return self.cover_amount
        return amount* self.cover_amount / 100
    cover_amount_option = fields.Selection(
        selection = AmountOption,
        default ='percentage',
        required=1,
    )
    cover_amount = fields.Integer(
        string='Cover Amount',
        default =10,
        help="""This is the declared
        value/cover amount for an individual package."""
    )
    display_name = fields.Char(
        compute=_complete_name,
        string="Complete Name",
    )
    product_tmpl_ids = fields.Many2many(
        'product.template',
        'product_tmp_product_packaging_rel',
        'packaging_id',
        'product_tmpl_id',
        string='Template'
    )
