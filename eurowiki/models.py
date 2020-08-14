import uuid
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import get_language, ugettext_lazy as _
import django_comments as comments
from rdflib_django.models import URIStatement, LiteralStatement
from .utils import node_id

try:
    from commons.models import Project
    euro_project = Project.objects.get(pk=settings.EURO_PROJECT_ID)
except:
    euro_project = None
    
def user_is_member(self, project=euro_project):
    return self.is_authenticated and ((project and project.is_member(self)) or (not project and self.is_full_member()))
User.is_euro_member = user_is_member


def literalstatement_item_code(self):
    s, p, o = self.as_triple()
    return node_id(s)
LiteralStatement.item_code = literalstatement_item_code

def literalstatement_is_country(self):
    return self.item_code() in settings.EU_COUNTRY_KEYS
LiteralStatement.item_code = literalstatement_item_code

def literalstatement_indexable_literal(self):
    s, p, o = self.as_triple()
    if o.datatype:
        return ''
    else:
        return o.value
LiteralStatement.indexable_literal = literalstatement_indexable_literal


class StatementExtension(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    uri_statement = models.OneToOneField(URIStatement, null=True, blank=True, on_delete=models.CASCADE, related_name='uri_statement')
    literal_statement = models.OneToOneField(LiteralStatement, null=True, blank=True, on_delete=models.CASCADE, related_name='literal_statement')
    deleted = models.BooleanField(default=False, verbose_name=_('deleted'))
    comment_enabled = models.BooleanField(
        _('comments enabled'), default=True,
        help_text=_('Allows comments if checked.'))

    def enable_comments(self):
        self.comment_enabled = True
        self.save()

    def disable_comments(self):
        self.comment_enabled = False
        self.save()

    @property
    def comments(self):
        return comments.get_model().objects.for_model(
            self).filter(is_public=True, is_removed=False).order_by('-pk')

    @property
    def comments_are_open(self):
        return self.comment_enabled

    def can_comment(self, request):
        user = request.user
        return user.is_authenticated
