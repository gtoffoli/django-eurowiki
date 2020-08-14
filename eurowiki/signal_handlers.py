# -*- coding: utf-8 -*-"""

from django_comments.models import Comment
from django_comments.signals import comment_will_be_posted
from eurowiky.views import statement_extension

def comment_will_be_posted_handler(sender, **kwargs):
    if statement_extension._state.adding:
        statement_extension.save()

comment_will_be_posted.connect(comment_will_be_posted_handler, sender=Comment)
