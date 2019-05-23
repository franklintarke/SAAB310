def short():
  print('short')

def long():
  print('long')

import button
but = button.BUTTON()
but.short = short
but.long = long
