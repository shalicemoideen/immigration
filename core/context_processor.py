
def user_processor(request):
	user = User.objects.get(id=request.user.id)
	return {'user': user}