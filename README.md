# vim-auto-fix

vim plugin to fix word before cursor

## requires
* python3
* `pip3 install PyYAML`

## how to use
```
imap <C-x><C-x> <Plug>(vim-auto-fix:fix)
nnoremap <silent> <C-x><C-x> :call vim_auto_fix#auto_fix()<CR>
```

## settings
* `~/.config/auto_fix/fix.json`: default data filepath
* `~/.config/auto_fix/fix.log`: default log data filepath

----

## test
```
cd autoload
python -m unittest auto_fix_test.py
```
