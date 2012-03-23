from sortable import Sortable


def sortable_helper(request, objects, fields=None):
  """Helper used to make sortable slightly less verbose."""
  
  field_name = request.GET.get('sort', None)
  direction = request.GET.get('dir', 'asc')
  
  if not field_name:
    return objects
  
  sortable = Sortable(objects, fields)  
  return sortable.sorted(field_name, direction)