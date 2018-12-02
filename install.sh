#!/usr/bin/env bash
script_dir=$(cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd)
cd ${script_dir}
touch domains.txt index.txt mail.txt e-mails.txt log.txt users.txt keywords.txt
echo "alias start_parser='nohup python3 $script_dir/parser.py >> $script_dir/log.txt 2>&1 &'" >> ~/.bashrc
