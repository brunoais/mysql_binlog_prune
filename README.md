# mysql_binlog_prune
Tool to prune mysql binlog files based on size or number by querying MySQL server to delete old ones

# Requirements

* python 3.6 or a compatible above version (tested on python 3.8)
* `mysql` command part of `mysql-client` package
* `.cnf` file with mysql admin credentials (debian and derivatives already include one)

# Installation


```
wget "https://raw.githubusercontent.com/brunoais/mysql_binlog_prune/master/mysql_binlog_prune.py"
chmod +x "mysql_binlog_prune.py"
```

# How to use

```
./mysql_binlog_prune.py --help
```
