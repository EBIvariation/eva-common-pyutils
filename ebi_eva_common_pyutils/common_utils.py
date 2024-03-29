# Copyright 2020 EMBL - European Bioinformatics Institute
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


def merge_two_dicts(x, y):
    z = x.copy()  # start with x's keys and values
    z.update(y)  # modifies z with y's keys and values & returns None
    return z


def pretty_print(header, table):
    cell_widths = [len(h) for h in header]
    for row in table:
        for i, cell in enumerate(row):
            cell_widths[i] = max(cell_widths[i], len(str(cell)))
    format_string = ' | '.join('{%s:>%s}' % (i, w) for i, w in enumerate(cell_widths))
    print('| ' + format_string.format(*header) + ' |')
    for row in table:
        print('| ' + format_string.format(*row) + ' |')
