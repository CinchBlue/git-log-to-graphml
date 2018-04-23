import itertools, collections
import xml.etree.cElementTree as ET

# Setup the header XML element, including
# the links to the schema
root = ET.Element('graphml')
root.set('xmlns',
        'http://graphml.graphdrawing.org/xmlns')
root.set('xmlns:xsi',
        'http://www.w3.org/2001/XMLSchema-instance')
root.set('xsi:schemaLocation',
          'http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd')

# Setup the actor_type attribute for nodes
keyd0 = ET.Element('key')
keyd0.set('id', 'd0')
keyd0.set('for', 'node')
keyd0.set('attr.name', 'actor_type')
keyd0.set('attr.type', 'integer')

# Setup the label attribute for nodes
keyd1 = ET.Element('key')
keyd1.set('id', 'd1')
keyd1.set('for', 'node')
keyd1.set('attr.name', 'email')
keyd1.set('attr.type', 'string')

# Setup the Git commit contributor name attribute
keyd2 = ET.Element('key')
keyd2.set('id', 'd2')
keyd2.set('for', 'node')
keyd2.set('attr.name', 'username')
keyd2.set('attr.type', 'string')

# Setup the filename attribute 
keyd3 = ET.Element('key')
keyd3.set('id', 'd3')
keyd3.set('for', 'node')
keyd3.set('attr.name', 'filename')
keyd3.set('attr.type', 'string')


# Put the two attribute subtrees on the XML
# element tree
root.append(keyd0)
root.append(keyd1)
root.append(keyd2)
root.append(keyd3)

# Prepare the graph subtree.
# This will be appended to.
graph = ET.Element('graph')
graph.set('id', 'G')
graph.set('edgedefault', 'directed')

# Integers to hold our global count for the
# node id and the edge id
node_id = 0
edge_id = 0

#debug
# Test XML capabilities
print(ET.tostring(root, 'utf-8'))

# A global line buffer to be used by the
# parsing procedures.
line = ''

def consume(iterator, n):
    collections.deque(itertools.islice(iterator, n))

def next_line(it):
    global line
    line = it.next()

def parse_entry(it):
    global line
    global graph
    # Parse the commit info line for that line
    parts = line.split('|')

    # Remove empty strings from the list
    parts = filter(None, parts)
    print('parts: ' + ' | '.join(parts))
    next_line(it)

    print(graph.findall('node'))

    # Add the new contributor node to the list
    # only if it already is not there.
    for node_elem in graph.findall('node'):
        if node_elem.findtext(parts[0]):
            print('FOUND: ' + parts[0])
        else:
            print('NOT FOUND: ' + parts[0])

    # For each file, mark it.
    files = []
    sentinel = object()
    while (line != '$'):
        if (line.strip() != ''):
            files.append(line)
            print('>>> ' + line)
        try:
            next_line(it)
        except StopIteration:
            print("End of file reached.")
            line = ''
            break
    print('files: ' + ','.join(files))


with open('git-commit.log', 'r') as file:
    # Get all the lines in the file
    lines = file.readlines()
    # Strip leading, trailing whitespace
    lines = [x.strip() for x in lines]

    #debug
    print(lines)

    # Get the iterator for the lines array
    it = iter(lines)
    line = it.next()

    # For each line, 
    while True:
        try:
            if (line == '$'):
                print('NEW ENTRY:')
                next_line(it)
                parse_entry(it)
            else:
                next_line(it)
        except StopIteration:
            print('Ended loop.')
            break
    root.append(graph)
    print(ET.tostring(root, 'utf-8'))

