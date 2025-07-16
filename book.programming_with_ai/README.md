- In a different tmux
  ```
  > source $HOME/src/venv/mkdocs/bin/activate
  > (cd /Users/saggese/src/tutorials1/tmp.mkdocs; mkdocs serve --dev-addr localhost:8001)
  ```

- To render:
  ```
  > helpers_root/dev_scripts_helpers/documentation/mkdocs/preprocess_mkdocs.py --input programming_with_ai --output tmp.mkdocs
  ```
