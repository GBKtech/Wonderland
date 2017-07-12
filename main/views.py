from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse

# Create your views here.
from .models import Post, Section, Comment, UserExtend, Attachment
from django.core.paginator import EmptyPage, PageNotAnInteger
from digg_paginator import DiggPaginator as Paginator
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.views import generic
from django.contrib.auth.decorators import login_required, permission_required 
from main.forms import CreateTopicForm, CreateCommentForm, SignupForm, EditProfileForm, SearchForm
from django.views.decorators.http import require_POST
from hitcount.models import HitCount
from hitcount.views import HitCountMixin
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .token import account_activation_token
from django.core.mail import EmailMessage
from django.utils import timezone
from django.db.models import Q
import datetime

try:
    from django.utils import simplejson as json
except ImportError:
    import json


def home(request):
    sections = Section.objects.all()
    post_num = Post.objects.count()
    user_num = User.objects.filter(is_active=True).count()
    user_extend = None

    if request.user.is_authenticated():
        user_extend = UserExtend.objects.get(user=request.user)

    query = Post.objects.filter(status__exact='y').order_by('-fp_created')
    page = request.GET.get('page', 1)

    paginator = Paginator(query, 20, body=5)

    try:
        post_list = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        post_list = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        post_list = paginator.page(paginator.num_pages)
    
    return render(request, 'main/post_list.html', {'post_list': post_list,'sections': sections, 
        'post_num': post_num, 'user_num': user_num, 'user_extend': user_extend, 'today':datetime.datetime.now(),},)

@login_required(login_url='/accounts/login/')
def myPinnedPost(request):
    sections = Section.objects.all()
    post_num = Post.objects.count()
    user_num = User.objects.filter(is_active=True).count()
    user_extend = None

    if request.user.is_authenticated():
        user_extend = UserExtend.objects.get(user=request.user)

    query = user_extend.pin_post.all()
    page = request.GET.get('page', 1)

    paginator = Paginator(query, 20, body=5)

    try:
        pin_post_list = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        pin_post_list = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        pin_post_list = paginator.page(paginator.num_pages)
    
    return render(request, 'main/myPinnedPost.html', {'pin_post_list': pin_post_list,'sections': sections, 
        'post_num': post_num, 'user_num': user_num, 'user_extend': user_extend, 'today':datetime.datetime.now(),},)

def latest(request):
    sections = Section.objects.all()
    post_num = Post.objects.count()
    user_num = User.objects.filter(is_active=True).count()
    user_extend = None

    if request.user.is_authenticated():
        user_extend = UserExtend.objects.get(user=request.user)

    query = Post.objects.exclude(status__exact='t').order_by('-id')
    page = request.GET.get('page', 1)

    paginator = Paginator(query, 20, body=5)

    try:
        latest = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        latest = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        latest = paginator.page(paginator.num_pages)
    
    return render(request, 'main/latest_list.html', {'latest': latest, 'sections': sections, 
        'post_num': post_num, 'user_num': user_num, 'user_extend': user_extend,},)

def trending(request):
    sections = Section.objects.all()
    post_num = Post.objects.count()
    user_num = User.objects.filter(is_active=True).count()
    user_extend = None

    if request.user.is_authenticated():
        user_extend = UserExtend.objects.get(user=request.user)

    query = Post.objects.exclude(status__exact='t').order_by('-comment_count')
    page = request.GET.get('page', 1)

    paginator = Paginator(query, 20, body=5)

    try:
        trending = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        trending = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        trending = paginator.page(paginator.num_pages)
    
    return render(request, 'main/trending_list.html', {'trending': trending, 'sections': sections, 
        'post_num': post_num, 'user_num': user_num, 'user_extend': user_extend,},)

# class page(generic.DetailView):
#     """
#     Generic class-based detail view for a post.
#     """
#     model = Post

