if !has('python3')
  echo "[vim-auto-fix][ERROR]: Required vim compiled with +python3"
  finish
endif

if exists('g:loaded_vim_auto_fix')
  finish
endif
let g:loaded_vim_auto_fix = 1

let s:save_cpo = &cpo
set cpo&vim

let g:vim_auto_fix_auto_startup = get(g:, 'vim_auto_fix_auto_startup', 0)

command! -nargs=? -complete=file AutoFixDumpToFile :call vim_auto_fix#dump_to_file(<f-args>)
command! -nargs=1 AutoFixAddWord :call vim_auto_fix#add_word(<f-args>)
command! -nargs=1 AutoFixAddWordCommon :call vim_auto_fix#add_word_common(<f-args>)
command! -nargs=+ AutoFixAddWordFileType :call vim_auto_fix#add_word_ft(<f-args>)

" NOTE: you cannot modify line(call setline()) at insert mode
" :help <expr>
" >For this reason the following is blocked:
" >- Changing the buffer text |textlock|.
" >- Editing another buffer.
" 1. <C-r>=<expr>
" 2. <expr>内でキー操作そのものを返す
" 3. <expr>で処理をするのをあきらめる
" correct cursor positionは<C-o>ではなく，<C-\><C-O>,<expr>,<C-r>=利用時は取得可能
" FYI: [insert \- Vim日本語ドキュメント]( https://vim-jp.org/vimdoc-ja/insert.html#i_CTRL-\_CTRL-O )
inoremap <silent> <Plug>(vim-auto-fix:fix) <C-\><C-o>:call vim_auto_fix#auto_fix()<CR>
nnoremap <silent> <expr><Plug>(vim-auto-fix:fix) vim_auto_fix#auto_fix()

let &cpo = s:save_cpo
unlet s:save_cpo
