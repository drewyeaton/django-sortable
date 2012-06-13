from operator import itemgetter, attrgetter


class SortableInvalidObjectsException(Exception): pass


class Sortable(object):
  """docstring for Sortable"""
  
  def __init__(self, objects, fields):
    super(Sortable, self).__init__()
    self.objects = objects
    self.fields = None
    self.set_normalized_fields(fields)
  
  
  def set_normalized_fields(self, fields):
    """Takes name-to-field mapping tuple, normalizes it, and sets field."""
    if fields is None:
      return
    
    field_list = []
    for f in fields:
      if isinstance(f, basestring):
        field_list.append((f, (f,)))
      elif isinstance(f[1], basestring):
        field_list.append((f[0], (f[1],)))
      else:
        field_list.append(f)
    self.fields = dict(field_list)
  
    
  def sorted(self, field_name, direction='asc'):
    """Returns QuerySet with order_by applied or sorted list of dictionary."""
    
    if self.fields:
      try:
        fields = self.fields[field_name]
      except KeyError:
        return self.objects
    else:
      fields = (field_name,)
    
    if direction not in ('asc', 'desc'):
      return self.objects
    
    fields = Sortable.prepare_fields(fields, direction)
    
    if hasattr(self.objects, 'order_by'):
      result = self.objects.order_by(*fields)
    elif isinstance(self.objects, (list, tuple)):
      if len(self.objects) < 2:
        return self.objects
      
      comparers = []
      getter = itemgetter if isinstance(self.objects[0], dict) else attrgetter
      for f in fields:
        field = f[1:] if f.startswith('-') else f
        comparers.append((getter(field), 1 if field == f else -1))

      def comparer(left, right):
        for func, polarity in comparers:
          result = cmp(func(left), func(right))
          return 0 if not result else polarity * result
      
      result = sorted(self.objects, cmp=comparer)
    else:
      raise SortableInvalidObjectsException('An object of this type can not be sorted.')
    
    return result
  
  
  def sql_predicate(self, field_name, direction='asc', default=None):
    """Returns a predicate for use in a SQL ORDER BY clause."""
    
    if self.fields:
      try:
        fields = self.fields[field_name]
      except KeyError:
        fields = default
    else:
      fields = field_name
    
    if direction not in ('asc', 'desc'):
      fields = default
    
    fields = Sortable.prepare_fields(fields, direction, sql_predicate=True)
    return ', '.join(fields)


  @staticmethod
  def prepare_fields(fields, direction, sql_predicate=False):
    """Given a list or tuple of fields and direction, return a list of fields 
    with their appropriate order_by direction applied.

    >>> fields = ['++one', '--two', '+three', 'four', '-five']
    >>> Sortable.prepare_fields(fields, 'asc')
    ['one', '-two', 'three', 'four', '-five']
    >>> Sortable.prepare_fields(fields, 'desc')
    ['one', '-two', '-three', '-four', 'five']
    >>> Sortable.prepare_fields(fields, 'not_asc_or_desc')
    ['one', '-two', 'three', 'four', '-five']
    >>> Sortable.prepare_fields(fields, 'desc', True)
    ['one ASC', 'two DESC', 'three DESC', 'four DESC', 'five ASC']
    """
    
    if direction not in ('asc', 'desc'):
      direction = 'asc'  
    
    fields = list(fields)
    for i, field in enumerate(fields):
      if field.startswith('--'):
        fields[i] = field[1:]
      elif field.startswith('++'):
        fields[i] = field[2:]
      elif field.startswith('-'):
        fields[i] = (direction == 'asc' and '-' or '') + field[1:]
      else:
        field = field[1:] if field.startswith('+') else field
        fields[i] = (direction == 'desc' and '-' or '') + field
        
    if not sql_predicate:
      return fields
    
    # determine sql predicates from list
    fields = list(fields)
    for i, field in enumerate(fields):
      if field.startswith('-'):
        fields[i] = '%s DESC' % (field[1:],)
      else:
        fields[i] = '%s ASC' % (field,)
    return fields
