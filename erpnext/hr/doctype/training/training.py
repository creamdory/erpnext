# -*- coding: utf-8 -*-
# Copyright (c) 2017, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc

class Training(Document):
	pass

def set_missing_values(source, target):
	target.ignore_pricing_rule = 1
	target.run_method("set_missing_values")
	target.run_method("calculate_taxes_and_totals")

@frappe.whitelist()
def make_training_event(source_name, target_doc=None):

	doc = get_mapped_doc("Training", source_name,	{
		"Training": {
			"doctype": "Training Event",
			"field_map": {
				"training": "training"
			},
			"validation": {
				"docstatus": ["!=", 2],
			}
		},
	}, target_doc, set_missing_values)

	return doc