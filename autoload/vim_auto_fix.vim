if !exists('g:loaded_vim_auto_fix')
  finish
endif
let g:loaded_vim_auto_fix = 1

let s:save_cpo = &cpo
set cpo&vim

if !exists("g:vim_auto_fix_log_flag")
  let g:vim_auto_fix_log_flag = 1
endif
if !exists("g:vim_auto_fix_log_filepath")
  let g:vim_auto_fix_log_filepath = $HOME."/.config/auto_fix/fix.log"
endif

let s:this_plugin_directory = escape(expand('<sfile>:p:h'), '\"')
execute printf('python3 import sys; sys.path += ["%s"]', s:this_plugin_directory)

" check result of loading python file
" e.g. required yaml package
let g:vim_auto_fix_error_flag = v:false
let g:vim_auto_fix_error_message=""
try
  py3file <sfile>:p:h/vim_bridge.py
catch
  echohl ErrorMsg
  for line in split(v:exception, "\n")
    echom line
    " don't use echoerr because this throw exception and break this scope
  endfor
  echohl NONE
  let g:vim_auto_fix_error_flag = v:true
  " echoerr ''
endtry

let g:fix_log=[]
let g:fix_log_backup=[]
function! vim_auto_fix#auto_fix(...)
  if g:vim_auto_fix_error_flag
    return v:false
  endif

  let cursor_col=get(a:, 1, col('.')-1)
  let line=getline('.')
  " NOTE: 厳密なカーソル区切り or expand('<cword>') 利用区切り?の検討
  let lbuffer=line[:cursor_col-1]
  let rbuffer=line[cursor_col:]
  let words=split(lbuffer,' \+')
  if len(words)==0
    return v:false
  endif
  let last_word=words[-1]
  let new_word=''
  try
    let new_word=py3eval("vim_auto_fix_bridge_auto_fix(vim.eval('last_word'), filetype=vim.eval('&filetype'))")
  catch
    echohl ErrorMsg
    for line in split(v:exception, "\n")
      echom line
      " don't use echoerr because this throw exception and break this scope
    endfor
    echohl NONE
    let g:vim_auto_fix_error_flag = v:true
    echoerr ''
  endtry

  let debug_log_flag=0
  if debug_log_flag==1
    let log_data={'lbuffer':lbuffer,'rbuffer':rbuffer,'last_word':last_word,'new_word':new_word}
    echo log_data
  endif
  " NOTE: for python exception
  if new_word==-1
    return v:false
  endif
  if new_word !=# last_word
    let g:fix_log+=[{'input':last_word,'output':new_word}]
    let lbuffer_space=matchstr(lbuffer,' \+$')
    let lbuffer=substitute(lbuffer,' \+$','','')
    let lbuffer=lbuffer[:-(len(last_word)+1)]
    let rbuffer=substitute(rbuffer,'^ \+',' ','')
    let newline=lbuffer.new_word.lbuffer_space.rbuffer
    call setline('.', [newline])
    let pos=getpos('.')
    let pos[2]=len(lbuffer)+len(new_word)+len(lbuffer_space)+1
    call setpos('.', pos)
    if debug_log_flag==1
      let log_data={'line':'['.line.']','newline':'['.newline.']'}
      echo log_data
    endif
    return v:true
  endif
  return v:false
endfunction

function! vim_auto_fix#add_word(word,...)
  if g:vim_auto_fix_error_flag
    return v:false
  endif

  let bad_words=get(a:, 1, [])
  call vim_auto_fix#add_word_ft(&filetype, a:word,bad_words)
endfunction
function! vim_auto_fix#add_word_ft(ft,word,...)
  if g:vim_auto_fix_error_flag
    return v:false
  endif

  let bad_words=get(a:, 1, [])
  python3 vim_auto_fix_bridge_add_data(vim.eval('a:ft'),vim.eval('a:word'),words=vim.eval('bad_words'))
  echom 'Please update data by :AutoFixDumpToFile'
endfunction
function! vim_auto_fix#add_word_common(word,...)
  if g:vim_auto_fix_error_flag
    return v:false
  endif

  let bad_words=get(a:, 1, [])
  call vim_auto_fix#add_word_ft('_', a:word,bad_words)
endfunction
function! vim_auto_fix#dump_to_file(...)
  if g:vim_auto_fix_error_flag
    return v:false
  endif

  let filepath=get(a:, 1, '')
  if empty(filepath)
    python3 vim_auto_fix_bridge_dump()
  else
    python3 vim_auto_fix_bridge_dump(vim.eval('filepath'))
  endif
endfunction

function! vim_auto_fix#flush_log()
  if g:vim_auto_fix_error_flag
    return v:false
  endif

  if g:vim_auto_fix_log_flag == 0
    return
  endif
  if empty(g:vim_auto_fix_log_filepath)
    return
  endif

  let vim_auto_fix_log_dirpath=fnamemodify(g:vim_auto_fix_log_filepath, ":h")
  if !isdirectory(vim_auto_fix_log_dirpath)
    call mkdir(vim_auto_fix_log_dirpath, "p")
  endif

  execute ":redir! >> ".g:vim_auto_fix_log_filepath
  " WARN: \n is printed by real newline
  silent! echo g:fix_log
  redir END

  let g:fix_log_backup=g:fix_log
  let g:fix_log={}
endfunction
function! vim_auto_fix#term()
  if g:vim_auto_fix_error_flag
    return v:false
  endif

  call vim_auto_fix#flush_log()
endfunction
augroup vim_auto_fix_term_group
  autocmd!
  autocmd VimLeavePre * call vim_auto_fix#term()
augroup END

let &cpo = s:save_cpo
unlet s:save_cpo
