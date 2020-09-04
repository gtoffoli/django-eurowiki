import uuid
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField, AutoSlugField
import django_comments as comments
from rdflib_django.models import URIStatement, LiteralStatement
from commons.models import Publishable, PUBLICATION_STATE_CHOICES, DRAFT
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
    """
    if o.datatype:
        return ''
    else:
    """
    for p_key in settings.INDEXABLE_PREDICATES:
        if p.count(p_key):
            return o.value
    return ''
LiteralStatement.indexable_literal = literalstatement_indexable_literal


class StatementExtension(models.Model):
    """
    this class, like the commons.Resource class, links the rdflib-django3 models to other ones;
    currently the fields 'deleted' and 'comment_enabled' aren't used
    """
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

class SparqlQuery(models.Model, Publishable):
    title = models.CharField(max_length=200, db_index=True, verbose_name=_('title'))
    description = models.TextField(blank=True, null=True, verbose_name=_('description'))
    text = models.TextField(blank=True, null=True, verbose_name=_('query text'))
    state = models.IntegerField(choices=PUBLICATION_STATE_CHOICES, default=DRAFT, null=True, verbose_name='publication state')

    modified = ModificationDateTimeField(_('last modified'))
    editor = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name=_('last editor'), related_name='query_editor')

    class Meta:
        verbose_name = _('SPARQL query definition')
        verbose_name_plural = _('SPARQL query definitions')

    def __str__(self):
        return self.title

    def can_edit(self, request):
        user = request.user
        return user.is_authenticated and user.is_euro_member()

    def can_delete(self, request):
        user = request.user
        return user.is_superuser or (user.is_authenticated and user.is_euro_member() and self.editor==user)

class QueryRun(models.Model):
    query = models.ForeignKey(SparqlQuery, on_delete=models.CASCADE, related_name='query', verbose_name=_('query'))
    result = models.TextField(blank=True, null=True, verbose_name=_('query result'))

    executed = CreationDateTimeField(_('execution time'))
    executor = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('executor'), related_name='executor')

    class Meta:
        verbose_name = _('SPARQL query execution')
        verbose_name_plural = _('SPARQL query executions')
 
    def __str__(self):
        return 'run of query {} at {}'.format(self.query.title, self.executed)