#     def get_context_data(self, **kwargs):
#         # Call the base implementation first to get a context
#         context = super(page, self).get_context_data(**kwargs)
#         # Add in the publisher
#         context['sections'] = Section.objects.all()
#         context['post_num'] = Post.objects.count()
#         context['user_num'] = User.objects.count()
#         context['comments']
#         return context

def page(request, pk, topic):
    sections = Section.objects.all()
    post_num = Post.objects.count()
    user_num = User.objects.filter(is_active=True).count()

    try:
        post_query = Post.objects.get(pk=pk)
    except Post.DoesNotExist:
       return render(request, 'main/post_detail.html', {'sections': sections, 
            'post_num': post_num, 'user_num': user_num,},)

    if slugify(topic) != slugify(post_query.title[0:50]):
         return render(request, 'main/post_detail.html', {'sections': sections, 
            'post_num': post_num, 'user_num': user_num,},)

    if post_query:
        if request.user.is_authenticated():
            hit_count = HitCount.objects.get_for_object(post_query)
            hit_count_response = HitCountMixin.hit_count(request, hit_count)
            userextend_user = UserExtend.objects.get(user=request.user)
            userextend_user.last_seen = timezone.now()
            userextend_user.save(update_fields=['last_seen'])

        query = post_query.comment_set.all()
        page = request.GET.get('page', 1)

        paginator = Paginator(query, 20, body=5)

        try:
            comment = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
             comment = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            comment = paginator.page(paginator.num_pages)
        
        return render(request, 'main/post_detail.html', {'post': post_query, 'comment_list': comment,'sections': 
            sections, 'post_num': post_num, 'user_num': user_num,},)

from django.core.urlresolvers import reverse

def userProfile(request, slug):
    slug = slug.strip()
    # query = get_object_or_404(User, username=slug)
    sections = Section.objects.all()
    post_num = Post.objects.count()
    user_num = User.objects.filter(is_active=True).count()
    try:
        query = User.objects.get(username=slug)
    except User.DoesNotExist:
       return render(request, 'main/user_detail.html', context={'sections': sections, 
            'post_num': post_num, 'user_num': user_num,},)
    if query:
        user_extend = UserExtend.objects.get(user=query)
        return render(request, 'main/user_detail.html', context={'query': query,'sections': sections, 
            'post_num': post_num, 'user_num': user_num, 'user_extend': user_extend,},)
        

@require_POST
def post_like(request):
    if request.method == 'POST':
        user = request.user
        slug = request.POST.get('slug', None)
        pos = get_object_or_404(Post, id=slug)
        if pos.post_likes.filter(id=user.id).exists():
            pos.post_likes.remove(user)
            message = 'You disliked this post'
        else:
            pos.post_likes.add(user)
            message = 'You liked this post'
        ctx = {'likes_count': pos.total_likes, 'message': message}
        return HttpResponse(json.dumps(ctx), content_type='application/javascript')

@require_POST
def comment_like(request):
    if request.method == 'POST':
        user = request.user
        slug = request.POST.get('slug', None)
        com = get_object_or_404(Comment, id=slug)
        if com.comment_likes.filter(id=user.id).exists():
            com.comment_likes.remove(user)
            message = 'You disliked this comment'
        else:
            com.comment_likes.add(user)
            message = 'You liked this comment'
        if request.GET.has_key('post'):
            page_num = Comment.objects.filter(post=com.post.id).count() / 20
            page_num = page_num + 1
            url = "%s?page=%d#%d" % \
            (reverse('post-detail', args=(com.post.id, slugify(com.post.title),)), page_num, com.id)
            return HttpResponseRedirect( url )
        else:
            ctx = {'likes_count': com.total_likes, 'message': message}
            return HttpResponse(json.dumps(ctx), content_type='application/javascript')

