# Lessons Learned

1. Proteins with more than 9999 atoms cannot be processed with sphgen. This is
why we need to create active sites.
2. Several binaries have problems with path length. Some will cut off input
paths beyond 80 characters. Keep this in mind when specifiying paths. Many
commandline calls are performed in the output directories to minimize 
path length. How this can unironically be a problem in \<current year\> is
beyond me.
3. On the other hand some binaries __require__ absolute paths because they
ignore the current working directory.
