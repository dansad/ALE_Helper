# You run it with 
# python ale_changer.py [PATH_TO_FILE]
import sys

args = sys.argv
if (len(args) > 1):
  PATH_TO_FILE = args[1] 
else:
  print('No file found')

  
DELIMITER = '\t'
LINE_BREAK = '\n'
if sys.version.startswith('2'):
  LINE_BREAK =  '\r\n'

class Translation:
  
  def __init__(self, kind=None):
    if kind:
      self.kind = kind
    
  def kind(self, kind):
    '''kind should by "copy", "rename","filename_extract","recipe","delete" '''
    self.kind = kind
    return self
  
  def existing_column(self, column):
    self.existing_column = column
    return self
    
  def new_column(self, column):
    self.new_column = column
    return self
    
  def recipe(self, recipe_string):
    self.recipe_string = recipe_string
    return self

class Ale:
  
  def __init__(self, filepath, delimiter=DELIMITER, linebreak=LINE_BREAK):
    self.delimiter = delimiter
    self.linebreak = linebreak
    self.filepath = filepath
    
    self.header = []
    self.column_names = []
    self.data = []
    
    self.parse_file()
  
  def parse_file(self):
    f = open(self.filepath, 'r')
    lines = f.readlines()
    f.close()
    
    first_empty = lines.index(self.linebreak)
    column_index = lines.index('Column' + self.linebreak)
    data_index = lines.index('Data' + self.linebreak)
    
    columns = lines[column_index + 1]
    columns = columns.replace(self.linebreak, '')
    data = lines[data_index+1:]
    
    
    self.header = lines[0:first_empty]
    self.column_names = [x for x in columns.split(self.delimiter) if len(x) > 0]
    for line in data:
      line = line.replace(self.linebreak, '')
      line = line.strip()
      if (len(line) > 0):        
        data_list = line.split(self.delimiter)
        self.data.append(Ale_line(data_list, self.column_names))
   
  def copy_just_the_filename(self, existing_column, new_column):
    self.column_names.append(new_column)
    for ale_line in self.data:
      fullpath = ale_line[existing_column]
      value_to_copy = self.get_file_name(fullpath)
      ale_line[new_column] = value_to_copy
  
  def get_file_name(self, path):
    last_slash = path.rfind('/')
    return path[last_slash +1 :]
  
  def copy_column(self, existing_column, new_column):
    
    self.column_names.append(new_column)
    for ale_line in self.data:
      value_to_copy = ale_line[existing_column]
      ale_line[new_column] = value_to_copy
  
  def rename(self, existing_column, new_column):
    existing_index = self.column_names.index(existing_column)
    self.column_names[existing_index] = new_column
    
    for ale_line in self.data:
      val = ale_line[existing_column]
      ale_line[new_column] = val
      ale_line.delete(existing_column)
  
  def handle_recipe(self, new_column, recipe):
    self.column_names.append(new_column)
    
    for ale_line in self.data:
      val = ale_line.parse_recipe(recipe)
      ale_line[new_column] = val
    
  def delete_column(self, existing_column):
    self.column_names.remove(existing_column)
    
    for ale_line in self.data:
      ale_line.delete(existing_column)
  
  def get_output_name(self):
    extension_index = self.filepath.rfind('.ale')
    output_path = self.filepath[:extension_index] + '_UPDATED.ale'
    return output_path
  
  def get_writeable_data(self):
    # A list of DELIMITER delimited strings
    writable_lines = []
    
    for line in self.data:
      values = []

      for i in range(len(self.column_names)):
        column_name = self.column_names[i]
        val = line[column_name]
        values.append(val)
      
      writable_line = self.delimiter.join(values)
      writable_lines.append(writable_line)

    return writable_lines
 
  def write_to_file(self):
    w = open(self.get_output_name(),'w')
        
    w.writelines(self.header)
    w.write(self.linebreak)
    
    w.write('Column'+self.linebreak)    
    columns = self.delimiter.join(self.column_names) + self.linebreak
    w.write(columns)
    w.write(self.linebreak)
    
    w.write('Data' + self.linebreak)
    lines = self.get_writeable_data()
    lines = self.linebreak.join(lines)
    w.write(lines)
    
    w.write(self.linebreak)
    
    w.close()
    
  def process(self):
    for trans in translations:
      if trans.kind != 'recipe' and trans.existing_column not in self.column_names:
        print('The name "' + str(trans.existing_column) +'" was not found in the file')
        continue
    
      if trans.kind == 'copy':
        self.copy_column(trans.existing_column, trans.new_column)
      
      if trans.kind == 'filename_extract':
        self.copy_just_the_filename(trans.existing_column, trans.new_column)
        
      if trans.kind == 'rename':
        self.rename(trans.existing_column, trans.new_column)
      
      if trans.kind == 'recipe':
        self.handle_recipe(trans.new_column,trans.recipe_string)
        
      if trans.kind == 'delete':
        self.delete_column(trans.existing_column)
  
  def go(self):
    self.process()
    self.write_to_file()
    print('Done. --> ' + self.get_output_name())

class Ale_line:
  def __init__(self, data_list, column_name_list):
    self.record = {}
    
    for i in range(len(data_list)):
      self.record[column_name_list[i]] = data_list[i]
      
  def __setitem__(self, name, value):
    self.record[name] = value
  
  def __getitem__(self, name):
    return self.record[name]
  
  def delete(self,name):
    del self.record[name]
    return self
    
  def parse_recipe(self,recipe):
    r = self.record
    val = eval(recipe)
    return val

# CHANGE THIS PART
translations = [
  Translation('filename_extract').existing_column('Sync Audio').new_column('Audiofile'),
  Translation('copy').existing_column('LUT Used').new_column('LUT'),
  Translation('copy').existing_column('Tape').new_column('Camroll'),
  Translation('copy').existing_column('Auxiliary TC1').new_column('Aux TC 24'),
  Translation('delete').existing_column('Name'),
  Translation('recipe').new_column('Name').recipe("r['Scene'] + '-' + r['Take'].lstrip('0') + r['Tape'][0].lower()"),
  Translation('recipe').new_column('Camroll').recipe("r['Tape'][:5]")
]
# STOP CHANGE

#first 4 of Tape Camroll

if __name__ =='__main__':
  
  ale_changer = Ale(PATH_TO_FILE)
  ale_changer.go()
  
  
  