@require_POST
def pin_post(request):
    if request.method == 'POST':
        user = request.user
        slug = request.POST.get('slug', None)
        pos = get_object_or_404(Post, id=slug)
        user_pin = get_object_or_404(UserExtend, user=user)
        if user_pin.pin_post.filter(id=pos.id).exists():
            user_pin.pin_post.remove(pos)
            message = 'You unstarred this post'
        else:
            user_pin.pin_post.add(pos)
            message = 'You starred this post'
        ctx = {'message': message}
        return HttpResponse(json.dumps(ctx), content_type='application/javascript')


# def like(request, action_type, action, post_id):
#     # Number of visits to this view, as counted in the session variable.
#     if action_type and action and post_id:
#         action = action.strip()
#         action_type = action_type.strip()
#         post_id = post_id.strip()
#         if action and action_type:
#             posty = Post.objects.get(id=post_id)
#             if action_type == 'commentAction':
#                 new_like, created = Like.objects.get_or_create(user=request.user, comment_id=action)
#             if action_type == 'postAction':
#                 new_like, created = Like.objects.get_or_create(user=request.user, post_id=post_id)
#             return HttpResponseRedirect(reverse('post-detail', args=(posty.id,posty.title.replace(' ','-'))))

def section(request, slug):
    slug = slug.strip()
    sections = Section.objects.all()
    post_num = Post.objects.count()
    user_num = User.objects.filter(is_active=True).count()
    user_extend = None

    try:
        sec_query = Section.objects.get(name=slug)
    except Section.DoesNotExist:
       return render(request, 'main/section_list.html', {'sections': sections, 
            'post_num': post_num, 'user_num': user_num, 'err':'error',},)

    if request.user.is_authenticated():
        user_extend = UserExtend.objects.get(user=request.user)

    if sec_query:

        query = sec_query.post_set.exclude(status__exact='t')
        page = request.GET.get('page', 1)

        paginator = Paginator(query, 20, body=5)

        try:
            section = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
             section = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            section = paginator.page(paginator.num_pages)
        
        return render(request, 'main/section_list.html', {'section_name': sec_query, 'section_list': section,'sections': sections, 
            'post_num': post_num, 'user_num': user_num, 'user_extend': user_extend,},)

def popular(request, slug):
    slug = slug.strip()
    sections = Section.objects.all()
    post_num = Post.objects.count()
    user_num = User.objects.filter(is_active=True).count()
    user_extend = None

    try:
        sec_query = Section.objects.get(name=slug)
    except Section.DoesNotExist:
       return render(request, 'main/popular_section.html', {'sections': sections, 
            'post_num': post_num, 'user_num': user_num, 'err':'error'},)

    if request.user.is_authenticated():
        user_extend = UserExtend.objects.get(user=request.user)

    if sec_query:

        query = sec_query.post_set.exclude(status__exact='t').order_by('-comment_count')
        page = request.GET.get('page', 1)

        paginator = Paginator(query, 20, body=5)

        try:
            section = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
             section = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            section = paginator.page(paginator.num_pages)
        
        return render(request, 'main/popular_section.html', {'section_name': sec_query, 'section_list': section,
            'sections': sections, 'post_num': post_num, 'user_num': user_num, 'user_extend': user_extend,},)
        

  #   def get_context_data(self, **kwargs):
  #       # Call the base implementation first to get a context
  #       context = super(section, self).get_context_data(**kwargs)
  #       # Add in the publisher
  #       context['sections'] = Section.objects.all()
  #       context['post_num'] = Post.objects.count()
  #       context['user_num'] = User.objects.count()
  #       return context

  # #   def get_queryset(self):
		# # #self.section = get_object_or_404(Section, name=self.kwargs['slug'])
		# # return Section.objects.filter(name=self.kwargs['slug']).order_by('-name')


# ############################################################################
# Creating ....
#############################################################################

