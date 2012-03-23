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
    
    self.fields = dict([
      (f, f) if isinstance(f, basestring) else f 
      for f in fields
    ])
  
  
  def sorted(self, field_name, direction='asc'):
    """Returns QuerySet with order_by applied or sorted list of dictionary."""
    
    if self.fields:
      try:
        field = self.fields[field_name]
      except KeyError:
        return self.objects
    else:
      field = field_name
    
    if direction not in ('asc', 'desc'):
      return self.objects
    
    if hasattr(self.objects, 'order_by'):
      result = (self.objects
        .order_by((direction == 'desc' and '-' or '') + field)
      )
    elif isinstance(self.objects, (list, tuple)):
      if len(self.objects) < 2:
        return self.objects
      
      if isinstance(self.objects[0], dict):
        func = itemgetter(field)
      else:
        func = attrgetter(field)
      
      result = sorted(
        self.objects, 
        key=func,
        reverse=(direction == 'desc')
      )
    else:
      raise SortableInvalidObjectsException('An object of this type can not be sorted.')
    
    return result
  
  
  def sql_column(self, field_name, direction='asc', default=None):
    """Returns a column for use in a SQL ORDER BY clause."""
    
    if self.fields:
      try:
        field = self.fields[field_name]
      except KeyError:
        return default
    else:
      field = field_name
    
    if direction not in ('asc', 'desc'):
      return default
    
    return '%s %s' % (field, direction.upper())
