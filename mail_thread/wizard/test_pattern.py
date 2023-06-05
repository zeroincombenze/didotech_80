# -*- coding: utf-8 -*-
# © 2017 Didotech srl (www.didotech.com)

from openerp import models, fields, api
from openerp.tools.translate import _
import re


class WizardTestPattern(models.TransientModel):
    _name = 'wizard.test.pattern'

    rule_id = fields.Many2one('mail.parent.rule', string='Rule')
    pattern = fields.Char(related='rule_id.pattern', string='Pattern')
    text = fields.Text('Text to test')
    result = fields.Char('Test Result', readonly=True)

    @api.multi
    def action_test_string(self):
        if self.text:
            try:
                match = re.search(self.pattern, self.text)
                if match:
                    search_pattern = self.rule_id.prefix or ''
                    search_pattern += match.group(1)
                    search_pattern += self.rule_id.suffix or ''
                    self.result = "Pattern: '{}'".format(search_pattern)
                else:
                    self.result = "Pattern don't match"
            except:
                self.result = "Wrong pattern"
        else:
            self.result = ''

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
            'res_id': self.id,
        }
