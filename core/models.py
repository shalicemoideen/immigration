from django.db import models
from django.utils.translation import ugettext_lazy as _


class Division(models.Model):
	name = models.CharField(max_length=200, null=True, blank=True)
	email = models.EmailField(max_length=100)

	class Meta:
		verbose_name = _("Division")
		verbose_name_plural = _("Division")

	def __str__(self):
		return "{0}".format(self.name)

class Employee(models.Model):
	name = models.CharField(max_length=100, null=True, blank=True)
	email = models.EmailField(max_length=100)
	email_copy = models.CharField(max_length=200, null=True, blank=True)
	subject = models.CharField(max_length=100, null=True, blank=True)
	requested_date = models.DateTimeField(auto_now_add=True)
	reported_date  = models.DateTimeField(blank=True, null=True)
	description = models.TextField(max_length=4000, null=True, blank=True)
	division = models.ForeignKey(Division)
	token = models.CharField(max_length=200)
	status = models.BooleanField(default=False)
	completed = models.BooleanField(default=False)

	class Meta:
		verbose_name = _("Employee")
        verbose_name_plural = _("Employees")
    
	def __str__(self):
        	return self.email


class Document(models.Model):
	name = models.CharField(max_length=500)
	
	class Meta:
		verbose_name = _("Document")
        verbose_name_plural = _("Documents")
	
	def __str__(self):
        	return self.name

	@staticmethod
	def getAllDocuments():
		documents = Document.objects.all()
		return documents



class EmployeeDocument(models.Model):
	"""Employee document listing"""
	employee = models.ForeignKey(Employee)
	document = models.ForeignKey(Document)
	required = models.BooleanField(default=False)
	file     = models.FileField(upload_to='documents/',blank=True,null=True)
	status   = models.BooleanField(default=False)
	received_date  = models.DateTimeField(blank=True, null=True)

	class Meta:
		verbose_name = _("Employee-document")
        verbose_name_plural = _("Employee-documents")

	def __str__(self):
        	return "{0} - {1}".format(self.employee.email, self.document.name)




		
