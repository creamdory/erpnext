from frappe import _

def get_data():
	return {
		'fieldname': 'training',
		'transactions': [
			{
				'label': _('Training Event'),
				'items': ['Training Event']
			},
		]
	}