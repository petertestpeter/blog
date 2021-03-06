# coding: utf-8

from django.shortcuts import render_to_response, RequestContext, HttpResponse, get_object_or_404
from django.contrib.auth.decorators import login_required
from blogSystem.common.views import response_json
from service.commonKey import CATEGORY_DICT
from service.commonFunc import get_user_level, set_post_img_random
from django.db.models import F, Q
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404
from datetime import datetime
from service.decorator import is_authenticated, check_permission
from django.conf import settings
# from django.contrib.auth.decorators import permission_required

import models as blog_models
import json
import logging

logger = logging.getLogger(__name__)



# 首页展示
def index(req, tmp_name='index.html'):
    posts = blog_models.Post.objects.filter(is_valid=1).order_by('?')[0: 11]
    post_list = [
        {
            'img': "/static/images/%s/%s" % (post.img.img_category.name, post.img.src),
            'href': post.post_detail_path(),
            'title': post.title
        } for post in posts
    ]
    data = {
        'posts1': post_list[0: 4],
        'posts2': post_list[4: 7],
        'posts3': post_list[7: 11]
    }
    return render_to_response(tmp_name, data, context_instance=RequestContext(req))

# 帖子详情页面
def postDetail(req, category1=None, category2=None, post_id=None, tmp_name='postDetail.html'):
    breads = []
    if category1:
        breads.append({
            'location': CATEGORY_DICT.get(category1, category1),
            'href': '/category/%s' % category1
        })
    if category2:
        breads.append({
            'location': category2.upper(),
            'href': '/category/%s/%s' % (category1, category2)
        })
    if breads:
        breads.insert(0, {'location': u'首页', 'href': '/'})
    # 帖子阅读次数加1
    blog_models.Post.objects.filter(id=post_id).update(scan=F('scan') + 1)

    # 获取帖子对象
    postObj = get_object_or_404(blog_models.Post, pk=post_id)
    breads.append({
        'location': postObj.title
    })

    comments = blog_models.PostComment.objects.filter(post_id=post_id)

    dic = {
        'postObj': postObj,
        'breads': breads,
        'comments': comments
    }

    return render_to_response(tmp_name, dic, context_instance=RequestContext(req))

# 发帖页面
@login_required(login_url='/accounts/log_in')
@check_permission('blogSystem.add_post')
def makePost(req, tmp_name='makePost.html'):
    category = blog_models.Category.objects.filter(level=2).order_by('-parent_level', 'id')
    return render_to_response(tmp_name, {'category': category}, context_instance=RequestContext(req))

def user_post(req, uid, nickname, tmp_name='postList.html'):
    breads = [
        {'location': u'首页', 'href': '/'},
        {'location': nickname}
    ]
    limit = settings.PAGE_SIZE
    page = req.GET.get('page', 1)

    if not blog_models.UserExtend.objects.filter(user_id=uid, nickname=nickname).exists():
        raise Http404()

    posts = blog_models.Post.objects.filter(author__user__id=uid, is_valid=1).order_by('-id')

    paginator = Paginator(posts, limit)  # 实例化一个分页对象
    try:
        posts = paginator.page(page)  # 获取某页对应的记录
    except PageNotAnInteger:  # 如果页码不是个整数
        posts = paginator.page(1)  # 取第一页的记录
    except EmptyPage:  # 如果页码太大，没有相应的记录
        posts = paginator.page(paginator.num_pages)  # 取最后一页的记录

    dic = {
        'breads': breads,
        'posts': posts
    }
    return render_to_response(tmp_name, dic, context_instance=RequestContext(req))

