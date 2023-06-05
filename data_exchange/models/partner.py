# -*- encoding: utf-8 -*-
# =============================================================================
# For copyright and license notices, see __openerp__.py file in root directory
# =============================================================================

from openerp import models, fields, api, _
from exchange import ExchangeProxy
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class ResPartner(models.Model):
    _inherit = 'res.partner'

    rpc_url = fields.Char()
    rpc_database = fields.Char()
    rpc_user = fields.Char()
    rpc_password = fields.Char()

    partner_mapping_ids = fields.One2many('res.partner.mapping', 'remote_partner_id', string=_("Remote Partner Info"))

    @api.multi
    def action_export_partner(self):
        view_rec = self.env['ir.model.data'].get_object_reference('data_exchange', 'partner_export_form')
        if view_rec:
            view_id = view_rec and view_rec[1] or False
        return {
            'type': 'ir.actions.act_window',
            'name': _('Partner Export'),
            'res_model': 'wizard.export.partner',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [view_id],
            'target': 'new',
            'res_id': False,
            'context': {
                'active_model': 'res.partner',
                'active_ids': self._context['active_ids']
            }
        }

    @api.multi
    def sync_remote(self, remote_partner):
        remote_partner_info_obj = self.env['res.partner.mapping']
        remote = ExchangeProxy(remote_partner)

        def sync_partners(partners):
            for partner in partners:
                remote_partner_info = remote_partner_info_obj.search([
                    ('partner_id', '=', partner.id),
                    ('remote_partner_id', '=', remote_partner.id)
                ])
                if remote_partner_info and remote_partner_info[0].remote_id:
                    # TODO: compare update time and modification time and if the last one is bigger, update partner
                    pass
                else:
                    if partner.vat:
                        remote_partner_ids = remote.search('res.partner', [('vat', '=', partner.vat)])
                    else:
                        return {
                            'error': _("Partner '{}' has no VAT number which is required for synchronization").format(partner.name)
                        }

                    if remote_partner_ids:
                        remote_partner_id = remote_partner_ids[0]
                    else:
                        remote_values = {
                            'name': partner.name,
                            'vat': partner.vat,
                            'customer': partner.customer,
                            'supplier': partner.supplier,
                            'is_company': partner.is_company,
                            'street': partner.street,
                            'street2': partner.street2,
                            'zip': partner.zip,
                            'city': partner.city,
                            'phone': partner.phone,
                            'mobile': partner.mobile,
                            'fax': partner.fax,
                            'email': partner.email
                        }

                        if hasattr(partner, 'fiscalcode'):
                            remote_values['fiscalcode'] = partner.fiscalcode

                        if partner.country_id:
                            country_ids = remote.search('res.country', [('code', '=', partner.country_id.code)])
                            if country_ids:
                                remote_values['country_id'] = country_ids[0]

                        remote_partner_id = remote.create('res.partner', remote_values)

                    remote_partner_info_obj.create({
                        'partner_id': partner.id,
                        'remote_partner_id': remote_partner.id,
                        'remote_id': remote_partner_id,
                        'update_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                    })

                # TODO: sync partner contacts
                # if partner.child_ids:
                #     sync_partners(partner.child_ids)
        sync_partners(self)
        return {}


class ResPartnerMapping(models.Model):
    _name = 'res.partner.mapping'

    partner_id = fields.Many2one('res.partner', string=_("Partner"))
    remote_partner_id = fields.Many2one('res.partner', string=_("Remote Partner"))
    remote_id = fields.Integer(_("Remote ID"))
    update_date = fields.Datetime(_("Last Update"))
