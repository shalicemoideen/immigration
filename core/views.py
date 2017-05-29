from django.shortcuts import render, redirect
from django.views.generic import View
from django.shortcuts import HttpResponse
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core import serializers
from django.utils.crypto import get_random_string
import json
import urllib
import StringIO
import zipfile
import os
from django.db.models import Count
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from datetime import datetime

from core.forms import DocumentForm
from immigration.settings import BASE_URL, MEDIA_URL, ADMIN_EMAIL
from core.models import Employee, Document, EmployeeDocument, Division
from core.utils import SendMail


class HomeClass(View):
    template_name = 'core/home.html'

    def get(self, request, *args, **kwargs):
        documents = Document.getAllDocuments()
        user = request.user
        divisions = Division.objects.all()
        return render(request, self.template_name, {'documents': documents , 'user': user, 'divisions': divisions})

    def post(self, request, *args, **kwargs):
        tag = request.POST.get('tag') or 'getDocumentList'
        options = {
            'getDocumentList': self.getDocumentList,
            'listDocument': self.listDocument,
            'createDocument': self.createDocument,
            'createDocumentRequest': self.createDocumentRequest,
            'deleteDocument': self.deleteDocument,
            'deleteEmployee': self.deleteEmployee,
            'getAllDocuments': self.getAllDocuments,
            'profileUpdate': self.profileUpdate,
            }
        result = options[tag](request)
        return JsonResponse(result)

    def getDocumentList(self, request):
        username = request.POST.get('search[value]', None)
        doctype = request.POST.get('doctype', None) if request.POST.get('doctype', None) else 'recieved'
        if doctype == 'recieved':
            if username:
                obj = Employee.objects.filter(completed__exact=1,
                                              email__contains=username).order_by('-pk')
            else:
                obj = Employee.objects.filter(completed__exact=1).order_by('-pk')
        else:
            if username:
                obj = Employee.objects.filter(completed__exact=0,
                                              email__contains=username).order_by('-pk')
            else:
                obj = Employee.objects.filter(completed__exact=0).order_by('-pk')
        draw = request.POST.get('draw', None)
        length = request.POST.get('length', None)
        start = request.POST.get('start', None)
        count = obj.count()
        if(start is not None and length is not None):
            end = start + length
            obj = obj[start:end]
        if count > 0:
            serialized_obj = serializers.serialize('json', obj)
            if serialized_obj:
                serialized_obj = json.loads(serialized_obj)
            data = {'data': serialized_obj, 'recordsTotal': count, 'recordsFiltered': count}
        else:
            data = {'data': [], 'recordsTotal': 0, 'recordsFiltered': 0}
        return data

    def listDocument(self, request):
        name = request.POST.get('search[value]', None)
        if name:
            obj = Document.objects.filter(name__contains=name).order_by('-pk')
        else:
            obj = Document.objects.all().order_by('-pk')

        draw = request.POST.get('draw', None)
        length = request.POST.get('length', None)
        start = request.POST.get('start', None)
        count = obj.count()

        if(start is not None and length is not None):
            end = start + length
            obj = obj[start:end]

        # import ipdb;ipdb.set_trace()
        serialized_obj = serializers.serialize('json', obj)
        serialized_obj = json.loads(serialized_obj)
        result = {
            'data': serialized_obj, 'recordsTotal': count,
            'recordsFiltered': count
        }
        return result

    def createDocument(self, request):
        name = request.POST.get('name', None)
        if name:
            s = Document(name=name)
            s.save()
            result = {
                'status': 'success',
                'data': 'Document added successfully'
            }
        else:
            result = {
                'status': 'failure',
                'error': "Please enter the document name"
            }
        return result

    def createDocumentRequest(self, request):
        email = request.POST.get('email', None)
        name = request.POST.get('name', None)
        cc_email = request.POST.get('cc_email', None)
        description = request.POST.get('description', None)
        division = request.POST.get('division', None)
        cc_email_list = []
        if cc_email:
            cc_email_list = cc_email.split(",")
        subject = request.POST.get('subject', None)
        documentslist = request.POST.getlist('document')
        if email:
            # import ipdb;ipdb.set_trace()
            is_exist = Employee.objects.filter(email__iexact=email, completed=False).exists()
            result = {}
            if is_exist:
                employeeobj = Employee.objects.get(email__iexact=email, completed=False)
                employee_id = employeeobj.id
                employeeobj.subject=subject
                employeeobj.name=name
                employeeobj.save()

                docobj = EmployeeDocument.objects.filter(employee_id=employee_id)
                alreadyadded = []
                for documentpk in documentslist:
                    documentpk not in docobj.values_list('document_id',flat=True)
                    if int(documentpk) not in docobj.values_list('document_id',flat=True):
                        required = True if request.POST.get('document_required_'+documentpk) == "on" else False
                        d = EmployeeDocument.objects.create(employee_id=employee_id, document_id=documentpk, required=required)
                    else:
                        required = True if request.POST.get('document_required_'+documentpk) == "on" else False
                        addedobj = EmployeeDocument.objects.get(employee_id=employee_id, document_id=int(documentpk))
                        addedobj.required = required
                        addedobj.save()
                        alreadyadded.append(documentpk)
                result = {
                    'status': 'success',
                    'data':'Document has been successfully updated',
                    'warning': 'Already append documents {0}'.format(str(alreadyadded)) 
                }
            else:
                unique_id = get_random_string(length=32)
                s = Employee(email=email, token=unique_id, subject=subject, name=name, email_copy=cc_email, description=description, division_id=division)
                s.save()
                for documentpk in documentslist:
                    required = True if request.POST.get('document_required_'+documentpk) == "on" else False
                    d = EmployeeDocument.objects.create(employee=s, document_id=documentpk, required=required)
                try:
                    if(subject == '' or subject is None):
                        subject = 'Marlabs Immigration Document Upload Form'
                    from_email, to = 'noreply@marlabs.com', "%s" %(email)
                    
                    url = "%sdoclogin/?pk=%s" % (BASE_URL, s.id)
                    text_content = 'This is an important message.'

                    plaintext = get_template('core/email.txt')
                    htmly = get_template('core/email.html')

                    d = Context({'url': url ,'token': unique_id, 'name':name})
                    text_content = plaintext.render(d)
                    html_content = htmly.render(d)
                    msg = EmailMultiAlternatives(subject, text_content, from_email, [to], cc=cc_email_list)
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()
                    result = {'status': 'success', 'data': 'Mail has been sent successfully'}
                except Exception as e:
                    Employee.objects.filter(email=email).delete()
                    result = {'status': 'failure', 'error': "Mail sending error "+e.message}
        else:
            result = {'status': 'failure', 'error': "Please enter a valid email id"}
        return result

    def deleteDocument(self, request):
        pk = request.POST.get('pk', None)
        if pk:
            Document.objects.filter(pk=pk).delete()
            result = {'status': 'success', 'data': 'Deleted successfully'}
        else:
            result = {'status': 'failure', 'error': 'Something went wrong..!'}
        return result

    def deleteEmployee(self, request):
        pk = request.POST.get('pk', None)
        if pk:
            empDocs = EmployeeDocument.objects.filter(employee_id = pk)
            for empDoc in empDocs:
                empDoc.file.delete()
            empDel = Employee.objects.get(pk=pk)
            email = empDel.email
            completed = empDel.completed
            empDel.delete()
            if(completed == False):
                subject, from_email, to = 'Marlabs Immigration Document Upload Form - Request Cancelled', 'legal@marlabs.com', "%s" %(email)
                print subject, from_email, to
                text_content = 'This is an important message.'
                plaintext = get_template('core/email_cancelled.txt')
                htmly = get_template('core/email_cancelled.html')
                d = Context({})
                text_content = plaintext.render(d)
                html_content = htmly.render(d)
                msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                msg.attach_alternative(html_content, "text/html")
                msg.send()
            # empDel = Employee.objects.filter(pk=pk)
            # import ipdb;ipdb.set_trace()

            result = {'status': 'success', 'data': 'Deleted successfully'}
        else:
            result = {'status': 'failure', 'error': 'Something went wrong..!'}
        return result

    def getAllDocuments(self, request):
        documents = Document.getAllDocuments()
        serialized_obj = serializers.serialize('json', documents)
        if serialized_obj:
            serialized_obj = json.loads(serialized_obj)
        result = {'status': 'success', 'data': serialized_obj}
        return result
    def profileUpdate(self, request):
        email = request.POST.get('email', None)
        first_name = request.POST.get('first_name', None)
        last_name = request.POST.get('last_name', None)
        old_password = request.POST.get('old_password', None)
        password = request.POST.get('password', None)


