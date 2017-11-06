# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import unittest
import frappe
from erpnext.stock.get_item_details import get_price_list_rate_for

class TestItem(unittest.TestCase):

	def test_duplicate_item(self):
		from erpnext.stock.doctype.item_price.item_price import ItemPriceDuplicateItem
		doc = frappe.copy_doc(test_records[0])
		self.assertRaises(ItemPriceDuplicateItem, doc.save)

	def test_addition_of_new_fields(self):
		# Based on https://github.com/frappe/erpnext/issues/8456
		test_fields_existance = [
			'disable', 'customer', 'uom', 'min_qty', 'lead_time_days',
			'packing_unit', 'valid_from', 'valid_upto', 'note'
		]
		doc_fields = frappe.copy_doc(test_records[1]).__dict__.keys()

		for test_field in test_fields_existance:
			self.assertTrue(test_field in doc_fields)

	def test_dates_validation_error(self):
		doc = frappe.copy_doc(test_records[1])
		# Enter invalid dates valid_from  >= valid_upto
		doc.valid_from = "2017-04-20"
		doc.valid_upto = "2017-04-17"
		# Valid Upto Date can not be less/equal than Valid From Date
		self.assertRaises(frappe.ValidationError, doc.save)

	def test_multiple_prices(self):
		doc = frappe.copy_doc(test_records[2])
		doc.min_qty = doc.min_qty + 1
		doc.save()

		doc2 = frappe.copy_doc(test_records[2])
		doc2.price_list_rate = 1.5*doc.price_list_rate
		doc2.min_qty = doc.min_qty - 5
		doc2.save()

		#Check correct price at this quantity
		price = get_price_list_rate_for(doc.price_list, doc.item_code, doc.min_qty)
		self.assertEqual(price, doc.price_list_rate)

		#Check correct price at alternate quantity
		price = get_price_list_rate_for(doc2.price_list, doc2.item_code, doc2.min_qty)
		self.assertEqual(price, doc2.price_list_rate)

		#Check correct price when no quantity
		price = get_price_list_rate_for(doc2.price_list, doc2.item_code, doc2.min_qty - 1)
		self.assertEqual(price, None)


	def test_prices_at_date(self):
		doc = frappe.copy_doc(test_records[3])
		doc.save()

		doc2 = frappe.copy_doc(test_records[3])
		doc2.valid_from = "2017-04-18"
		doc2.valid_upto = "2017-04-26"
		doc2.price_list_rate = 0.75*doc.price_list_rate
		doc2.save()

		#Check correct price at first date
		price = get_price_list_rate_for(doc.price_list, doc.item_code, doc.min_qty, "2017-04-11")
		self.assertEqual(price, doc.price_list_rate)

		#Check correct price at second date
		price = get_price_list_rate_for(doc2.price_list, doc2.item_code, doc2.min_qty, "2017-04-24")
		self.assertEqual(price, doc2.price_list_rate)

		#Check correct price at invalid date
		price = get_price_list_rate_for(doc2.price_list, doc2.item_code, doc2.min_qty, "2017-04-28")
		self.assertEqual(price, None)
		
		doc3 = frappe.copy_doc(test_records[3])
		doc3.price_list_rate = 4*doc.price_list_rate
		doc3.valid_from = None
		doc3.valid_upto = None
		doc3.save()
		
		#Check correct price when there is an always valid price
		price = get_price_list_rate_for(doc2.price_list, doc2.item_code, doc2.min_qty, "2017-04-24")
		self.assertEqual(price, doc2.price_list_rate)

		#Check correct price when outside of the date
		price = get_price_list_rate_for(doc3.price_list, doc3.item_code, doc3.min_qty, "2017-04-30")
		self.assertEqual(price, doc3.price_list_rate)

		#Check lowest price when no date provided
		price = get_price_list_rate_for(doc3.price_list, doc3.item_code, doc3.min_qty)
		self.assertEqual(price, doc2.price_list_rate)


	def test_duplicates(self):
		doc = frappe.copy_doc(test_records[1])
		self.assertRaises(frappe.ValidationError, doc.save)

	def test_invalid_item(self):
		doc = frappe.copy_doc(test_records[1])
		# Enter invalid item code
		doc.item_code = "This is not an item code"
		# Valid item codes must already exist
		self.assertRaises(frappe.ValidationError, doc.save)

	def test_price_list(self):
		doc = frappe.copy_doc(test_records[1])
		# Check for invalid price list
		doc.price_list = "This is not a price list"
		# Valid price list must already exist
		self.assertRaises(frappe.ValidationError, doc.save)


		# Check for disabled price list
		doc = frappe.copy_doc(test_records[1])
		# Enter invalid price list
		pr = frappe.get_doc("Price List", doc.price_list)
		pr.enabled = 0
		pr.save()

		doc.price_list = pr.name
		# Valid price list must already exist
		self.assertRaises(frappe.ValidationError, doc.save)
		pr.enabled = 1
		pr.save()

	def test_price(self):
		doc = frappe.copy_doc(test_records[0])
		doc.min_qty = 5
		doc.save()

		#Check correct price at this quantity
		price = get_price_list_rate_for(doc.price_list, doc.item_code, doc.min_qty)
		self.assertEqual(price, doc.price_list_rate)

		#Check correct price at this quantity + 1
		price = get_price_list_rate_for(doc.price_list, doc.item_code, doc.min_qty + 1)
		self.assertEqual(price, doc.price_list_rate)

		#Check correct price at this quantity - 1
		price = get_price_list_rate_for(doc.price_list, doc.item_code, doc.min_qty - 1)
		self.assertEqual(price, None)


test_records = frappe.get_test_records('Item Price')
