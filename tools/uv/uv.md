


## python version 
```shell
# install
uv python install cpython-3.12

# run 
uv run -p 3.12 python  # 
uv run -p 3.12 ai.py

```

## python dependency

```shell

# init project
uv init -p 3.10
uv add requests

uv tree # list dep

# dev
uv add ruff --dev
ruff check
uv remote ruff --dev

#  install tool
uv tool install ruff # install to system 
ruff check
where ruff  # where ruff  : c:\Users\jason\.local\bin\ruff.exe
    # list tool
uv tool list

# add project.scripts section 
uv build   # package a wheel







```
