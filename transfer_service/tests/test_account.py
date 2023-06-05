# -*- coding: utf-8 -*-

"""
Test unlink, 4 cases:
    - invoice line has no origins
    - origin line is sale.order.line
    - origin line created from task
        - task was created from sale.order.line
        - task was created from template.order.line
"""
