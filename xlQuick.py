from xlutils.copy import copy
import xlwt
import xlrd
from datetime import datetime

workbook = xlrd.open_workbook('example.xls', on_demand = True, formatting_info=True)
wb = copy(workbook)

style0 = xlwt.easyxf('font: name Times New Roman, color-index red, bold on',
    num_format_str='#,##0.00')
style1 = xlwt.easyxf(num_format_str='D-MMM-YY')

wb = xlwt.Workbook()
ws = wb.get_sheet(0)

ws.write(0, 0, 1234.56, style0)
ws.write(1, 0, datetime.now(), style1)
ws.write(2, 0, 1)
ws.write(2, 1, 1)
ws.write(2, 2, xlwt.Formula("A3+B3"))
# def _getOutCell(outSheet, colIndex, rowIndex):
#     """ HACK: Extract the internal xlwt cell representation. """
#     row = outSheet._Worksheet__rows.get(rowIndex)
#     if not row: return None
#
#     cell = row._Row__cells.get(colIndex)
#     return cell
#
# def setOutCell(outSheet, col, row, value):
#     """ Change cell value without changing formatting. """
#     # HACK to retain cell style.
#     previousCell = _getOutCell(outSheet, col, row)
#     # END HACK, PART I
#
#     outSheet.write(row, col, value)
#
#     # HACK, PART II
#     if previousCell:
#         newCell = _getOutCell(outSheet, col, row)
#         if newCell:
#             newCell.xf_idx = previousCell.xf_idx
#     # END HACK

# outSheet = wb.get_sheet(0)
# setOutCell(outSheet, 2, 2, 'Test')
wb.save('importNumbers.xls')