class Documentlogin(View):
    template_name = 'document/login.html'
    template_add = 'document/add.html'
    error_page = 'document/error.html'

    def get(self, request, *args, **kwargs):
        pk = request.GET.get('pk', None)
        if pk is None or pk == '':
            return render(request, self.error_page, {'error': 1, 'data': 'Invalid user'})
        else:
            if Employee.objects.filter(pk=pk).exists():
                return render(request, self.template_name, {'pk': pk})
            else:
                return render(request, self.error_page, {'error': 1, 'data': 'Invalid user'})

    def post(self, request, *args, **kwargs):
        pk = request.POST.get('pk', None)
        token = request.POST.get('token', None)
        data = {'pk': pk, 'token': token}

        form = DocumentForm()
        if (pk is None or pk == '') or (token is None or token == ''):
            messages.error(request, 'Invalid token')
            return render(request, self.template_name, {'pk': pk})
        else:
            is_exist = Employee.objects.filter(pk=pk, token=token, completed=False).exists()
            authenticated = 0
            if is_exist:
                documents = EmployeeDocument.objects.select_related().filter(employee_id=pk)
                employee = Employee.objects.get(pk=pk)
                return render(request, self.template_add, {'form': form, 'data': data, 'media_url': MEDIA_URL, 'documents': documents, 'employee': employee, 'authenticated': authenticated})

            else:
                messages.error(request, 'Invalid token')
                return render(request, self.template_name, {'pk': pk})
        

