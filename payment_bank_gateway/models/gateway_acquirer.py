# -*- coding: utf-'8' "-*-"

from openerp.osv import orm, fields
from openerp.tools.translate import _

# from openerp.addons.payment.models.payment_acquirer import ValidationError
# from openerp.tools.float_utils import float_compare
# import pprint

import logging

_logger = logging.getLogger(__name__)


class GatewayPaymentAcquirer(orm.Model):
    _inherit = 'payment.acquirer'

    def _get_providers(self, cr, uid, context=None):
        providers = super(GatewayPaymentAcquirer, self)._get_providers(cr, uid, context=context)
        providers.append(['bank_gateway', _('Bank Gateway')])
        return providers

    _columns = {
        'bank_name': fields.char('Bank Name'),
        'bank_api_username': fields.char('Bank API Username'),
        'bank_api_password': fields.char('Bank API Password'),
        'bank_test_enabled': fields.boolean('Use Test API'),
        'bank_test_username': fields.char('Bank Test Username'),
        'bank_test_password': fields.char('Bank Test Password')
    }

    def transfer_get_form_action_url(self, cr, uid, id, context=None):
        return '/payment/gateway/feedback'

    def _format_gateway_data(self, cr, uid, context=None):
        bank_ids = [bank.id for bank in self.pool['res.users'].browse(cr, uid, uid, context=context).company_id.bank_ids]
        # filter only bank accounts marked as visible
        bank_ids = self.pool['res.partner.bank'].search(cr, uid, [('id', 'in', bank_ids), ('footer', '=', True)], context=context)
        accounts = self.pool['res.partner.bank'].name_get(cr, uid, bank_ids, context=context)
        bank_title = _('Bank Accounts') if len(accounts) > 1 else _('Bank Account')
        bank_accounts = ''.join(['<ul>'] + ['<li>%s</li>' % name for id, name in accounts] + ['</ul>'])
        post_msg = '''<div>
<h3>Please use the following gateway details</h3>
<h4>%(bank_title)s</h4>
%(bank_accounts)s
<h4>Communication</h4>
<p>Please use the order name as communication reference.</p>
</div>''' % {
            'bank_title': bank_title,
            'bank_accounts': bank_accounts,
        }
        return post_msg

    def create(self, cr, uid, values, context=None):
        """ Hook in create to create a default post_msg. This is done in create
        to have access to the name and other creation values. If no post_msg
        or a void post_msg is given at creation, generate a default one. """
        if values.get('provider') == 'bank_gateway' and not values.get('post_msg'):
            values['post_msg'] = self._format_gateway_data(cr, uid, context=context)
        return super(GatewayPaymentAcquirer, self).create(cr, uid, values, context=context)


# class GatewayPaymentTransaction(orm.Model):
#     _inherit = 'payment.transaction'
#
#     def _transfer_form_get_tx_from_data(self, cr, uid, data, context=None):
#         reference, amount, currency_name = data.get('reference'), data.get('amount'), data.get('currency_name')
#         tx_ids = self.search(
#             cr, uid, [
#                 ('reference', '=', reference),
#             ], context=context)
#
#         if not tx_ids or len(tx_ids) > 1:
#             error_msg = 'received data for reference %s' % (pprint.pformat(reference))
#             if not tx_ids:
#                 error_msg += '; no order found'
#             else:
#                 error_msg += '; multiple order found'
#             _logger.error(error_msg)
#             raise ValidationError(error_msg)
#
#         return self.browse(cr, uid, tx_ids[0], context=context)
#
#     def _transfer_form_get_invalid_parameters(self, cr, uid, tx, data, context=None):
#         invalid_parameters = []
#
#         if float_compare(float(data.get('amount', '0.0')), tx.amount, 2) != 0:
#             invalid_parameters.append(('amount', data.get('amount'), '%.2f' % tx.amount))
#         if data.get('currency') != tx.currency_id.name:
#             invalid_parameters.append(('currency', data.get('currency'), tx.currency_id.name))
#
#         return invalid_parameters
#
#     def _transfer_form_validate(self, cr, uid, tx, data, context=None):
#         _logger.info('Validated gateway payment for tx %s: set as pending' % (tx.reference))
#         return tx.write({'state': 'pending'})
