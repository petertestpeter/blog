# coding: utf-8

import blogSystem.models as blog_models
from django.shortcuts import render_to_response, RequestContext
import json
from django.db.models import Q
import time
from itertools import chain
import jieba
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger




def search(req, tmp_name='postList.html'):
    page = req.GET.get('page', 1)
    limit = 2
    start = time.time()
    query = req.GET.get('q', '')
    qs = jieba.cut(query)
    qs = [q for q in list(qs) if q.strip()]


    breads = [
        {'location': u'首页', 'href': '/'},
        {'location': u'搜索：%s'%query}
    ]
    s_list = []
    for q in qs:
        post = blog_models.Post.objects.filter(Q(title__icontains=q) | Q(summary__icontains=q) | Q(content__icontains=q))
        s_list.append(post)
    posts = chain.from_iterable(s_list)
    posts = list(posts)

    paginator = Paginator(posts, limit)  # 实例化一个分页对象
    try:
        post = paginator.page(page)  # 获取某页对应的记录
    except PageNotAnInteger:  # 如果页码不是个整数
        post = paginator.page(1)  # 取第一页的记录
    except EmptyPage:  # 如果页码太大，没有相应的记录
        post = paginator.page(paginator.num_pages)  # 取最后一页的记录

    end = time.time()
    dic = {
        'breads': breads,
        'posts': post,
        'q': query,
        'time': str(round((end - start), 3)) + 's',
        'count': len(posts),
        'show': 'yes' if int(page) == 1 else 'no'
    }
    return render_to_response(tmp_name, dic, context_instance=RequestContext(req))