import os
import os.path as path
import sys

block_comment_stack = []

def skip(line):
	return is_empty_line(line) or is_import(line) or is_package(line)

def is_empty_line(line):
	return line.isspace()

def is_line_comment(line):
	return line.strip(' \t').startswith('//')

def is_import(line):
	return line.startswith('import ')

def is_package(line):
	return line.startswith('package ')

def process_block_comment(line, block_comment_stack):
	minimum = 0
	bc_start_index = line.find('/*', minimum)
	bc_end_index = line.find('*/', minimum)
	while bc_start_index > -1 or bc_end_index > -1:
		if bc_start_index == -1:
			block_comment_stack.pop()
			minimum = bc_end_index
		elif bc_end_index == -1:
			block_comment_stack.append(1)
			minimum = bc_start_index
		else:
			if bc_start_index < bc_end_index:
				block_comment_stack.append(1)
				minimum = bc_start_index
			else:
				block_comment_stack.pop()
				minimum = bc_end_index 
		bc_start_index = line.find('/*', minimum + 1)
		bc_end_index = line.find('*/', minimum + 1)

def process_file(f_name, counts):
	""" Processes a single Java file and counts the number of code lines."""
	loc = comments = total = 0
	block_comment_stack = []
	with open(f_name) as f:
		for line in f:
			before = len(block_comment_stack)
			process_block_comment(line, block_comment_stack)
			after = len(block_comment_stack)
			if ((before > 0 and after == 0) or after > 0):
				comments += 1
			else:
				if is_line_comment(line):
					comments += 1
				elif not skip(line):
					loc += 1
			total += 1

	counts['loc'] += loc
	counts['comments'] += comments
	counts['total'] += total
	counts['files'] += 1

def traverse(dir_path, counts):
	""" traverses a given directory to find Java source files. """
	for entry in os.listdir(dir_path):
		f_path = path.normpath(path.join(dir_path, entry))
		if path.isfile(f_path) and f_path.endswith('.java'):
			print('Processing Java file: ', f_path)
			process_file(f_path, counts)
		elif path.isdir(f_path):
			traverse(f_path, counts)


if __name__=='__main__':
	src_root = sys.argv[1]
	abs_path = path.abspath(src_root)
	counts = {'loc':0, 'comments':0, 'total':0, 'files':0}
	traverse(abs_path, counts)
	print(counts)

