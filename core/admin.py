from django.contrib import admin

from core.models import Employee, Document, EmployeeDocument, Division

# Register your models here.
admin.site.register(Employee)
admin.site.register(Document)
admin.site.register(EmployeeDocument)
admin.site.register(Division)