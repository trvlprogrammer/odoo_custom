# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.osv.expression import get_unaccent_wrapper

import logging
_logger = logging.getLogger(__name__)


class PODPartner(models.Model):
    _inherit = 'res.partner'

    @api.depends('phone')
    def _compute_adapted_phone(self):
        for partner in self:
            if partner.phone:
                adapt = partner.phone.replace(" ", "")
                adapt = adapt.replace("-","")
                adapt = adapt.replace("+","")
                adapt = adapt.replace(" ","")
                adapt = adapt.replace("(0)","")
                if adapt and adapt[0] == "0":
                    adapt = "31"+adapt[1:]
                partner.lookup_phone = adapt

    @api.depends('mobile')
    def _compute_adapted_mobile(self):
        for partner in self:
            if partner.mobile:
                adapt = partner.mobile.replace(" ", "")
                adapt = adapt.replace("-","")
                adapt = adapt.replace("+","")
                adapt = adapt.replace(" ","")
                adapt = adapt.replace("(0)","")
                if adapt and adapt[0] == "0":
                    adapt = "31"+adapt[1:]
                partner.lookup_mobile = adapt

    lookup_phone = fields.Char(compute=_compute_adapted_phone, string="Lookup Phone", required=False, store=True)
    lookup_mobile = fields.Char(compute=_compute_adapted_mobile, string="Lookup Mobile", required=False, store=True)
