# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Didotech Inc. (<http://www.didotech.com>)
#    All Rights Reserved
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
##############################################################################.

from openerp import models, fields, api, _, addons
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta


class ContractContract(models.Model):
    _name = 'contract.contract'
    _description = "Card Contract"

    _inherit = ['mail.thread']

    @api.multi
    def get_referencable_models(self):
        return addons.base.res.res_request.referencable_models(self, self._cr, self._uid, self._context)

    name = fields.Char(string=_('Reference/Description'), index=True,
                       readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([
            ('draft', 'Draft'),
            ('wait_confirm', _('Wait confirmation')),
            ('wait_payment', _('Wait payment')),
            ('active', _('Active')),
            ('expiring', _('Expiration')),
            ('cancel', _('Cancelled')),
            #('suspended', _('Suspended')),
            ('done', _('Done'))
        ], string=_('Status'), index=True, readonly=True, default='draft',
        track_visibility='onchange', copy=False,
        help=" * The 'Draft' status is used when a new contract is created.\n" \
             " * The 'Cancelled' status is used when user cancel contract.")
    parent_id = fields.Many2one('contract.contract', _('Parent Contract'), readonly=True)
    partner_id = fields.Many2one('res.partner', string='Partner', change_default=True,
        required=True, readonly=True, states={'draft': [('readonly', False)]},
        domain="[('customer', '=', True)]")
    contract_date = fields.Date(_('Contract date'))
    expiry_date = fields.Date(_('Expiry'))
    expiry_days = fields.Integer(string=_('Expires after days'), compute='remaining_days', store=False)
    card = fields.Char(string=_('Card Description'), index=True,
                       readonly=True, states={'draft': [('readonly', False)]})
    origin = fields.Reference(get_referencable_models, _('Origin'))
    email_sent = fields.Date(_('Expiring email'))
    renewed = fields.Boolean(compute='compute_renewed')
    
    @api.one
    def compute_renewed(self):
        self.renewed = self.env['mission.mission'].search([('origin', '=', 'contract.contract, {0}'.format(self.id))])
        
    @api.model
    def create(self, values):
        contract = super(ContractContract, self).create(values)
        if contract.partner_id:
            contract.message_subscribe([contract.partner_id.id])
        return contract

    @api.one
    @api.depends('expiry_date')
    def remaining_days(self):
        if self.expiry_date:
            expiry_date = datetime.strptime(self.expiry_date, DEFAULT_SERVER_DATE_FORMAT)
            self.expiry_days = (expiry_date.date() - date.today()).days

    @api.multi
    def action_renew(self):
        assert len(self) == 1, 'This option should only be used for a single id at a time.'

        if self.origin:
            mission = self.origin
            new_mission = mission.copy({
                'origin': "contract.contract, {0}".format(self.id),
                'date_order': fields.Date.today(),
            })
        else:
            service_id = self.env['crm.case.categ'].search([('associated_model', '=', 'contract.contract')])
            
            new_mission = self.env['mission.mission'].create({
                'origin': "contract.contract, {0}".format(self.id),
                'partner_id': self.partner_id.id,
                'date_order': fields.Date.today(),
                'user_id': self.partner_id.user_id and self.partner_id.user_id.id or self._uid,
                'service_id': service_id.id,
                'supplier_id': len(service_id.supplier_ids) == 1 and service_id.supplier_ids.id or False,
            })
        
        new_mission.signal_workflow('action_assign')
        new_mission.signal_workflow('quotation_sent')
        new_mission.signal_workflow('order_confirm')
        new_mission.signal_workflow('executed')
        
        contract_date = self.expiry_date or fields.Date.today()
        contract_date = datetime.strptime(contract_date, DEFAULT_SERVER_DATE_FORMAT)
        
        new_contract = self.copy({
            'name': self.name,
            'contract_date': contract_date.strftime(DEFAULT_SERVER_DATE_FORMAT),
            'expiry_date': (contract_date + relativedelta(years=+1)).strftime(DEFAULT_SERVER_DATE_FORMAT),
            'origin': 'mission.mission, {mission_id}'.format(mission_id=new_mission.id),
            'parent_id': self.id
        })
        
        message = _("Contract renewed")
        self.message_post(body=message)
        
        self.signal_workflow('renew')
        
        return {
            'domain': str([('id', '=', new_contract.id)]),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'contract.contract',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'name': _('Card/Contract'),
            'res_id': new_contract.id
        }

    @api.multi
    def action_active(self):
        assert len(self) == 1, 'This option should only be used for a single id at a time.'
        self.contract_date = self.contract_date or fields.Date.today()
        contract_date = datetime.strptime(self.contract_date, DEFAULT_SERVER_DATE_FORMAT)
        self.expiry_date = self.expiry_date or (contract_date + relativedelta(years=+1)).strftime(DEFAULT_SERVER_DATE_FORMAT)
        self.state = 'active'

    @api.one
    def expired(self):
        if self.expiry_days < 0:
            return True
        else:
            return False

    # The old API way:
    @api.cr_uid_ids_context
    def cron_check_expiry(self, cr, uid, *deadlines):
        today = date.today()
        context = self.pool['res.users'].context_get(cr, uid)
        deadlines = map(int, deadlines)
        deadlines.sort(reverse=True)

        contract_ids = self.search(cr, uid, [('state', 'in', ('active', 'expiring'))])
        for contract in self.browse(cr, uid, contract_ids):
            #print "Checking expiry for contract", contract.id, '....'
            if contract.expiry_date:
                expiry_date = datetime.strptime(contract.expiry_date, DEFAULT_SERVER_DATE_FORMAT).date()
                if expiry_date < today:
                    #print "Contract", contract.id, "expired"
                    contract.signal_workflow('expired')
                else:
                    for days in deadlines:
                        deadline = expiry_date - timedelta(days=days)
                        if deadline < today:
                            if contract.email_sent:
                                email_sent = datetime.strptime(contract.email_sent, DEFAULT_SERVER_DATE_FORMAT).date()
                                if email_sent < deadline:
                                    sent_email = True
                                    break
                                else:
                                    sent_email = False
                            else:
                                sent_email = True
                                break
                        else:
                            sent_email = False
                            break
        
                    if sent_email:
                        if contract.renewed:
                            #print "Contract", contract.id, "already renewed"
                            pass
                        else:
                            #print "Contract", contract.id, "Email should be sent. Remains less than ", days, "days"
                            
                            # send email
                            #partner_ids = [self.partner_id.user_id.id, contract.partner_id.id]
                            records = self._get_followers(cr, uid, [contract.id], None, None, context=context)
                            follower_ids = records[contract.id]['message_follower_ids']
                            
                            contract.message_post(
                                body="Remains less than {days} days for contract {name} to expire.".format(days=days, name=contract.name),
                                partner_ids=follower_ids,
                                subtype='mt_comment',  # 'mail.mt_comment' is the xml_id of 'Discussions'; we generally use it for user input.
                            )
                        
                            contract.write({'email_sent': date.today().strftime(DEFAULT_SERVER_DATE_FORMAT)})
                            contract.signal_workflow('expiration')
