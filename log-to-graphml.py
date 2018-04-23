import itertools, collections
import xml.etree.cElementTree as ET

# Setup the header XML element, including
# the links to the schema
root = ET.Element('graphml')
root.set('xmlns',
        'http://graphml.graphdrawing.org/xmlns')
root.set('xmlns:xsi',
        'http://www.w3.org/2001/XMLSchema-instance')
root.set('xsi:schemaLocation', 'http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd')

# Setup the actor_type attribute for nodes
keyd0 = ET.Element('key')
keyd0.set('id', 'd0')
keyd0.set('for', 'node')
keyd0.set('attr.name', 'actor_type')
keyd0.set('attr.type', 'int')

# Enum-like class for the actor_type attribute
class NodeActorType():
    CONTRIBUTOR = 0
    FILE = 1

# Setup the label attribute for nodes
keyd1 = ET.Element('key')
keyd1.set('id', 'd1')
keyd1.set('for', 'node')
keyd1.set('attr.name', 'email')
keyd1.set('attr.type', 'string')

# Setup the Git commit contributor name / filename
# attribute
keyd2 = ET.Element('key')
keyd2.set('id', 'd2')
keyd2.set('for', 'node')
keyd2.set('attr.name', 'name')
keyd2.set('attr.type', 'string')

# Put the attribute subtrees on the XML element tree
root.append(keyd0)
root.append(keyd1)
root.append(keyd2)

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

def generate_node_id():
    global node_id
    temp = node_id
    node_id = node_id + 1
    return temp

def generate_edge_id():
    global edge_id
    temp = edge_id
    edge_id = edge_id + 1
    return temp

def insert_contributor_node(data):
    global graph
    # Get the email and username data
    email = data[0]
    username = data[1]

    # Generate the contributor id
    node_id = 'n' + str(generate_node_id())

    # Build the XML tree
    node = ET.Element('node')
    node.set('id', node_id)
    # Fill out the actor_type attribute
    datad0 = ET.SubElement(node, 'data')
    datad0.set('key', 'd0')
    datad0.text = str(NodeActorType.CONTRIBUTOR)

    # Fill out the email attribute
    datad1 = ET.SubElement(node, 'data')
    datad1.set('key', 'd1')
    datad1.text = data[0]

    # Fill out the name attribute (for the contributor)
    datad2 = ET.SubElement(node, 'data')
    datad2.set('key', 'd2')
    datad2.text = data[1]

    # Finally, add the node to the graph
    graph.append(node)

    # Return the node_id that was created
    return node_id

def insert_file_node(filename):
    global graph

    # Generate the contributor id
    node_id = 'n' + str(generate_node_id())

    # Build the XML tree
    node = ET.Element('node')
    node.set('id', node_id)

    # Fill out the actor_type attribute
    datad0 = ET.SubElement(node, 'data')
    datad0.set('key', 'd0')
    datad0.text = str(NodeActorType.FILE)

    # Fill out the email attribute
    datad1 = ET.SubElement(node, 'data')
    datad1.set('key', 'd1')
    datad1.text = ''

    # Fill out the name attribute (for the contributor)
    datad2 = ET.SubElement(node, 'data')
    datad2.set('key', 'd2')
    datad2.text = filename

    # Finally, add the node to the graph
    graph.append(node)

    # Return the node_id that was created
    return node_id

def insert_commit_edge(contributor_id, file_id):
    global graph

    # Generate the contributor id
    edge_id = 'e' + str(generate_edge_id())

    # Build the XML tree
    edge = ET.Element('edge')
    edge.set('id', edge_id)
    edge.set('source', contributor_id)
    edge.set('target', file_id)

    # Finally, add the node to the graph
    graph.append(edge)

    # Return the node_id that was created
    return edge_id
    

def parse_entry(it):
    global line
    global graph
    # Parse the commit info line for that line
    parts = line.split('|')

    # Remove empty strings from the list
    parts = filter(None, parts)
    print('parts: ' + ' | '.join(parts))
    next_line(it)

    # Add the new contributor node to the list
    # only if it already is not there.
    contributor_id = ''
    contributor_found = False
    for node_elem in graph.findall('node'):
        found_data_elem = node_elem.find('./data[@key=\'d1\']')
        if found_data_elem is not None:
            print(ET.tostring(found_data_elem, 'utf-8'))
            if found_data_elem.text == parts[0]:
                contributor_id = node_elem.get('id')
                contributor_found = True
                break
        else:
            print('Could not find data...')

    if contributor_found:
        print('Contributor ' + parts[0] + ' already found')
    else:
        print('Contributor ' + parts[0] + ' not found')
        print('Inserting contributor node into graph...')
        contributor_id = insert_contributor_node(parts)

    print('ContributorID: ' + contributor_id)

    # For each file, mark it.
    files = []
    sentinel = object()
    while (line != '$'):
        if (line.strip() != ''):
            files.append(line)

            file_id = ''

            # Add the new file node to the graph
            # only if it already is not there.
            filename_found = False
            for node_elem in graph.findall('node'):
                found_data_elem = node_elem.find('./data[@key=\'d2\']')
                if found_data_elem is not None:
                    print(ET.tostring(found_data_elem, 'utf-8'))
                    if found_data_elem.text == line:
                        file_id = node_elem.get('id')
                        filename_found = True
                        break
                else:
                    print('Could not find file...')

            if filename_found:
                print('Filename ' + line + ' already found')
            else:
                print('Filename ' + line + ' not found')
                print('Inserting file node into graph...')
                file_id = insert_file_node(line)
            print('FileID: ' + file_id)

            # Finally, insert the edge.
            insert_commit_edge(contributor_id, file_id)

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
    tree = ET.ElementTree(root)
    tree.write(
            open('git-commit.graphml', 'w'),
            encoding='utf-8')

