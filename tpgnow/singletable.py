from terminaltables import SingleTable
from terminaltables.width_and_alignment import align_and_pad_cell, max_dimensions
from terminaltables.build import build_border, build_row, flatten


class SingleTableUnescaped(SingleTable):
    """The original table does escaping, etc. based on the execution platform (win, linux).
    We want it more "natural". For web use as well :-) """

    CHAR_F_INNER_HORIZONTAL = '─'
    CHAR_F_INNER_INTERSECT = '┼'
    CHAR_F_INNER_VERTICAL = '│'
    CHAR_F_OUTER_LEFT_INTERSECT = '├'
    CHAR_F_OUTER_LEFT_VERTICAL = '│'
    CHAR_F_OUTER_RIGHT_INTERSECT = '┤'
    CHAR_F_OUTER_RIGHT_VERTICAL = '│'
    CHAR_H_INNER_HORIZONTAL = '─'
    CHAR_H_INNER_INTERSECT = '┼'
    CHAR_H_INNER_VERTICAL = '│'
    CHAR_H_OUTER_LEFT_INTERSECT = '├'
    CHAR_H_OUTER_LEFT_VERTICAL = '│'
    CHAR_H_OUTER_RIGHT_INTERSECT = '┤'
    CHAR_H_OUTER_RIGHT_VERTICAL = '│'
    CHAR_INNER_HORIZONTAL = '─'
    CHAR_INNER_INTERSECT = '┼'
    CHAR_INNER_VERTICAL = '│'
    CHAR_OUTER_BOTTOM_HORIZONTAL = '─'
    CHAR_OUTER_BOTTOM_INTERSECT = '┴'
    CHAR_OUTER_BOTTOM_LEFT = '└'
    CHAR_OUTER_BOTTOM_RIGHT = '┘'
    CHAR_OUTER_LEFT_INTERSECT = '├'
    CHAR_OUTER_LEFT_VERTICAL = '│'
    CHAR_OUTER_RIGHT_INTERSECT = '┤'
    CHAR_OUTER_RIGHT_VERTICAL = '│'
    CHAR_OUTER_TOP_HORIZONTAL = '─'
    CHAR_OUTER_TOP_INTERSECT = '┬'
    CHAR_OUTER_TOP_LEFT = '┌'
    CHAR_OUTER_TOP_RIGHT = '┐'

    def __init__(self, *args, **kwargs):
        """If we specified the column_widths already in the constructor, then set them right away"""
        self.column_widths = kwargs.get("column_widths", None)
        super(SingleTable, self).__init__(*args, **kwargs)

    @property
    def column_widths(self):
        """If we set our own column width, then we take that one, otherwise we will use the default one"""
        if self.__column_widths:
            return self.__column_widths
        else:
            return super(SingleTable, self).column_widths

    @column_widths.setter
    def column_widths(self, col_widths):
        """We can actually set our own column_widths"""
        self.__column_widths = col_widths

    @property
    def table(self):
        """
        Return a large string of the entire table ready to be printed to the terminal.
        In this version we actually add a padding of one space to the title.
        It looks nicer that way.
        """
        if self.title:
            self.title = " %s " % self.title.strip() # add spaces around the title (remove existing ones beforehand)
        if self.__column_widths:
            dimensions = (self.column_widths, [1]*len(self.table_data), [i+2 for i in self.column_widths])
        else:
            dimensions = max_dimensions(self.table_data, self.padding_left, self.padding_right)[:3]

        return flatten(self.gen_table(*dimensions))
