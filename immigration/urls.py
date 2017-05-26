"""immigration URL Configuration
"""
from django.conf import settings
from django.conf.urls import include, url, patterns
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required


from core.forms import LoginForm, EmailValidationOnForgotPassword
from core.views import HomeClass, DocumentClass, ChangePassword, Profile, Documentlogin, ConfirmRequest, DocumentList, Thankyou, MediaHandle

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', auth_views.login, {'template_name': 'core/login.html' ,'authentication_form': LoginForm},name='login'),
    url(r'^login', auth_views.login, {'template_name': 'core/login.html','authentication_form': LoginForm},name='login'),
    url(r'^logout', auth_views.logout, {'next_page': '/'}, name='logout'),
    url(r'^documentlist/',login_required(DocumentList.as_view()), name='document-list'),
    url(r'^home',login_required(HomeClass.as_view()), name='home'),
    url(r'^document',DocumentClass.as_view(), name='document'),
    url(r'^doclogin',Documentlogin.as_view(), name='document-login'),    
    url(r'^thankyou/',Thankyou.as_view(), name='thankyou'),    
    url(r'^confirmrequest',ConfirmRequest.as_view(), name='confirm-request'),
    url(r'^downloadDocument$', 'core.views.downloadDocument', name='download-document'),
    url(r'^password$', login_required(ChangePassword.as_view()), name='password'),
    url(r'^profile$', login_required(Profile.as_view()), name='profile'),
    url(r'^media/(?P<path>.*)$', MediaHandle.as_view(), {
        'document_root': settings.MEDIA_ROOT}),
    # url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
    #     'document_root': settings.MEDIA_ROOT}),
]

urlpatterns =urlpatterns+patterns('django.contrib.auth.views',
    url(r'^password/reset/$', auth_views.password_reset, name='password_reset', 
        kwargs={'template_name': 'registration/password_resetform.html', 'subject_template_name': 'registration/password_resetsubject.txt', 'password_reset_form': EmailValidationOnForgotPassword}),
    url(r'^password/done/$', 'password_reset_done', name='password_reset_done', kwargs={
        'template_name': 'registration/password_resetdone.html'
    }),
    url(r'^password/confirm/(?P<uidb64>.+)/(?P<token>.+)/$', 'password_reset_confirm', name='password_reset_confirm',kwargs={
        'template_name': 'registration/password_resetconfirm.html'
        } ),
    url(r'^password/complete/$', 'password_reset_complete', name='password_reset_complete',kwargs={
        'template_name': 'registration/password_resetcomplete.html'} ),
)


if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns


        
