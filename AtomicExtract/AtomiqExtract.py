###########################################################
# Version log
# 2014-January-28: Initial version written by Oguz Altun

######################################################
# Info
#
# This script extracts matches from Atomiq.Console_1.1.3.94.exe
# html output, and outputs to another html page. It is intended for
# preparing plagiarism reports.
#
# Specifically, this script
#     1) extracts specific blocks
#     2) show matching lines side by side
#     3) write a little more printer friendly tables

###################################################################
# Installation & Usage
#
# 1) Script needs BeautifulSoup package. install it if it is not in
#    your path.
# 2) Run Atomiq.Console yourself to get its output html file.
# 3) Edit the options below, and run the script.

###############################################################
#Options

# list of blocks to extract. At most 20th, because we gather from
# "top 20" from atomiq output. Starts from 1.
blocks = [1, 3, 7]
#blocks = range(1,7)

#the directory submissions
path_to_submissions_dir = '../submissions'

# path to atomiq output file.
path_to_atomiq_results = 'AtomiqResults.htm'

# path to output html file
path_to_output_file = 'AtomiqExtractResults.htm'

# you can modify the output by modifying header, footer, and block
# templates below
header_template = """
<html>
<head>
<title>Atomiq Extract Results</title>

<style type="text/css">
    pre {
        white-space: pre-wrap; /* css-3 */
        white-space: -moz-pre-wrap !important; /* Mozilla, since 1999 */
        white-space: -pre-wrap; /* Opera 4-6 */
        white-space: -o-pre-wrap; /* Opera 7 */
        word-wrap: break-word; /* Internet Explorer 5.5+ */
    }
    td{
        word-wrap: break-word;
    }
    .pagebreak { page-break-after: always; }
</style>

</head>
<body>

<h1>Selected Matches From Atomiq Output</h1>
"""

footer_template = """
</body></html>
"""

block_template = """

<h2>Match {blockno}, size = {size}</h2>

Left: {file1}, begin: {begin1}, end: {end1}
<br>
Right: {file2}, begin: {begin2}, end: {end2}

<table border=1 style="table-layout:fixed">

<tr>
<td width=50%>
<pre>
<code>{match1}</code>
</pre>
</td>

<td width=50%>
<pre>
<code>{match2}</code>
</pre>
</td>
</tr>

</table><br>\n
<span class="pagebreak"> </span>
"""

#######################################################
### script starts here ###
from bs4 import BeautifulSoup

import os

#### prepare path and import pymeta
filedir = os.path.dirname(os.path.realpath(__file__))
print('- Current Dir: ' + filedir)
os.chdir(filedir)

subdir = os.path.abspath(path_to_submissions_dir)
spardir = os.path.dirname(subdir)
print('- Submission Dir: ' + subdir)
print('- Submission Parent Dir: ' + spardir)

### we accept only block ids between 1 and 20
for i in blocks:
    if i > 20 or i < 1:
        raise Exception('Block ID needs to between 1 and 20')

### gather info from the atomiq output into the "records" table.
records = []
with open(path_to_atomiq_results, 'r') as f:
    ### find the first cell of the table we are interested in
    soup = BeautifulSoup(f)
    tables = soup.find_all('table')
    table = tables[3]
    td = table.find('td')

    for i in range(21):
        ### read next row
        row = []
        for c in range(5):
            row.append(td.text)
            td = td.find_next('td')

        ### if we are interested in this row extract data from row
        ### and append to the record table
        if i in blocks:
            file1, size, range1, file2, range2 = row
            file1 = file1.strip()[1:]
            file2 = file2.strip()[1:]
            size = int(size)
            begin1, end1 = [int(part) for part in range1.split(' - ')]
            begin2, end2 = [int(part) for part in range2.split(' - ')]
            records.append([file1, begin1, end1, file2, begin2, end2, size, i])

### write the extract output file
with open(path_to_output_file, 'w') as fe:
    ### write header
    fe.write(header_template)

    ### for each block we are interested
    for i, r in enumerate(records):
        file1, begin1, end1, file2, begin2, end2, size, blockno = r

        ### read first file
        with open(spardir + '/' + file1, 'r') as fs:
            lines = fs.readlines()
            lines = lines[begin1 + 1:end1 + 2]
            match1 = ''.join(lines)


        ### read second file
        with open(spardir + '/' + file2, 'r') as fs:
            lines = fs.readlines()
            lines = lines[begin2 + 1:end2 + 2]
            match2 = ''.join(lines)

        ### write block
        fe.write(block_template.format(
            blockno = str(blockno),
            size = str(size),
            file1 = file1,
            begin1 = str(begin1),
            end1 = str(end1),
            file2 = file2,
            begin2 = str(begin2),
            end2 = str(end2),
            match2 = str(match2),
            match1 = str(match1)
            ))

    fe.write(footer_template)

print('- Wrote matches to {}'.format(
    os.path.abspath(path_to_output_file)))
print('- Done.')
