# Copyright (c) 2017, Frappe and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe

def execute():
	frappe.reload_doctype('Training Event')

	training_events = frappe.get_all("Training Event", fields=["name", "event_name", "training", "trainer_name", \
		"trainer_email", "supplier", "contact_number"])
	for training_event in training_events:
		training_event_doc = frappe.get_doc("Training Event", training_event.name)
		
		if not frappe.db.get_value("Training", training_event_doc.event_name):
			training_doc = frappe.new_doc("Training")
			training_doc.training_name = training_event_doc.event_name
			training_doc.trainer_name = training_event_doc.trainer_name
			training_doc.trainer_email = training_event_doc.trainer_email
			training_doc.supplier = training_event_doc.supplier
			training_doc.contact_number = training_event_doc.contact_number
			training_doc.save(ignore_permissions=True)
			training_doc.submit()
		
		if not training_event_doc.training:
			frappe.db.set_value("Training Event", training_event.name,
				"training", training_event_doc.event_name, update_modified=False)