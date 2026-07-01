app_name = "sharepointfrappe"
app_title = "SharepointFrappe"
app_publisher = "Octo Advisory"
app_description = "Upload attachments to SharePoint and Google Drive from Frappe"
app_email = "team@octoadvisory.com"
app_license = "mit"

# Branding
# ------------------
app_logo_url = "/assets/sharepointfrappe/images/logo_bockhoff.png"

# Apps
# ------------------

override_doctype_class = {
    "File": "sharepointfrappe.overrides.file_override.CustomFile"
}
# required_apps = []

# Each item in the list will be shown as an app in the apps page
add_to_apps_screen = [
    {
        "name": "sharepointfrappe",
        "logo": "/assets/sharepointfrappe/images/logo_bockhoff.png",
        "title": "SharepointFrappe",
        "route": "/app/sf-cloud-connection",
    }
]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_js = "/assets/sharepointfrappe/js/sharepointfrappe_brand.js"

# include js, css files in header of web template
# web_include_css = "/assets/sharepointfrappe/css/sharepointfrappe.css"
# web_include_js = "/assets/sharepointfrappe/js/sharepointfrappe.js"

# Website branding (favicon for portal / guide pages)
# website_context = {
# 	"favicon": "/assets/sharepointfrappe/images/favicon.ico",
# }

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "sharepointfrappe/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "sharepointfrappe/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "sharepointfrappe.utils.jinja_methods",
# 	"filters": "sharepointfrappe.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "sharepointfrappe.install.before_install"
# after_install = "sharepointfrappe.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "sharepointfrappe.uninstall.before_uninstall"
# after_uninstall = "sharepointfrappe.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "sharepointfrappe.utils.before_app_install"
# after_app_install = "sharepointfrappe.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "sharepointfrappe.utils.before_app_uninstall"
# after_app_uninstall = "sharepointfrappe.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "sharepointfrappe.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"sharepointfrappe.tasks.all"
# 	],
# 	"daily": [
# 		"sharepointfrappe.tasks.daily"
# 	],
# 	"hourly": [
# 		"sharepointfrappe.tasks.hourly"
# 	],
# 	"weekly": [
# 		"sharepointfrappe.tasks.weekly"
# 	],
# 	"monthly": [
# 		"sharepointfrappe.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "sharepointfrappe.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "sharepointfrappe.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "sharepointfrappe.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["sharepointfrappe.utils.before_request"]
# after_request = ["sharepointfrappe.utils.after_request"]

# Job Events
# ----------
# before_job = ["sharepointfrappe.utils.before_job"]
# after_job = ["sharepointfrappe.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"sharepointfrappe.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

