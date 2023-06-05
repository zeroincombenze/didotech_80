# -*- encoding: utf-8 -*-
# =============================================================================
# For copyright and license notices, see __openerp__.py file in root directory
# =============================================================================

from openerp import models, fields, api, _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def last_invoice(self, sequence, date_invoice, internal_number):
        invoice_date = datetime.strptime(date_invoice, DEFAULT_SERVER_DATE_FORMAT)

        number_template = '{:0%d}' % sequence.padding

        current_number = number_template.format(sequence.number_next_actual - sequence.number_increment)

        prefix = sequence.prefix and sequence.prefix % {
            'year': invoice_date.year,
            'y': invoice_date.strftime('%y'),
            'month': invoice_date.month,
            'day': invoice_date.day,
            'doy':  invoice_date.strftime('%j'),
            'woy': invoice_date.isocalendar()[1],
            'weekday': invoice_date.weekday(),
            'h24': invoice_date.hour,
            'h12': invoice_date.strftime('%I'),
            'min': invoice_date.minute,  # Will never work, missing source info
            'sec': invoice_date.second  # Will never work, missing source info
        } or ''

        suffix = sequence.suffix and sequence.suffix % {
            'year': invoice_date.year,
            'y': invoice_date.strftime('%y'),
            'month': invoice_date.month,
            'day': invoice_date.day,
            'doy':  invoice_date.strftime('%j'),
            'woy': invoice_date.isocalendar()[1],
            'weekday': invoice_date.weekday(),
            'h24': invoice_date.hour,
            'h12': invoice_date.strftime('%I'),
            'min': invoice_date.minute,  # Will never work, missing source info
            'sec': invoice_date.second  # Will never work, missing source info
        } or ''

        current_sequence = '{prefix}{current_number}{suffix}'.format(
            prefix=prefix, current_number=current_number, suffix=suffix
        )

        return current_sequence == internal_number and current_number or False

    @api.multi
    def unlink(self):
        if len(self) == 1:
            for invoice in self:
                sequence = invoice.journal_id.sequence_id
                if invoice.date_invoice:
                    current_sequence_number = self.last_invoice(
                        sequence, invoice.date_invoice, invoice.internal_number)
                    if invoice.state in ('draft', 'cancel') and invoice.internal_number and current_sequence_number:
                        invoice.internal_number = False

            result = super(AccountInvoice, self).unlink()
            sequence.number_next_actual = current_sequence_number
            return result
        else:
            return super(AccountInvoice, self).unlink()
