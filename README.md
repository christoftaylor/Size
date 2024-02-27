# Size
A script that lists the sizes of items in a directory with directory sizes being the sum total of recursing their children.  
This could have been `du --max-depth=1 -h | sort -h`, but sort on my NAS doesn't do -h.  
And since I was bored, I prettied up the output a bit.  

```
usage: size.py [-h] [-v] [-r] [path]

Prints out directory listing sorted by total recursive size for directories.

positional arguments:
  path           Optional. The starting path. Current directory if not specified.

options:
  -h, --help     show this help message and exit
  -v, --verbose  Include more columns in output.
  -r, --reverse  Reverse the sort order to put big stuff at the top.
```