def send_mail(req):
    import json
    # # from django.core.mail import EmailMessage
    # import smtplib
    # from email.mime.text import MIMEText
    # from email.header import Header
    # sender = 'from@runoob.com'
    # receivers = ['zhangzhiliang@cmcm.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
    #
    # # 三个参数：第一个为文本内容，第二个 plain 设置文本格式，第三个 utf-8 设置编码
    # message = MIMEText('Python 邮件发送测试...', 'plain', 'utf-8')
    # message['From'] = Header("菜鸟教程", 'utf-8')
    # message['To'] = Header("测试", 'utf-8')
    #
    # subject = 'Python SMTP 邮件测试'
    # message['Subject'] = Header(subject, 'utf-8')
    #
    # try:
    #     smtpObj = smtplib.SMTP()
    #     smtpObj.connect('smtp.gmail.com', 25)
    #     smtpObj.starttls()
    #     smtpObj.login('liveme_cms_finance@conew.com', 'wckckzuthxcgivop')
    #     for _ in range(5):
    #         status = smtpObj.sendmail(sender, receivers, message.as_string())
    #         print "邮件发送成功", status
    #     return HttpResponse(json.dumps({'msg': 'success'}), content_type='application/json')
    # except smtplib.SMTPException, exc:
    #     print exc
    #     print "Error: 无法发送邮件"
    #     return HttpResponse(json.dumps({'msg': 'error'}), content_type='application/json')
    from django.core.mail import EmailMessage
    try:
        # email = EmailMessage('test', 'this is a test mail', 'test@test.com', ['zhangzhiliang@cmcm.com'])
        # email.content_subtype = 'html'
        # email.attach('/Users/zhangzhiliang/zzl/mail.xls')
        # email.send()
        # return HttpResponse(json.dumps({'msg': 'success'}), content_type='application/json')

        html_content = "Comment tu vas?"
        email = EmailMessage("my subject", html_content, "paul@polo.com", ['zhangzhiliang@cmcm.com','823515849@qq.com'])
        email.content_subtype = "html"

        fd = open('/Users/zhangzhiliang/zzl/mail.xls', 'r')
        email.attach('mail.xls', fd.read(), 'text/plain')

        res = email.send()
        return HttpResponse(json.dumps({'msg': 'success', 'num': res}), content_type='application/json')
    except Exception, exc:
        return HttpResponse(json.dumps({'msg': 'error'}), content_type='application/json')

def postList(req, category1=None, category2=None, tmp_name='postList.html'):
    breads = []
    limit = settings.PAGE_SIZE
    page = req.GET.get('page', 1)
    if category1:
        breads.append({
            'location': CATEGORY_DICT.get(category1, category1),
            'href': '/category/%s'%category1
        })
    if category2:
        breads.append({
            'location': category2.upper()
        })
    if breads:
        breads.insert(0, {'location': u'首页', 'href': '/'})
    posts = []
    if category2:
        posts = blog_models.Post.objects.filter(category__name=category2, is_valid=1).order_by('-id')
    if category1 and not category2:
        c1Obj = get_object_or_404(blog_models.Category, name=category1)
        category2_list = blog_models.Category.objects.filter(parent_level=c1Obj.id).values_list('id')
        posts = blog_models.Post.objects.filter(category_id__in=category2_list, is_valid=1).order_by('-id')

    paginator = Paginator(posts, limit)  # 实例化一个分页对象
    try:
        posts = paginator.page(page)  # 获取某页对应的记录
    except PageNotAnInteger:  # 如果页码不是个整数
        posts = paginator.page(1)  # 取第一页的记录
    except EmptyPage:  # 如果页码太大，没有相应的记录
        posts = paginator.page(paginator.num_pages)  # 取最后一页的记录

    dic = {
        'breads': breads,
        'posts': posts
    }
    return render_to_response(tmp_name, dic, context_instance=RequestContext(req))

