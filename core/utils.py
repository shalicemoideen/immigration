from django.template.loader import get_template
from django.template import Context
from django.core.mail import EmailMultiAlternatives

def SendMail(htmlTemplate, textTemplate, data, subject, text_content, from_email, to ):
	try:
		plaintext = get_template(textTemplate)
		htmly = get_template(htmlTemplate)
		d = Context(data)
		text_content = plaintext.render(d)
		html_content = htmly.render(d)
		msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
		msg.attach_alternative(html_content, "text/html")
		msg.send()
		return True
	except Exception as e:
		print e
		return e
