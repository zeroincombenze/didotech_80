# -*- coding: utf-8 -*-
# © 2017 Didotech srl (www.didotech.com)

from openerp import models, fields, api


class MailThread(models.Model):
    _inherit = 'mail.thread'

    @api.model
    def message_route(self, message, message_dict, model=None, thread_id=None,
                      custom_values=None):
        route = super(MailThread, self).message_route(
            message, message_dict, model=model, thread_id=thread_id,
            custom_values=custom_values
        )

        mail_rule_obj = self.env['mail.parent.rule']

        if route and route[0][0] == 'crm.lead' and not route[0][1]:
            for rule in mail_rule_obj.get_rules(message_dict, new_thread=False):
                # thread_id = mail_rule_obj.get_thread_id(rule, message_dict)
                thread_id = rule.get_thread_id(message_dict)
                if thread_id:
                    first_route = list(route[0])
                    first_route[1] = thread_id
                    route[0] = tuple(first_route)
                    break

        return route

    # def message_route_process(self, cr, uid, message, message_dict, routes, context=None):
    #     # postpone setting message_dict.partner_ids after message_post, to avoid double notifications
    #     return super(CrmLead, self).message_route_process(cr, uid, message, message_dict, routes, context=context)

    # def message_update(self, cr, uid, ids, msg, update_vals=None, context=None):
    #     return super(CrmLead, self).message_update(cr, uid, ids, msg, update_vals=update_vals, context=context)


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    @api.model
    def message_new(self, message_dict, custom_values=None):
        # mail_rule_obj = self.env['mail.parent.rule']

        if not custom_values:
            custom_values = {}

        # The right place for this is in message_new() inside crm/crm_lead.py
        if message_dict.get('reply_to') and message_dict.get('from') and message_dict['reply_to'] != message_dict['from']:
            author = self.env['res.partner'].search([('email', 'ilike', message_dict['reply_to'])])
            if author:
                message_dict['author_id'] = author[0].id
            else:
                message_dict['author_id'] = False

            custom_values['email_from'] = message_dict.get('reply_to') or message_dict.get('from')

        # Disabled, because at the moment is not used by anybody
        # for rule in self.env['mail.parent.rule'].get_rules(message_dict, new_thread=True):
        #     email = mail_rule_obj.get_email(rule, message_dict)
        #     if email:
        #         custom_values.update({
        #             'email_from': email,
        #             'from': email
        #         })
        #         partner_ids = self.pool['res.partner'].search([
        #             ('email', 'ilike', email)
        #         ])
        #         if partner_ids:
        #             custom_values['author_id'] = partner_ids[0]
        #         else:
        #             custom_values['author_id'] = False

        return super(CrmLead, self).message_new(message_dict, custom_values=custom_values)

    @api.model
    def set_default_subtype(self):
        followers_obj = self.env['mail.followers']
        default_subtypes = self.env['mail.message.subtype'].search([
            '|',
            ('res_model', '=', self._name),
            ('res_model', '=', False),
            ('default', '=', True)
        ])

        leads = self.search([])
        for follower in followers_obj.search([('res_model', '=', self._name), ('res_id', 'in', leads.ids)]):
            for subtype in default_subtypes:
                if subtype.id not in follower.subtype_ids.ids:
                    follower.write({'subtype_ids': [(6, 0, follower.subtype_ids.ids + [subtype.id])]})
        return True