@is_authenticated
def makePostSummit(req):
    user = req.user
    content = req.POST.get('content')
    category = req.POST.get('category')
    title = req.POST.get('title')
    summary = req.POST.get('summary')
    if not all([content.strip(), category.strip(), title.strip(), summary.strip()]):
        json_str = {'status': 0, 'msg': u'标题、概要、内容为必填项！'}
        return response_json(json_str)
    try:
        blog_models.Post.objects.create(content=content,
                                        author_id=user.id,
                                        img_id=set_post_img_random(),
                                        category_id=category,
                                        title=title,
                                        summary=summary)
        json_str = {'status': 1, 'msg': u'提交成功'}
    except Exception, exc:
        logger.error(exc, exc_info=True)
        json_str = {'status': 0, 'msg': u'提交异常，请给作者留言，谢谢！'}
    return response_json(json_str)

def up_down_share_post(req):
    action_type = req.GET.get('type')
    post_id = req.GET.get('post_id')
    user_id = req.user.id
    if action_type in ('up', 'down'):
        if not req.user.is_authenticated():
            json_str = {'status': 0, 'msg': u'登录之后方可操作'}
            return response_json(json_str)
        if blog_models.ThumbUpDown.objects.filter(post_id=post_id, user_id=user_id, thumb_type=action_type).exists():
            json_str = {'status': 0, 'msg': u'不可重复操作'}
        else:
            blog_models.ThumbUpDown.objects.create(
                user_id=user_id,
                thumb_type=action_type,
                post_id=post_id
            )
            count = blog_models.ThumbUpDown.objects.filter(post_id=post_id, thumb_type=action_type).count()
            json_str = {'status': 1, 'count': count}
    elif action_type in ('weibo', 'qq', 'weixin', 'tencent', 'douban', 'qzone', 'linkedin', 'diandian', 'facebook', 'twitter', 'google'):
        blog_models.PostShare.objects.create(
            post_id=post_id,
            destination=action_type
        )
        count = blog_models.PostShare.objects.filter(post_id=post_id).count()
        json_str = {'status': 1, 'count': count}
    else:
        json_str = {'status': 0, 'msg': u'未知类型的操作'}
    return response_json(json_str)

@is_authenticated
def make_post_comment(req):
    post_id = req.POST.get('post_id')
    comment = req.POST.get('comment')
    user = req.user
    try:
        blog_models.PostComment.objects.create(
            comment=comment,
            post_id=post_id,
            poster_id=user.id
        )
        json_str = {'status': 1, 'msg': u'评论成功！'}
    except Exception, exc:
        logger.error(exc, exc_info=True)
        json_str = {'status': 0, 'msg': u'评论异常，请稍后重试！'}
    return response_json(json_str)

def get_top_three_post(req):
    page = req.GET.get('page', 1)
    posts = blog_models.Post.objects.all().order_by('?')[(int(page)-1)*9: int(page)*9]
    post_list = [
        {
            'img': "/static/images/%s/%s" % (post.img.img_category.name, post.img.src),
            'href': post.post_detail_path(),
            'summary': post.summary
        } for post in posts
    ]
    data = {'post_list': post_list}
    return response_json(data)

# @login_required
def leave_message(req, tmp_name='leaveWord.html'):
    count = blog_models.MessageLeave.objects.count()
    return render_to_response(tmp_name, {'count': count}, context_instance=RequestContext(req))

