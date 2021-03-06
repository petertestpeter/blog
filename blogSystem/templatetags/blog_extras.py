# coding: utf-8

from django import template
from blogSystem.models import UserExtend, UserAttention
import logging

register = template.Library()
logger = logging.getLogger(__name__)


# django model func template parameter
@register.simple_tag
def get_post_related_num(func, params):
    return func.get_post_related_num(params)


# get user's portrait path
@register.filter
def get_user_portrait(user):
    try:
        obj = UserExtend.objects.get(pk=user.id)
        return '%s/%s/%s' % ('/static/images', obj.portrait.img_category.name, obj.portrait.src)
    except Exception, exc:
        logger.error(exc, exc_info=True)
        return '/static/images/other/anonymous.jpg'

# judge whether user has paid attention to some user
@register.filter
def judge_user_attention(user, uid):
    if UserAttention.objects.filter(guan_zhu=user.id, bei_guan_zhu=uid).exists():
        return 'yes'
    else:
        return 'no'