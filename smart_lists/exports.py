from abc import (
    ABCMeta,
    abstractmethod,
)
from typing import TYPE_CHECKING

import six
from openpyxl import Workbook

from django.db.models import Q

from smart_lists.helpers import SmartListItem

if TYPE_CHECKING:
    from typing import Any, Callable, Iterable, Optional
    from smart_lists.helpers import SmartList


class SmartListExportBackend(six.with_metaclass(ABCMeta)):
    def __init__(
        self,
        verbose_name,
        file_name,
        extra_filters=None,
        limit=None,
    ):  # type: (str, str, Union[Q, Callable[[], Q], None], Optional[int]) -> None
        self.verbose_name = verbose_name
        self.file_name = file_name
        self.extra_filters = extra_filters or Q()
        self.limit = limit

    @property
    @abstractmethod
    def content_type(self):  # type: () -> str
        """Return the response Content-Type."""

    @abstractmethod
    def get_content(self, smart_list, value_renderer):  # type: (SmartList, Callable[[Any], str]) -> bytes
        """Given the SmartList to be exported, return the export file contents."""

    def get_items(self, smart_list):  # type: (SmartList) -> Iterable[SmartListItem]
        """Return an iterable of SmartListItem objects to be exported."""
        extra_filters = self.extra_filters() if callable(self.extra_filters) else self.extra_filters
        query_set = smart_list.object_list.filter(extra_filters)
        if self.limit is not None:
            query_set = query_set[: self.limit]
        return (SmartListItem(smart_list, obj) for obj in query_set)


class SmartListExcelExportBackend(SmartListExportBackend):

    content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    def get_content(self, smart_list, value_renderer):  # type: (SmartList, Callable[[Any], str]) -> bytes
        wb = Workbook()
        ws = wb.active

        ws.append([value_renderer(column.get_title()) for column in smart_list.get_columns()])
        for item in self.get_items(smart_list):
            ws.append([value_renderer(field.get_value()) for field in item.fields()])

        # using a naive method of determining widths of columns
        for column_cells in ws.columns:
            length = max(len(str(cell.value)) for cell in column_cells)
            ws.column_dimensions[column_cells[0].column_letter].width = length

        content = six.BytesIO()
        wb.save(content)
        return content.getvalue()
