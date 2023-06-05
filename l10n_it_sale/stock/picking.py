# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2010-2015 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    ddt_number = fields.Char('DDT', size=64, readonly=True)
    ddt_date = fields.Date('DDT date', readonly=True)
    ddt_in_reference = fields.Char('In DDT', size=32)
    ddt_in_date = fields.Date('In DDT Date')
    cig = fields.Char('CIG', size=64, help="Codice identificativo di gara")
    cup = fields.Char('CUP', size=64, help="Codice unico di Progetto")
    code = fields.Selection(related='picking_type_id.code', string=_('Type of Operation'), required=False)
    carriage_condition_id = fields.Many2one('stock.picking.carriage_condition', string=_('Carriage condition'))
    goods_description_id = fields.Many2one('stock.picking.goods_description', string=_('Description of goods'))
    transportation_condition_id = fields.Many2one(
        'stock.picking.transportation_condition',
        string=_('Transportation condition')
    )

    @api.multi
    @api.depends(
        'ddt_number',
        'ddt_in_reference',
        'name',
    )
    def name_get(self):
        res = []
        for picking in self:
            res.append((picking.id, picking.ddt_number or picking.ddt_in_reference or picking.name))
        return res

    @api.one
    @api.constrains(
        'ddt_in_reference',
        'partner_id'
    )
    def _check_ddt_in_reference_unique(self):
        # qui và cercato da gli stock.picking quelli che hanno ddt_in_reference e partner_id uguali
        return True

    # -----------------------------------------------------------------------------
    # EVITARE LA COPIA DI 'NUMERO DDT'
    # -----------------------------------------------------------------------------
    @api.one
    def copy(self, default=None):
        default = default or {}
        default.update({
            'ddt_number': False,
            'ddt_date': False,
            'ddt_in_reference': False,
            'ddt_in_date': False,
            'cig': False,
            'cup': False,
        })

        return super(StockPicking, self).copy(default)

    @api.one
    @api.onchange('picking_type_id')
    def on_change_picking_type_id(self):
        self.code = self.picking_type_id.code


class StockPickingCarriageCondition(models.Model):
    """
    Carriage condition
    """
    _name = "stock.picking.carriage_condition"
    _description = "Carriage Condition"
    name = fields.Char('Carriage Condition', size=64, required=True, readonly=False)
    note = fields.Text('Note')


class StockPickingGoodsDescription(models.Model):
    """
    Description of Goods
    """
    _name = 'stock.picking.goods_description'
    _description = "Description of Goods"

    name = fields.Char('Description of Goods', size=64, required=True, readonly=False)
    note = fields.Text('Note')


class StockPickingTransportationCondition(models.Model):
    """
    Transportation Condition
    """
    _name = "stock.picking.transportation_condition"
    _description = "Transportation Condition"

    name = fields.Char('Transportation Condition', size=64, required=True, readonly=False)
    note = fields.Text('Note')