@login_required(login_url='/accounts/login/')
def createTopic(request, section):
    section = section.strip()
    sections = Section.objects.all()
    post_num = Post.objects.count()
    user_num = User.objects.filter(is_active=True).count()

    try:
        sec_query = Section.objects.get(name = section)
    except Section.DoesNotExist:
        return render(request, 'main/createTopic.html', {'sections': sections, 
                'post_num': post_num, 'user_num': user_num,},)
   
    if request.method == "POST":
        form = CreateTopicForm(request.POST, request.FILES)
        if form.is_valid():
            post = Post.objects.create(
            title=form.cleaned_data['subject'],
            color=form.cleaned_data['color'],
            post_by= UserExtend.objects.get(user=request.user),
            post_made=form.cleaned_data['message'],
            section = sec_query,
            )
            for each in form.cleaned_data['attachments']:
                att = Attachment.objects.create(file=each)
                post.post_pix.add(att.pk)
            return HttpResponseRedirect(reverse('section', args=(sec_query,)))
    else:
        form = CreateTopicForm()

    return render(request, 'main/createTopic.html', {'section_name': sec_query, 'sections': sections, 
                'post_num': post_num, 'user_num': user_num, 'form':form,},)

@login_required(login_url='/accounts/login/')
def createComment(request, pk, topic):
    sections = Section.objects.all()
    post_num = Post.objects.count()
    user_num = User.objects.filter(is_active=True).count()

    try:
        pos_query = Post.objects.get(pk = pk)
    except Post.DoesNotExist:
        return render(request, 'main/createComment.html', {'sections': sections, 
                'post_num': post_num, 'user_num': user_num,},)

    if slugify(topic) != slugify(pos_query.title[0:50]):
         return render(request, 'main/createComment.html', {'sections': sections, 
            'post_num': post_num, 'user_num': user_num,},)
   
    if request.method == "POST":
        form = CreateCommentForm(request.POST, request.FILES)
        if form.is_valid():
            comment = Comment.objects.create(
            comment_made=form.cleaned_data['comment'],
            color=form.cleaned_data['color'],
            comment_by= UserExtend.objects.get(user=request.user),
            post=pos_query,
            )
            for each in form.cleaned_data['attachments']:
                att = Attachment.objects.create(file=each)
                comment.comment_pix.add(att.pk)
            pos_query.increase
            page_num = Comment.objects.filter(post=pos_query).count() / 20
            page_num = page_num + 1
            url = "%s?page=%d#%d" % \
            (reverse('post-detail', args=(pos_query.id, slugify(pos_query.title),)),page_num,comment.id)
            return HttpResponseRedirect( url )
    else:
        form = CreateCommentForm()

    return render(request, 'main/createComment.html', {'post_id': pos_query, 'sections': sections, 
                'post_num': post_num, 'user_num': user_num,'form':form,},)

@login_required(login_url='/accounts/login/')
def quoteComment(request, pk):
    sections = Section.objects.all()
    post_num = Post.objects.count()
    user_num = User.objects.filter(is_active=True).count()

    try:
        com_query = Comment.objects.get(pk = pk)
    except Comment.DoesNotExist:
        return render(request, 'main/quoteComment.html', {'sections': sections, 
                'post_num': post_num, 'user_num': user_num,},)
   
    if request.method == "POST":
        form = CreateCommentForm(request.POST, request.FILES)
        if form.is_valid():
            comment = Comment.objects.create(
            comment_made=form.cleaned_data['comment'],
            this_comment_quote= com_query,
            color=form.cleaned_data['color'],
            comment_by= UserExtend.objects.get(user=request.user),
            post=com_query.post,
            )
            for each in form.cleaned_data['attachments']:
                att = Attachment.objects.create(file=each)
                comment.comment_pix.add(att.pk)
            com_query.post.increase
            page_num = Comment.objects.filter(post=com_query.post.id).count() / 20
            page_num = page_num + 1
            url = "%s?page=%d#%d" % \
            (reverse('post-detail', args=(com_query.post.id, slugify(com_query.post.title),)), page_num ,comment.id)
            return HttpResponseRedirect( url )
    else:
        form = CreateCommentForm()

    return render(request, 'main/quoteComment.html', {'comment_id': com_query, 'sections': sections, 
                'post_num': post_num, 'user_num': user_num,'form':form, 
                'comment_to_be_quoted': com_query.comment_made,},)