class ConfirmRequest(View):
    error_page = 'document/error.html'
    thank_page = 'document/thank_you.html'

    def post(self, request, *args, **kwargs):
        pk = request.POST.get('pk', None)
        if pk is None or pk == '':
            return render(request, self.error_page, {'error': 1, 'data': 'Invalid user'})
        else:
            if Employee.objects.filter(pk=pk).exists():
                try:
                    obj = Employee.objects.get(pk=pk)
                    division = Division.objects.get(pk=obj.division_id)
                    obj.completed = True
                    obj.save()
                    
                    subject = 'Marlabs Immigration Document Upload Completion'
                    from_email, to = obj.email, "%s" %(division.email)
                    
                    text_content = 'This is an important message.'
                    plain_template = 'core/upload-complete-email.txt'
                    html_template = 'core/upload-complete-email.html'
                    
                    data = {'email':obj.email}
                    
                    result = SendMail(html_template, plain_template, data, subject, text_content, from_email, to)
                    if result:
                        return HttpResponseRedirect('/thankyou/')
                    else:
                        print result
                        return render(request, self.error_page, {'error': 1, 'data': 'Something went wrong'})
                except Exception as e:
                    print e.message
                    return render(request, self.error_page, {'error': 1, 'data': 'Something went wrong'})
            else:
                return render(request, self.error_page, {'error': 1, 'data': 'Invalid user'})

class Thankyou(View):
    thank_page = 'document/thank_you.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.thank_page)


class DocumentList(View):
    template_name = 'document/list.html'
    error_page = 'document/error.html'

    def get(self, request, *args, **kwargs):
        pk = request.GET.get('pk', None)
        if pk is None:
            return render(request, self.template_name, {'error': 1})
        else:
            is_exist = Employee.objects.filter(pk=pk).exists()
            authenticated = 1
            if is_exist:
                documents = EmployeeDocument.objects.select_related().filter(employee_id=pk)
                employee = Employee.objects.get(pk=pk)
                return render(request, self.template_name, { 'media_url': MEDIA_URL, 'documents': documents, 'employee': employee, 'authenticated': authenticated})
            else:
                return render(request, self.error_page, {'error': 1, 'authenticated': authenticated})
        return render(request, self.error_page, {'form': form, 'data': data, 'authenticated': authenticated})
                

class DocumentClass(View):
    template_name = 'document/add.html'
    error_page = 'document/error.html'

    def get(self, request, *args, **kwargs):
        pk = request.GET.get('pk', None)
        token = request.GET.get('token', None)
        data = {'pk': pk, 'token': token}

        form = DocumentForm()
        if pk is None:
            return render(request, self.template_name, {'error': 1})
        else:
            if request.user.is_authenticated():
                is_exist = Employee.objects.filter(pk=pk).exists()
                authenticated = 1
            else:
                is_exist = Employee.objects.filter(pk=pk, token=token).exists()
                authenticated = 0

            if is_exist:
                documents = EmployeeDocument.objects.select_related().filter(employee_id=pk)
                employee = Employee.objects.get(pk=pk)
                return render(request, self.template_name, {'form': form, 'data': data, 'media_url': MEDIA_URL, 'documents': documents, 'employee': employee, 'authenticated': authenticated})
            else:
                return render(request, self.template_name, {'error': 1, 'authenticated': authenticated})
        return render(request, self.template_name, {'form': form, 'data': data, 'authenticated': authenticated})

    def post(self, request, *args, **kwargs):
        form = DocumentForm(request.POST, request.FILES)
        pk = request.POST.get('pk')
        token = request.POST.get('token', None)
        data = {'pk': pk, 'token': token}
        employee_id = request.POST.get('employee_id') or None
        documentslist = request.POST.getlist('document')

        documents = EmployeeDocument.objects.select_related().filter(employee_id=pk)
        for documentlist in documentslist:
            uploadfile = request.FILES.get('upload_document_'+documentlist, '')
            print uploadfile
            if uploadfile != '':
                ed = EmployeeDocument.objects.get(id=documentlist)
                ed.status = 1
                ed.file = uploadfile
                ed.save()
                e = Employee.objects.get(pk=pk)
                e.status = 1
                e.save()
        em = Employee.objects.get(pk=pk)
        em.reported_date = datetime.now()
        em.save()
        # messages.success(request, 'Your documents uploaded successfully')
        return render(request, 'document/verify.html', {'form': form, 'status': "success", 'data': data, 'media_url': MEDIA_URL, 'documents': documents, 'authenticated': 0, 'employee': em})


