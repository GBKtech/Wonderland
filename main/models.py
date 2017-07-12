from __future__ import unicode_literals

from django.db import models
from django.db.models import F
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse #Used to generate urls by reversing the URL patterns
from django.utils import timezone
from django.utils.text import slugify
from hitcount.models import HitCountMixin


# Create your models here.
class Section(models.Model):
	"""Representing the SECTION table"""
	name = models.CharField(max_length=255, unique=True)
	slug = models.SlugField(unique=True)

	def save(self, *args, **kwargs):
		self.slug = slugify(self.name)
		super(Section, self).save(*args, **kwargs)

	def __str__(self):
		return self.name

class Post(models.Model, HitCountMixin):
	""" Representing the POST table """
	title = models.CharField(max_length=255)
	post_by = models.ForeignKey('UserExtend')
	post_made = models.TextField(max_length=1000)
	section = models.ForeignKey(Section)
	post_likes = models.ManyToManyField(User, blank=True)
	post_pix = models.ManyToManyField('Attachment', blank=True)
	created = models.DateTimeField(blank=True, default=timezone.now)
	fp_created = models.DateTimeField(blank=True, null=True)
	comment_count = models.PositiveIntegerField(default=0)
	FRONTPAGE_STATUS = ( ('y', 'Yes'), ('n', 'No'), ('t', 'Trash'), )
	status = models.CharField(max_length=1, choices=FRONTPAGE_STATUS, blank=True, default='n',
    	help_text='Move To Frontpage?')
	TEXT_COLOR = ( ('yellow', 'yellow'), ('red', 'red'), ('blue', 'blue'), ('green', 'green'), ('purple', 'purple'), 
		('black', 'black'), )
	color = models.CharField(max_length=6, choices=TEXT_COLOR, blank=True, default='black',
    	help_text='Change Text Color')

	class Meta:
		permissions = (("can_move_to_fp", "Change frontpage status"),)

	@property
	def total_likes(self):
	    return self.post_likes.count()

	@property
	def increase(self):
		self.comment_count = F('comment_count') + 1
		self.save()

	def get_absolute_url(self):
		""" Returns the url to access a particular post. """
		return reverse('post-detail', args=[str(self.id), slugify(self.title[0:50])])

	def __str__(self):
		return '%s (%s)' % (self.title, self.comment_count)

class Comment(models.Model):
	"""Representing the COMMENT table"""
	comment_made = models.TextField(max_length=1000)
	comment_by = models.ForeignKey('UserExtend')
	post = models.ForeignKey('Post')
	comment_pix = models.ManyToManyField('Attachment', blank=True)
	this_comment_quote = models.ForeignKey('self', null=True, blank=True)
	comment_likes = models.ManyToManyField(User, blank=True)
	created = models.DateTimeField(blank=True, default=timezone.now, editable=False)
	TEXT_COLOR = ( ('yellow', 'yellow'), ('red', 'red'), ('blue', 'blue'), ('green', 'green'), ('purple', 'purple'), 
		('black', 'black'), )
	color = models.CharField(max_length=6, choices=TEXT_COLOR, blank=True, default='black',
    	help_text='Change Text Color')

	@property
	def total_likes(self):
	    return self.comment_likes.count()	

	@property
	def before_me(self):
		me = Comment.objects.filter(post=self.post).count() / 20
		me = me + 1
		return me

	def __str__(self):
		return '%s (%s)' % (self.comment_made,self.post.title)

# class Like(models.Model):
# 	"""Representing the LIKE table"""
# 	user = models.ForeignKey(User)
# 	post = models.ForeignKey(Post, null=True, blank=True)
# 	comment = models.ForeignKey(Comment, null=True, blank=True)


# 	def __str__(self):
# 		if self.comment:
# 			return '%s (%s)' % (self.user.username,self.comment.comment_made)
# 		else:
# 			return '%s (%s)' % (self.user.username,self.post.post_made)
		
# class Quote(models.Model):
# 	"""Representing the SECTION table"""
# 	quote_made = models.TextField(max_length=1000)
# 	quote_by = models.ForeignKey(User)
# 	quote_which_comment = models.ForeignKey(Comment)

# 	def __str__(self):
# 		return self.quote_made		


class Attachment(models.Model):
    file = models.FileField(upload_to='attachments')

class UserExtend(models.Model):
	"""Representing the SECTION table"""
	user = models.OneToOneField(User)
	# status = models.CharField(max_length=255, blank=True, null=True)
	GENDER_OPT = ( ('m', 'Male'), ('f', 'Female'), )
	gender = models.CharField(max_length=1, choices=GENDER_OPT, blank=True, null=True)
	brief_desc = models.CharField(verbose_name="Brief Description", max_length=255, blank=True, null=True)
	pin_post = models.ManyToManyField(Post, blank=True)
	profile_pix = models.ForeignKey('Attachment', blank=True, null=True)
	last_seen = models.DateTimeField(blank=True, null=True)

	def get_absolute_url(self):
		return reverse('userProfile', args=[str(self.user.username)])

	def __str__(self):
		if self.gender:
			return '%s (%s)' % (self.user.username,self.gender)
		else:
			return self.user.username
