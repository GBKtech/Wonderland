from django import forms
from multiupload.fields import MultiImageField
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserExtend
import re
from django.core.exceptions import ObjectDoesNotExist

TEXT_COLOR = ( ('black', 'Black'), ('red', 'Red'), ('blue', 'Blue'), ('green', 'Green'), ('purple', 'Purple'), 
	('yellow', 'Yellow'), )
GENDER_OPT = ( ('m', 'Male'), ('f', 'Female'), )

class CreateTopicForm(forms.Form):
	subject = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control'}),)
	message = forms.CharField(max_length=990, widget=forms.Textarea(attrs={'class': 'form-control',
		'id': 'message'}),)
	color = forms.CharField(max_length=6, widget=forms.Select(choices=TEXT_COLOR, attrs={'class': 'form-control'}),)
	attachments = MultiImageField(min_num=1, max_num=4, max_file_size=1024*1024*4, required=False)

	def clean_message(self):
		data = self.cleaned_data['message']
		
		new_string = data.split(' ')
		compare_with = ['fuck', 'ass', 'dick', 'stupid', 'bastard', 'pussy', 'mad', 'idiot', 'fucking', 'fool',]
		
		for i in range(0,len(compare_with)):
			for a in range(0,len(new_string)):
					if compare_with[i] == new_string[a]:
						new_string[a] = '*' * len(new_string[a])

		# Remember to always return the cleaned data.
		return ' '.join(new_string)

class CreateCommentForm(forms.Form):
	comment = forms.CharField(max_length=990, widget=forms.Textarea(attrs={'class': 'form-control', 
		'id': 'comment'}),)
	color = forms.CharField(max_length=6, widget=forms.Select(choices=TEXT_COLOR, attrs={'class': 'form-control'}), )
	attachments = MultiImageField(min_num=1, max_num=4, max_file_size=1024*1024*4, required=False)

	def clean_comment(self):
		data = self.cleaned_data['comment']
		
		new_string = data.split(' ')
		compare_with = ['fuck', 'ass', 'dick', 'stupid', 'bastard', 'pussy', 'mad', 'idiot', 'fucking', 'fool',]
		
		for i in range(0,len(compare_with)):
			for a in range(0,len(new_string)):
					if compare_with[i] == new_string[a]:
						new_string[a] = '*' * len(new_string[a])

		# Remember to always return the cleaned data.
		return ' '.join(new_string) 


class SignupForm(UserCreationForm):
	username = forms.CharField(
		label='Username',
		widget=forms.TextInput(attrs={'class': 'form-control'}), 
		max_length=20
	)
	email = forms.EmailField(
		label='Email', 
		widget=forms.EmailInput(attrs={'class': 'form-control'})
		)
	password1 = forms.CharField(
		label='Password',
		min_length = 8,
		widget=forms.PasswordInput(attrs={'class': 'form-control'})
	)
	password2 = forms.CharField(
		label='Password (Again)',
		min_length = 8,
		widget=forms.PasswordInput(attrs={'class': 'form-control'})
	)

	class Meta:
		model = User
		fields = ('username', 'email', 'password1', 'password2')

	def clean_password2(self):
		if 'password1' in self.cleaned_data:
			password1 = self.cleaned_data['password1']
			password2 = self.cleaned_data['password2']
			if password1 == password2:
				return password2
		raise forms.ValidationError('Passwords do not match.')

	def clean_username(self):
		username = self.cleaned_data['username']
		if not re.search(r'^\w+$', username):
			raise forms.ValidationError('Username can only contain alphanumeric characters and the underscore.')
		try:
			User.objects.get(username=username)
		except ObjectDoesNotExist:
			return username
		raise forms.ValidationError('Username is already taken.')

	# def clean_email(self):
	# 	email = self.cleaned_data['email']
	# 	try:
	# 		User.objects.get(email=email)
	# 	except ObjectDoesNotExist:
	# 		return email
	# 	raise forms.ValidationError('Email account already exists')

class EditProfileForm(forms.Form):
	attach = MultiImageField(label='Change Display Picture', 
		min_num=1, max_num=1, max_file_size=1024*1024*4, required=False)
	brief_desc = forms.CharField(label='Brief Description', max_length=200, 
		widget=forms.Textarea(attrs={'class': 'form-control', 'cols': 20, 'rows': 3}),)
	gender = forms.CharField(max_length=1, widget=forms.Select(choices=GENDER_OPT, attrs={'class': 'form-control'}),)

class SearchForm(forms.Form):
	search = forms.CharField(label='Search', max_length=30, min_length=3,
		widget=forms.TextInput(attrs={'class': 'form-control',}))