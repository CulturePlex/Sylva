import re
from django.db.models import fields
from django.template.defaultfilters import slugify


def _unique_slugify(instance, value, slug_field_name='slug', queryset=None,
                    slug_separator='-'):
    """
    Calculates a unique slug of ``value`` for an instance.

    :param slug_field_name: Should be a string matching the name of the field to
        store the slug in (and the field to check against for uniqueness).

    :param queryset: usually doesn't need to be explicitly provided - it'll
        default to using the ``.all()`` queryset from the model's default
        manager.

    """
    slug_field = instance._meta.get_field(slug_field_name)

    slug_len = slug_field.max_length

    # Sort out the initial slug. Chop its length down if we need to.
    slug = slugify(value)
    if slug_len:
        slug = slug[:slug_len]
    slug = _slug_strip(slug, slug_separator)
    original_slug = slug

    # Create a queryset, excluding the current instance.
    if queryset is None:
        queryset = instance.__class__._default_manager.all()
        if instance.pk:
            queryset = queryset.exclude(pk=instance.pk)

    # Find a unique slug. If one matches, at '-2' to the end and try again
    # (then '-3', etc).
    next = 2
    while not slug or queryset.filter(**{slug_field_name: slug}):
        slug = original_slug
        end = '-%s' % next
        if slug_len and len(slug) + len(end) > slug_len:
            slug = slug[:slug_len - len(end)]
            slug = _slug_strip(slug, slug_separator)
        slug = '%s%s' % (slug, end)
        next += 1

    setattr(instance, slug_field.attname, slug)
    return slug


def _slug_strip(value, separator=None):
    """
    Cleans up a slug by removing slug separator characters that occur at the
    beginning or end of a slug.

    If an alternate separator is used, it will also replace any instances of the
    default '-' separator with the new separator.

    """
    if separator == '-' or not separator:
        re_sep = '-'
    else:
        re_sep = '(?:-|%s)' % re.escape(separator)
        value = re.sub('%s+' % re_sep, separator, value)
    return re.sub(r'^%s+|%s+$' % (re_sep, re_sep), '', value)


class AutoSlugField(fields.SlugField):
    """Auto slug field, creates unique slug for model."""

    def __init__(self, populate_from, *args, **kwargs):
        """Create auto slug field.

        If field is unique, the uniqueness of the slug is ensured from existing
        slugs by adding extra number at the end of slug.

        If field has slug given, it is used instead. If you want to re-generate
        the slug, just set it :const:`None` or :const:`""` so it will be re-
        generated automatically.

        :param populate_from: Must be assigned to list of field names which
            are used to prepopulate automatically.

        :type populate_from: sequence
        """
        self.populate_separator = kwargs.get("populate_separator", u"-")
        self.populate_from = populate_from
        kwargs["blank"] = True
        super(fields.SlugField, self).__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):  # @UnusedVariable
        """Pre-save event"""
        current_slug = getattr(model_instance, self.attname)

        # Use current slug instead, if it is given.
        # Assumption: There are no empty slugs.
        if not (current_slug is None or current_slug == ""):
            slug = current_slug
        else:
            slug = self.populate_separator.\
                        join(unicode(getattr(model_instance, prepop))
                             for prepop in self.populate_from)

        if self.unique:
            return _unique_slugify(model_instance, value=slug,
                                   slug_field_name=self.attname)
        else:
            return slugify(slug)[:self.max_length]