from django.contrib.auth.views import logout, login
from django.contrib.auth import authenticate

def custom_login(request):
    sections = Section.objects.all()
    post_num = Post.objects.count()
    user_num = User.objects.filter(is_active=True).count()
    if request.user.is_authenticated():
        return HttpResponseRedirect('/')
    else:
        username = password = ''
        if request.method == "POST":
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    if request.POST['next']:
                        return HttpResponseRedirect(request.POST['next'])
                    return HttpResponseRedirect('/')
                else:
                   return render(request, 'main/login.html', {'error': 'You are currently not allowed to login',
                    'sections': sections, 'post_num': post_num, 'user_num': user_num, 'next': request.POST.get('next')}) 
            return render(request, 'main/login.html', {'error': 'Username and Password Does Not Match',
                'sections': sections, 'post_num': post_num, 'user_num': user_num, 'next': request.POST.get('next')})
        if request.GET.has_key('next'):
            return render(request, 'main/login.html', {'sections': sections, 'post_num': post_num, 'user_num': user_num,
            'next': request.GET.get('next')},)
        else:
            return render(request, 'main/login.html', {'sections': sections, 'post_num': post_num, 'user_num': user_num,
            'next': '/'},)

def logout_page(request):
    logout(request)
    if request.GET.has_key('next'):
        return HttpResponseRedirect(request.GET.get('next'))
    else:
        return HttpResponseRedirect('/')