def get_more_message(req):
    page = req.GET.get('page', 1)
    is_login = 1 if req.user.is_authenticated() else 0

    limit = settings.PAGE_SIZE  # 每页显示的记录数
    msgs = blog_models.MessageLeave.objects.filter(level=1).order_by('-id')
    paginator = Paginator(msgs, limit)  # 实例化一个分页对象

    def _get_childrens(parentId):
        childrens = blog_models.MessageLeave.objects.filter(parent_id=parentId).order_by('-id')
        return [
            {
                'leaver_name': child.leaver.user.userextend.nickname,
                'leaver_portrait': "/static/images/%s/%s" % (child.leaver.portrait.img_category.name, child.leaver.portrait.src),
                'leave_msg': child.message,
                'leave_time': str(child.leave_time)[0:19],
            } for child in childrens
        ]

    try:
        msgObj = paginator.page(page)  # 获取某页对应的记录
    except PageNotAnInteger:  # 如果页码不是个整数
        msgObj = paginator.page(1)  # 取第一页的记录
    except EmptyPage:  # 如果页码太大，没有相应的记录
        # msgObj = paginator.page(paginator.num_pages)  # 取最后一页的记录
        msgObj = []
    msg_list = [
        {
            'leaver_name': msg.leaver.user.userextend.nickname,
            'leaver_portrait': "/static/images/%s/%s" % (msg.leaver.portrait.img_category.name, msg.leaver.portrait.src),
            'leave_msg': msg.message,
            'leave_time': str(msg.leave_time)[0:19],
            'id': msg.id,
            'childrens': _get_childrens(msg.id)
        } for msg in msgObj
    ]
    json_str = {
        'msg_list': msg_list,
        'next': 'yes' if msgObj.has_next() else 'no',
        'previous': 'yes' if msgObj and msgObj.has_previous() else 'no',
        'current_page': page,
        'is_login': is_login
    }
    return response_json(json_str)

# vue.js post时参数放在body中
@is_authenticated
@csrf_exempt
def make_leave_comment_submit(req):
    body = json.loads(req.body)
    user = req.user
    msg = body.get('msg', '')
    level = body.get('level', 1)
    parent_id = body.get('parent_id')
    try:
        if not msg.strip():
            json_str = {'status': 0, 'msg': u'留言不允许为空'}
            return response_json(json_str)
        # 保存留言
        blog_models.MessageLeave.objects.create(
                                            leaver_id=user.id,
                                            message=msg,
                                            level=level,
                                            parent_id=parent_id
                                        )
        msgObj = {
            'leaver_name': user.userextend.nickname,
            'leaver_portrait': "/static/images/%s/%s" % (user.userextend.portrait.img_category.name, user.userextend.portrait.src),
            'leave_msg': msg,
            'leave_time': str(datetime.now())[0:19]
        }
        msg = u'留言成功，博主会尽快给您答复！' if str(level) == '1' else u'回复成功！'
        json_str = {'status': 1, 'msg': msg, 'obj': msgObj}
    except Exception, exc:
        logger.error(exc, exc_info=True)
        json_str = {'status': 0, 'msg': u'留言异常，请稍后重试！'}
    return response_json(json_str)

def test(req, tmp_name='test2.html'):
    return render_to_response(tmp_name, context_instance=RequestContext(req))

@is_authenticated
def guan_zhu_poster(req):
    uid = req.GET.get('uid')
    user = req.user
    try:
        uid = int(uid)
        if blog_models.UserAttention.objects.filter(guan_zhu=user.id, bei_guan_zhu=uid).exists():
            blog_models.UserAttention.objects.filter(guan_zhu=user.id, bei_guan_zhu=uid).delete()
            json_str = {'status': 1, 'attention': 0, 'msg': u'取消关注'}
        else:
            blog_models.UserAttention.objects.create(
                guan_zhu=user.id,
                bei_guan_zhu=uid
            )
            json_str = {'status': 1, 'attention': 1, 'msg': u'关注成功'}
    except Exception, exc:
        logger.error(exc, exc_info=True)
        json_str = {'status': 0, 'msg': u'服务器异常，请稍后重试'}
    return response_json(json_str)

