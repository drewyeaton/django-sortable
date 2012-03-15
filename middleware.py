def get_field(self):
  try:
    field_name = self.REQUEST['sort']
  except (KeyError, ValueError, TypeError):
    field_name = ''
  return field_name


def get_direction(self):
  try:
    direction = self.REQUEST['dir']
  except (KeyError, ValueError, TypeError):
    direction = 'asc'
  return direction


class SortableMiddleware(object):
  def process_request(self, request):
    request.__class__.sort_field = property(get_field)
    request.__class__.sort_direction = property(get_direction)