def downloadDocument(request):
    pk = request.GET.get('pk', None)
    template_name = 'core/error.html'
    if pk:
        # import ipdb;ipdb.set_trace()
        is_exist = EmployeeDocument.objects.filter(employee_id=pk).exists()
        if is_exist:
            documentslist = EmployeeDocument.objects.select_related().filter(employee_id=pk)
            filenames = []

            zip_subdir = documentslist[0].employee.email
            zip_filename = "%s.zip" % (zip_subdir)
            s = StringIO.StringIO()
            zf = zipfile.ZipFile(s, "w")

            fileappend = 0
            for documentlist in documentslist:
                if documentlist.file:
                    fdir, fname = os.path.split(documentlist.file.path)
                    zip_path = os.path.join(zip_subdir, fname)
                    zf.write(documentlist.file.path, zip_path)
                    fileappend = 1
            zf.close()
            if fileappend:
                resp = HttpResponse(s.getvalue(), content_type="application/x-zip-compressed")
                resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
                return resp
            else:
                return render(request, template_name, {'error': 1, 'data': 'There is no file uploaded for this employee'})
        else:
            return render(request, template_name, {'error': 1, 'data': 'Invalid user data provided'})

    else:
        return render(request, template_name,
                      {'error': 1, 'data': 'Invalid user data provided'})

class ChangePassword(View):
    """docstring for ClassName"""
    def get(self, request, *args, **kwargs):
        form = PasswordChangeForm(request.user)
        form.fields['old_password'].widget.attrs = {'class': 'form-control'}
        form.fields['new_password1'].widget.attrs = {'class': 'form-control'}
        form.fields['new_password2'].widget.attrs = {'class': 'form-control'}
        return render(request, 'core/change_password.html', {
            'form': form
        })
        

    def post(self, request, *args, **kwargs):
        form = PasswordChangeForm(request.user, request.POST)
        form.fields['old_password'].widget.attrs = {'class': 'form-control'}
        form.fields['new_password1'].widget.attrs = {'class': 'form-control'}
        form.fields['new_password2'].widget.attrs = {'class': 'form-control'}
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  
            messages.success(request, 'Your password was successfully updated!')
            return redirect('password')
        return render(request, 'core/change_password.html', {
            'form': form
        })


class Profile(View):
    """profile view"""
    def get(self, request, *args, **kwargs):
        user = request.user
        return render(request, 'core/profile.html', {'user': user})

    def post(self, request, *args, **kwargs):
        user = User.objects.get(id=request.user.id)
        email = request.POST.get('email', None)
        first_name = request.POST.get('first_name', None)
        last_name = request.POST.get('last_name', None)
        if email:
            user.email = email
            user.save()
        if first_name:
            user.first_name = first_name
            user.save()
        if last_name:
            user.last_name = last_name
            user.save()
        messages.success(request, 'Your profile has been successfully updated')
        return render(request, 'core/profile.html', {'user': user})


class MediaHandle(View):
    def get(self, request, *args, **kwargs):
        import mimetypes
        mimetypes.init()
        pk = request.GET.get('pk', None)
        token = request.GET.get('token', None)
        valid = False
        try:
            if request.user.is_authenticated():
                valid = True
            elif pk is not None and token is not None:
                if Employee.objects.filter(pk=pk, token=token).exists():
                    valid = True

            if valid:
                file_path = request.path
                file_path = file_path[1:]
                fsock = open(file_path,"rb")
                file_name = os.path.basename(file_path)
                file_size = os.path.getsize(file_path)
                mime_type_guess = mimetypes.guess_type(file_name)
                if mime_type_guess is not None:
                    response = HttpResponse(fsock, content_type=mime_type_guess[0])
                response['Content-Disposition'] = 'attachment; filename=' + file_name
            else:
                response = HttpResponse("You are not allowed to download this document")
        except IOError:
            response = HttpResponseNotFound()
        return response
