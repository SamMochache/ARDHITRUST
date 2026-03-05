# core/pagination.py
from rest_framework.pagination import CursorPagination

class StandardCursorPagination(CursorPagination):
    page_size = 12
    ordering = "-created_at"
    cursor_query_param = "cursor"