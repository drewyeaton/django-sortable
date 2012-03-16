#Django Sortable

The objective of django-sortable is to provide a flexible way to handle sorting within a complex Django application. 

Like pagination in Django, django-sortable works on a variety of data-types. When possible, an `order_by` clause will be added to a QuerySet. However, django-sortable can also handle lists of dictionaries or objects. Support is available for raw queries as well.


##Installation

1.  Add django-sortable to the `INSTALLED_APPS` setting in your project's settings.py file:

    	INSTALLED_APPS = (
    		# …
    		'django_sortable',
    	)

2.  Add the request context processor to the `TEMPLATE_CONTEXT_PROCESSORS` setting. If you don't have these defined in your settings.py file, you'll have to specify the default ones, and add the request processor at the end. (The current defaults are listed in the Django [context processor documentation](https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATE_CONTEXT_PROCESSORS).) This setting will look something like this:

		TEMPLATE_CONTEXT_PROCESSORS = (
		    'django.contrib.auth.context_processors.auth',
		    'django.core.context_processors.debug',
		    'django.core.context_processors.i18n',
		    'django.core.context_processors.media',
		    'django.core.context_processors.static',
		    'django.contrib.messages.context_processors.messages',
		    
		    # this is the additional requirement… 
		    'django.core.context_processors.request', 
		)


##Basic Usage

The most basic way to use django-sortable is to pass a QuerySet to the sortable helper, and add some simple template tags. Here's an example view and template:

__views.py__

	from django_sortable.helpers import sortable_helper
	
	def books(request):
	    book_list = Book.objects.all()
	    books = sortable_helper(request, book_list)
	    
	    # pagination code would go here, after sorting
		# …
	    
	    return render_to_response('books.html', {'books': books})

__books.html__

	{% load sortable %}
	
	<table>
		<tr>
			{% sortable_header title %}
			{% sortable_header published %}
		</tr>
		{% for book in books %}
		<tr>
			<td>{{ book.title }}</td>
			<td>{{ book.published }}</td>
		</tr>
		{% endfor %}
	</table>


##Advanced Usage

If you need more control over the behavior of django-sortable, you can use the Sortable class directly. Here's how you'd do it:

__views.py__

	from django_sortable.sortable import Sortable
	
	def authors(request):
		
		# we can pass in a list of dictionaries too!
		author_list = Author.objects.values()
		
		sortable = Sortable(author_list, (('author', 'full_name'), 'birth_date'))
		field_name = request.GET.get('sort', '')
		direction = request.GET.get('dir', 'asc')
		authors = sortable.sorted(field_name, direction)
		
		# pagination code would go here, after sorting
		# …
		
		return render_to_response('authors.html', {'authors': authors})

__authors.html__

	{% load sortable %}
	
	<table>
		<tr>
			<th>{% sortable_link author %}</th>
			<th>{% sortable_link birth_date "Birthday" %}</th>
		</tr>
		{% for author in authors %}
		<tr>
			<td>{{ author.full_name }}</td>
			<td>{{ author.birth_date }}</td>
		</tr>
		{% endfor %}
	</table>


##Raw SQL Usage

You can use django-sortable with raw queries by asking for just ordering columns. This way you can build the query yourself and append an ORDER BY clause. Here's an example:

__views.py__

	from django_sortable.sortable import Sortable
	
	def books(request):
		
		# all we need is an ordering column, don't pass an object list
		sortable = Sortable(None, (('book', 'b.title'),))
		field_name = request.GET.get('sort', '')
		direction = request.GET.get('dir', 'asc')
		
		# also, you can pass in a default ordering column(s)
		order_col = sortable.sql_column(
			field_name=field_name, 
			direction=direction, 
			default='m.title ASC, p.title ASC, t.condition DESC'
		)
	
		sql = '''
			SELECT      
				b.id AS id,
				b.title AS title,
				b.page_count AS num_pages,
				a.full_name AS author,
			FROM 
				book as b, 
				author as a
			WHERE 
				b.page_count > 100 AND
				b.status = %s AND
				b.author_id = a.id
			ORDER BY ''' + order_col
			
		cursor = connection.cursor()
		cursor.execute(sql, ['available',])
		books = dictfetchall(cursor)
		
		return render_to_response('books.html', {'books': books})


__books.html__

	{% load sortable %}
	
	<table>
		<tr>
			<th>{% sortable_link book "Book" %}</th>
			<th>Author</th>
		</tr>
		{% for book in books %}
		<tr>
			<td>{{ book.title }}</td>
			<td>{{ book.author }}</td>
		</tr>
		{% endfor %}
	</table>


##Additional Options

####Defining Ordering Fields

Sometimes the column you sort by is complex; especially if it spans relationships. You can specify sortable fields with custom order fields very easily. Imagine that we want to sort by author in our basic books example. We need to specify ordering fields for all the fields we want to order by, and add an additional string for a special ordering field:

	books = sortable_helper(
		request=request, 
		objects=book_list, 
		fields=('title', 'published', ('author', 'author__fullname'), 'page_count')
	)

Notice that we have a tuple for the fields argument, and one of the items in the tuple is another tuple. In this inner tuple, the first item is the __field name__ and the second is our special __ordering field__. When we sort on _author_, we're actually sorting on _author__fullname_.

Defining ordering fields has the secondary benefit of locking down which fields are sorted on.


####Rendering Links

If you want to specify a title in the header or link, you can place it in the `sortable_header` itself. Do it like this:
	
	{% sortable_header page_count "Number of Pages" %}
	
This tag generates a table header like this:

	<th class="sort-asc"><a href="/books/?sort=page_count&dir=asc" title="Number of Pages">Number of Pages</a></th>

You may want to do this to obscure your field names, but most commonly you probably just want to specify some easier-to-read text. If you don't want to use table headers, you can get plain links with the `sortable_link` tag like this:

	{% sortable_link page_count "Number of Pages" %}

This tag will generate a link with a class on the anchor instead of the table header:

	<a class="sort-asc" href="/books/?sort=page_count&dir=asc" title="Number of Pages">Number of Pages</a>


####Setting Custom Classes

Depending on the direction of the sort, a class will be placed on each header or link. The default classes are `sort-asc`, `sort-desc`, and `sort-none`. However, these are fully customizable using your project's settings. In your settings.py file, set these variables:

	SORT_ASC_CLASS = 'sort-asc'
	SORT_DESC_CLASS = 'sort-desc'
	SORT_NONE_CLASS = 'sort-none'

