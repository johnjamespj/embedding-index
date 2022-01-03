# Task manager module

# Helpful commands
* remove all cache files `rm -r ./**/**/__pycache__ ./**/__pycache__`

* run N workers `for i in {0..N}; do python3 worker.py 2>&1 &> /tmp/log & done`
* kill all workers `kill $(jobs -p)`
* list all workers `jobs -l`