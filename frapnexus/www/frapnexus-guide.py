import frappe

no_cache = 1


def get_context(context):
	context.no_cache = 1
	context.title = "FrapNexus — Setup Guide"
	context.show_sidebar = False
	return context