def signup(request):
    sections = Section.objects.all()
    post_num = Post.objects.count()
    user_num = User.objects.filter(is_active=True).count()
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            subject = 'Activate your blog account.'
            message = render_to_string('main/acc_active_email.html', {
                'user':user, 'domain':current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            # user.email_user(subject, message)
            toemail = form.cleaned_data.get('email')
            email = EmailMessage(subject, message, to=[toemail])
            email.send()
            return render(request, 'main/signup.html', {'sections': sections, 
        'post_num': post_num, 'user_num': user_num, 
        'msg':'Please confirm your email address to complete the registration'})
    else:
        form = SignupForm()
    return render(request, 'main/signup.html', {'form': form, 'sections': sections, 
        'post_num': post_num, 'user_num': user_num,})

def activate(request, uidb64, token):
    sections = Section.objects.all()
    post_num = Post.objects.count()
    user_num = User.objects.filter(is_active=True).count()

    if request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        obj, created = UserExtend.objects.get_or_create(user=user)
        # login(request, user)
        return render(request, 'main/activated.html', {'sections': sections, 
        'post_num': post_num, 'user_num': user_num, 
        'msg':'Thank you for your email confirmation. Now you can login your account.'})
    else:
        return render(request, 'main/activated.html', {'sections': sections, 
        'post_num': post_num, 'user_num': user_num, 'errmsg':'Activation link is invalid!'})


@login_required(login_url='/accounts/login/')
def EditProfile(request, slug):
    slug = slug.strip()
    # query = get_object_or_404(User, username=slug)
    sections = Section.objects.all()
    post_num = Post.objects.count()
    user_num = User.objects.filter(is_active=True).count()
    try:
        query = User.objects.get(username=slug)
    except User.DoesNotExist:
       return render(request, 'main/user_update_form.html', {'sections': sections, 
                'post_num': post_num, 'user_num': user_num,},)
    
    userextend = UserExtend.objects.get(user=query)
    data = {'gender': userextend.gender, 'brief_desc': userextend.brief_desc}
    if request.method == "POST":
        form = EditProfileForm(request.POST, request.FILES)
        if form.is_valid():
            userextend.gender = form.cleaned_data['gender']
            userextend.brief_desc = form.cleaned_data['brief_desc']
            attach_data = form.cleaned_data['attach']
            att = Attachment.objects.create(file=attach_data)
            userextend.profile_pix = att
            userextend.save()
            return HttpResponseRedirect( reverse('userProfile', args=(query.username,)))
    else:
        form = EditProfileForm(initial=data)
        
    return render(request, 'main/user_update_form.html', {'sections': sections, 
                'post_num': post_num, 'user_num': user_num,'form':form,},)


@login_required(login_url='/accounts/login/')
def CommentUpdate(request, pk):
    # query = get_object_or_404(User, username=slug)
    sections = Section.objects.all()
    post_num = Post.objects.count()
    user_num = User.objects.filter(is_active=True).count()

    try:
        query = Comment.objects.get(id=pk)
    except Comment.DoesNotExist:
       return render(request, 'main/comment_update_form.html', {'sections': sections, 
                'post_num': post_num, 'user_num': user_num,'err':'error',},)

    if request.user != query.comment_by.user:
         return render(request, 'main/comment_update_form.html', {'sections': sections, 
            'post_num': post_num, 'user_num': user_num,'err':'error'},)

    data = {'comment': query.comment_made, 'color': query.color}
    if request.method == "POST":
        form = CreateCommentForm(request.POST, request.FILES)
        if form.is_valid():
            query.comment_made = form.cleaned_data['comment']
            query.color = form.cleaned_data['color']
            for each in form.cleaned_data['attachments']:
                att = Attachment.objects.create(file=each)
                query.comment_pix.add(att.pk)
            query.save()
            page_num = Comment.objects.filter(id__lte=query.id).count() / 20
            page_num = page_num + 1
            url = "%s?page=%d#%d" % \
            (reverse('post-detail', args=(query.post.id, slugify(query.post.title),)),page_num,query.id)
            return HttpResponseRedirect( url )
    else:
        form = CreateCommentForm(initial=data)
        
    return render(request, 'main/comment_update_form.html', {'sections': sections, 
                'post_num': post_num, 'user_num': user_num,'form':form,},)

@login_required(login_url='/accounts/login/')
def PostUpdate(request, pk):
    # query = get_object_or_404(User, username=slug)
    sections = Section.objects.all()
    post_num = Post.objects.count()
    user_num = User.objects.filter(is_active=True).count()

    try:
        query = Post.objects.get(id=pk)
    except Post.DoesNotExist:
       return render(request, 'main/post_update_form.html', {'sections': sections, 
                'post_num': post_num, 'user_num': user_num,'err':'error',},)

    if request.user != query.post_by.user:
         return render(request, 'main/post_update_form.html', {'sections': sections, 
            'post_num': post_num, 'user_num': user_num,'err':'error'},)

    data = {'subject': query.title, 'message': query.post_made, 'color': query.color,}
    if request.method == "POST":
        form = CreateTopicForm(request.POST, request.FILES)
        if form.is_valid():
            query.post_made = form.cleaned_data['message']
            query.title = form.cleaned_data['subject']
            query.color = form.cleaned_data['color']
            for each in form.cleaned_data['attachments']:
                att = Attachment.objects.create(file=each)
                query.post_pix.add(att.pk)
            query.save()
            url = reverse('post-detail', args=(query.id, slugify(query.title)))
            return HttpResponseRedirect( url )
    else:
        form = CreateTopicForm(initial=data)
        
    return render(request, 'main/post_update_form.html', {'sections': sections, 
                'post_num': post_num, 'user_num': user_num,'form':form,},)

@require_POST
@permission_required('main.can_move_to_fp')
def change_fp_mode(request):
    if request.method == 'POST':
        postid = request.POST.get('pk', None)
        fpmode = request.POST.get('mode', None)
        pos = get_object_or_404(Post, id=postid)
        message = 'Already in this mode'

        if fpmode == 'y' and pos.status != 'y':
            pos.status = fpmode
            pos.fp_created = timezone.now()
            message = 'Post moved to FP'
        elif fpmode == 'n' and pos.status != 'n':
            pos.status = fpmode
            pos.fp_created = None
            message = 'Post removed from FP'
        elif fpmode == 't' and pos.status != 't':
            pos.status = fpmode
            pos.fp_created = None
            message = 'Post moved to Bin'
        pos.save()
        ctx = {'message': message}
        return HttpResponse(json.dumps(ctx), content_type='application/javascript')

@permission_required('main.can_move_to_fp')
def moderator(request, slug):
   pass

def allMyPost(request, slug):
    slug = slug.strip()
    sections = Section.objects.all()
    post_num = Post.objects.count()
    user_num = User.objects.filter(is_active=True).count()
    user_extend = None

    try:
        queryu = User.objects.get(username=slug)
    except User.DoesNotExist:
       return render(request, 'main/allmypost.html', context={'sections': sections, 
            'post_num': post_num, 'user_num': user_num,},)

    if request.user.is_authenticated():
        user_extend = UserExtend.objects.get(user=request.user)

    query = Post.objects.exclude(status__exact='t').filter(post_by__user=queryu).order_by('-id')
    page = request.GET.get('page', 1)

    paginator = Paginator(query, 20, body=5)

    try:
        allpost = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        allpost = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        allpost = paginator.page(paginator.num_pages)
    
    return render(request, 'main/allmypost.html', {'allpost': allpost, 'sections': sections, 
        'post_num': post_num, 'user_num': user_num, 'user_extend': user_extend, 'post_owner':queryu,},)

def allMyComment(request, slug):
    slug = slug.strip()
    sections = Section.objects.all()
    post_num = Post.objects.count()
    user_num = User.objects.filter(is_active=True).count()
    user_extend = None

    try:
        queryu = User.objects.get(username=slug)
    except User.DoesNotExist:
       return render(request, 'main/allmycomment.html', context={'sections': sections, 
            'post_num': post_num, 'user_num': user_num,},)

    if request.user.is_authenticated():
        user_extend = UserExtend.objects.get(user=request.user)

    query = Comment.objects.exclude(post__status='t').filter(comment_by__user=queryu).order_by('-id')
    page = request.GET.get('page', 1)

    paginator = Paginator(query, 20, body=5)

    try:
        allcomment = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        allcomment = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        allcomment = paginator.page(paginator.num_pages)
    
    return render(request, 'main/allmycomment.html', {'allcomment': allcomment, 'sections': sections, 
        'post_num': post_num, 'user_num': user_num, 'user_extend': user_extend, 'post_owner':queryu,},)


def MyMention(request):
    sections = Section.objects.all()
    post_num = Post.objects.count()
    user_num = User.objects.filter(is_active=True).count()
    user_extend = None
    
    if request.GET.has_key('search'):
        form = SearchForm(request.GET)
    else:
        return render(request, 'main/my_mention.html', {'sections': sections, 
            'post_num': post_num, 'user_num': user_num, 'err':'error'},)

    if form.is_valid():
        user_extend = form.cleaned_data['search']
        query = Comment.objects.exclude(post__status='t').filter( \
            Q(this_comment_quote__comment_by__user__username__iexact=user_extend) | \
            Q(comment_made__icontains=user_extend) ).order_by('-id')
        page = request.GET.get('page', 1)

        paginator = Paginator(query, 20, body=5)

        try:
            allcomment = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            allcomment = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            allcomment = paginator.page(paginator.num_pages)
    
        return render(request, 'main/my_mention.html', {'allcomment': allcomment, 'sections': sections, 
            'post_num': post_num, 'user_num': user_num, 'post_owner':user_extend,},)
    else:
        return render(request, 'main/my_mention.html', {'sections': sections, 
            'post_num': post_num, 'user_num': user_num,},)