@is_authenticated
def get_user_list(req):
    page = req.GET.get('page', 1)
    limit = settings.PAGE_SIZE  # 每页显示的记录数
    users = blog_models.User.objects.all().exclude(id=req.user.id).order_by('id')
    paginator = Paginator(users, limit)  # 实例化一个分页对象

    try:
        userObj = paginator.page(page)  # 获取某页对应的记录
    except PageNotAnInteger:  # 如果页码不是个整数
        userObj = paginator.page(1)  # 取第一页的记录
    except EmptyPage:  # 如果页码太大，没有相应的记录
        userObj = []
    email_switch = lambda uid: blog_models.UserAttention.objects.get(guan_zhu=req.user.id, bei_guan_zhu=uid).email_notice or 0 \
                    if blog_models.UserAttention.objects.filter(guan_zhu=req.user.id, bei_guan_zhu=uid).exists() else 0
    user_list = [
        {
            'portrait': '/static/images/%s/%s'%(user.userextend.portrait.img_category.name, user.userextend.portrait.src),
            'nickname': user.userextend.nickname or u'暂无昵称',
            'date_joined': str(user.date_joined)[0: 10],
            'level': get_user_level(user.id),
            'fans': blog_models.UserAttention.objects.filter(bei_guan_zhu=user.id).count(),
            'posts': blog_models.Post.objects.filter(author_id=user.id).count(),
            'attention': 'yes' if blog_models.UserAttention.objects.filter(guan_zhu=req.user.id, bei_guan_zhu=user.id).exists() else 'no',
            'id': user.id,
            'email_notice': email_switch(user.id),
            'username': user.username
        } for user in userObj
    ]
    json_str = {
        'user_list': user_list,
        'next': int(page) + 1 if userObj and userObj.has_next() else 0,
        'current': page
    }
    return response_json(json_str)

@login_required
def email_notice_user(req):
    user = req.user
    uid = req.GET.get('uid')
    try:
        uid = int(uid)
        if blog_models.UserAttention.objects.filter(guan_zhu=user.id, bei_guan_zhu=uid).exists():
            if blog_models.UserAttention.objects.filter(guan_zhu=user.id, bei_guan_zhu=uid, email_notice=1).exists():
                blog_models.UserAttention.objects.filter(guan_zhu=user.id, bei_guan_zhu=uid).update(email_notice=0)
                json_str = {'status': 1, 'msg': u'您已成功关闭邮件通知'}
            else:
                blog_models.UserAttention.objects.filter(guan_zhu=user.id, bei_guan_zhu=uid).update(email_notice=1)
                json_str = {'status': 1, 'msg': u'该用户发帖时您将收到邮件通知'}
        else:
            json_str = {'status': 0, 'msg': u'请先关注该用户，然后执行此操作'}
    except Exception, exc:
        logger.error(exc, exc_info=True)
        json_str = {'status': 0, 'msg': u'服务器异常，请稍后重试'}
    return response_json(json_str)

@is_authenticated
def get_user_post(req):
    user = req.user
    page = req.GET.get('page', 1)

    limit = settings.PAGE_SIZE  # 每页显示的记录数
    posts = blog_models.Post.objects.filter(author__user__id=user.id, is_valid=1).order_by('-id')
    paginator = Paginator(posts, limit)  # 实例化一个分页对象

    try:
        postObj = paginator.page(page)  # 获取某页对应的记录
    except PageNotAnInteger:  # 如果页码不是个整数
        postObj = paginator.page(1)  # 取第一页的记录
    except EmptyPage:  # 如果页码太大，没有相应的记录
        postObj = []

    post_list = [
        {
            'time': str(post.post_time)[0: 19],
            'summary': '%s...' % post.summary[0:50] if len(post.summary) > 50 else post.summary,
            'post_detail_path': post.post_detail_path()
        } for post in postObj
    ]
    json_str = {
        'post_list': post_list,
        'next': 'yes' if postObj.has_next() else 'no',
        'previous': 'yes' if postObj and postObj.has_previous() else 'no',
        'current_page': page
    }
    return response_json(json_str)

def about_myself(req, tmp_name='myself.html'):
    return render_to_response(tmp_name, context_instance=RequestContext(req))

# 获取所有标签分类
def get_label_list(req):
    try:
        cats = blog_models.Category.objects.filter(level=2)
        labelList = [
            {
                'href': '/category/%s/%s' % (blog_models.Category.objects.get(id=cat.parent_level).name, cat.name),
                'name': cat.name
            } for cat in cats
        ]
        return response_json({'labelList': labelList})
    except Exception, exc:
        logger.error(exc, exc_info=True)
        return response_json({'labelList': []})