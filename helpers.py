from sortable import Sortable


def sortable_helper(request, objects, fields=None):
  """Helper used to make sortable slightly less verbose."""
  
  sortable = Sortable(objects, fields)
  field_name = request.GET.get('sort', '')
  direction = request.GET.get('dir', 'asc')
  
  return sortable.sorted(field_name, direction)