# -*- coding: utf-8 -*-
# © 2017 Didotech srl (www.didotech.com)

from openerp import models, fields, api
from openerp.tools.translate import _
from openerp.addons.mail.mail_message import decode
import re


class MailParentRule(models.Model):
    _name = 'mail.parent.rule'

    @api.multi
    def _check_text_selected(self):
        if self.subject or self.body:
            return True
        else:
            return False

    name = fields.Char(required=True)
    sequence = fields.Integer('Sequence')
    model = fields.Many2one('ir.model', string='Model', required=True)
    domain = fields.Char('Domain (after @)')
    prefix = fields.Char()
    suffix = fields.Char()
    pattern = fields.Char(required=True)
    subject = fields.Boolean()
    body = fields.Boolean()
    new_thread = fields.Boolean()

    _order = 'sequence'

    _constraints = [
        (
            _check_text_selected,
            _('At least one among Subject and Body should be selected'),
            ['subject', 'body']
        )
    ]

    models = set()

    # @api.model
    # def get_models(self):
    #     # TODO: add cache. Cache should be updated when adding new rule
    #     models = [rule.model.model for rule in self.search([])]
    #     models = list(set(models))
    #     return models

    @api.model
    def get_rules(self, values, new_thread):
        email_from = values.get('email_from', False)
        if email_from:
            email_pattern = re.compile(r"@([\w.]+)")
            domain_match = email_pattern.search(email_from)
            if domain_match:
                domain = [
                    ('domain', '=', domain_match.group(1)),
                    ('new_thread', '=', new_thread)
                ]
                return self.search(domain, order='sequence asc')
        return []

    @api.model
    def get_thread_id(self, values):
        email_text_parts = ('subject', 'body')
        for email_part in email_text_parts:
            if getattr(self, email_part):
                text_to_check = values.get(email_part, '')
                if text_to_check:
                    match = re.search(self.pattern, text_to_check)
                    if match:
                        search_pattern = self.prefix or ''
                        search_pattern += match.group(1)
                        search_pattern += self.suffix or ''
                        email_query = [
                            ('model', '=', self.model.model),
                            (email_part, 'ilike', search_pattern)
                        ]
                        if self.domain:
                            email_query.append(('email_from', '=ilike', '%@{}%'.format(self.domain)))

                        messages = self.env['mail.message'].search(email_query)
                        if messages and messages[0].res_id:
                            self.env[self.model.model].browse(messages[0].res_id).message_post(
                                body=_("Forced association of '{}' to this thread").format(
                                    values.get('subject', '')))
                            return messages[0].res_id

        return False

    @api.multi
    def action_match_test(self):
        test = self.env['wizard.test.pattern'].create({
            'rule_id': self.id
        })
        view = self.env['ir.model.data'].get_object_reference('mail_thread', 'wizard_test_string_form')
        view_id = view and view[1] or False

        return {
            'type': 'ir.actions.act_window',
            'name': _('Test Pattern'),
            'res_model': 'wizard.test.pattern',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [view_id],
            'target': 'new',
            'res_id': test.id
        }

    def get_email(self, rule, message_dict):
        body = message_dict['body']
        match = re.search(rule.pattern, body)
        if match:
            return match.group(1)
        else:
            return False


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def message_parse(self, cr, uid, message, save_original=False, context=None):
        message_dict = super(MailThread, self).message_parse(
            cr, uid, message, save_original=save_original, context=context
        )
        message_dict['reply_to'] = decode(message.get('reply-to'))
        return message_dict


# class MailMessage(models.Model):
#     _inherit = 'mail.message'
#
#     body = fields.Html(select=1)
#     subject = fields.Char(select=1)
