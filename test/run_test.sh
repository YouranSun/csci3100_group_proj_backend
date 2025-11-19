# set path
$env:PYTHONPATH = "$env:PYTHONPATH;$PWD;${PWD}/cms"

# start testing
python run_all_test.py