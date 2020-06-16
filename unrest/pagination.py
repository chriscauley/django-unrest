import functools

noop = lambda i: i

def paginate(items, per_page=20, process=noop, **kwargs):
    page = int(kwargs.get('page', 1))
    offset = (page - 1) * per_page
    total = len(items)
    return {
        'items': [process(i) for i in items[offset: offset + per_page]],
        'page': page,
        'total': len(items),
        'next_page': page + 1 if offset + per_page > total else None,
        'prev_page': page - 1 if page > 0 else None,
    }
