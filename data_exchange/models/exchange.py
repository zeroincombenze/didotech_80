# -*- encoding: utf-8 -*-
# =============================================================================
# For copyright and license notices, see __openerp__.py file in root directory
# =============================================================================

# from openerp import models, fields, api, _
import jsonrpclib
# from openerp.exceptions import Warning


# class ExchangeSerializer(models.Model):
#     _name = 'exchange.serializer'
#
#     source_model = fields.Selection(selection='get_selections')
#     destination_model = fields.Selection(selection='get_selections')
#     fields = fields.Char()
#     # fields_map = fields.One2many('exchange.serializer.values', 'serializer_id', _('Fields Map'))
#
#
# class ExchangeConfigSerializerValues(models.Model):
#     _name = 'exchange.serializer.values'
#
#     key = fields.Char()
#     value = fields.Char()
#     serializer_id = fields.Many2one('exchange.serializer')
#
#
# class ExchangeData(models.Model):
#     _name = 'exchange.data'
#
#     exchange_type = fields.Selection((
#         ('export', _('Export')),
#         ('import', _('Import'))
#     ), required=True)
#     partner_id = fields.Many2one('res.partner', required=True)
#     serializer_id = fields.Many2one('exchange.serializer', required=True)
#
#     def __init__(self):
#         pdb.set_trace()
#         super(ExchangeData, self).__init__()
#
#     @api.multi
#     def exchange_data(self):
#         if self.exchange_type == 'import':
#             pass


class ExchangeProxy(object):
    def __init__(self, partner):
        self.db = partner.rpc_database
        self.password = partner.rpc_password

        # server proxy object
        url = "{}/jsonrpc".format(partner.rpc_url)
        self.server = jsonrpclib.Server(url)

        # log in the given database
        self.uid = self.server.call(service="common", method="login",
                                    args=[partner.rpc_database, partner.rpc_user, partner.rpc_password])

    def execute(self, model, method, *args):
        args = [self.db, self.uid, self.password, model, method] + list(args)
        return self.server.call(service="object", method="execute", args=args)

    def search(self, model, domain):
        return self.execute(model, 'search', domain)

    def read(self, model, domain, fields):
        return self.execute(model, 'read', domain, {'fields': fields})

    def create(self, model, values):
        return self.execute(model, 'create', values)
