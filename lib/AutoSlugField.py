from django.db.models import CharField

from django.utils.encoding import force_unicode

from django.template.defaultfilters import slugify

def _get_field(instance, name):
    try:
        return getattr(instance, name)
    except AttributeError:
        raise ValueError("Model %s has no field '%s'" % \
                             (instance.__class__.__name__, name))

class AutoSlugField(CharField):
    """ A SlugField that automatically populate itself using the value of another
    field.

    In addition to CharField's usual parameters you can specify:

    populate_from (mandatory): the name of the field to be used for the slug
                               creation. ValueError will be raised at the
                               object save() time if the field does not exist.

    slugify_func: the function to apply on the value of the field.
                  If unspecified django.template.defaultfilters.slugify will be
                  used.

    append_field: the name of a field that will be appended to the slug, or
                  None. ValueError will be raised at the object save() time if
                  the field does not exist.

    prepend_field: the name of a field that will be prepended to the slug, or
                   None. ValueError will be raised at the object save() time if
                   the field does not exist.

    field_separator: the separator between the slug and the {pre, ap}pended
                     fields. The default value is u'-'.

    Unless explicitly set otherwise, the field will be created with the
    'editable' and 'db_index' parameters set respectively to False and
    True. """
    
    def __init__(self, *args, **kwargs):
        # Set editable=False if not explicitly set
        if 'editable' not in kwargs:
            kwargs['editable'] = False
            
        # Set db_index=True if not explicitly set
        if 'db_index' not in kwargs:
            kwargs['db_index'] = True

        populate_from = kwargs.pop('populate_from', None)
        slugify_func = kwargs.pop('slugify_func', slugify)
        append_field = kwargs.pop('append_field', None)
        prepend_field = kwargs.pop('prepend_field', None)
        field_separator = kwargs.pop('field_separator', u'-')
            
        if populate_from is None:
            raise ValueError("missing 'populate_from' argument")
        else:
            self._populate_from = populate_from
        
        self._slugify_func = slugify_func

        self._prepend_field = prepend_field
        self._append_field = append_field
        self._field_separator = field_separator

        super(AutoSlugField, self).__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):

        value = getattr(model_instance, self.attname)

        # only derive the slug if it does not already have a value
        if not value:
            populate_from = _get_field(model_instance, self._populate_from)

            make_slug = self._slugify_func

            chunks = list()

            if self._prepend_field is not None:
                prepend_field = _get_field(model_instance, self._prepend_field)
                # Prepend the field's value only if it is not empty
                if prepend_field:
                    chunks.append(force_unicode(prepend_field))

            chunks.append(make_slug(populate_from))

            if self._append_field is not None:
                append_field = _get_field(model_instance, self._append_field)
                # Append the field's value only if it is not empty
                if append_field:
                    chunks.append(force_unicode(append_field))

            value = self._field_separator.join(chunks)


        # make sure the slug is not too long
        if len(value) > self.max_length:
            value = value[:self.max_length]

        # make sure the record is unique
        unique_together = [lst for lst in model_instance._meta.unique_together if self.attname in lst]
        if self.unique or unique_together:
            
            filter_dict = None

            filter_dicts = []
            if self.unique:
                filter_dicts.append({})
            else: 
                # unique_together is a list of lists of fields that should be unique together
                for lst in unique_together:
                    filter_dict = {}
                    for name in lst:
                        if name != self.attname:
                            filter_dict[name] = getattr(model_instance, name)
                    filter_dicts.append(filter_dict)

            root = value
            def get_query():
                for filter_dict in filter_dicts:
                    query = model_instance.__class__.objects.filter(**{self.attname: value})
                    if filter_dict:
                        query = query.filter(**filter_dict)
                    if model_instance.pk:
                        query = query.exclude(pk=model_instance.pk)
                    if query.count() > 0:
                        return True
                return False

            counter = 1
            while get_query():
                value = make_slug("%s-%s" % (root, counter))
                # make sure the slug is not too long
                while len(value) > self.max_length:
                    root = root[:-1]
                    value = make_slug("%s-%s" % (root, counter))
                counter += 1

        setattr(model_instance, self.attname, value)

        return value

    def get_internal_type(self):
        return 'SlugField'

