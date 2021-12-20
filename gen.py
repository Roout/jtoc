import json
import re
import sys
from datetime import datetime
from typing import Any

class CodeGenerator:

  def __init__(self, scopes: list[str], structs: list[list[tuple]], used: set[str]):
      self.scopes = scopes
      self.structs = structs
      self.used = used
      self.footer = ''
      # this is all supported types and array:
      # std::array<one_of_supported_type, ...>
      self.methods_by_type = {
        'bool': 'GetBool()', 
        'float': 'GetFloat()', 
        'int': 'GetInt()', 
        'std::string': 'GetString()'}

  @staticmethod
  def cpp_numeric(typename: str, value):
    s = str(value)
    if s.find('.') >= 0:
      s += 'f'
    elif typename == 'float':
      s += '.f'
    return s

  # rules to generate variable names (public data members)
  # from underscores
  # Camel Case
  @staticmethod
  def cpp_var_name(json_field: str):
    json_field = json_field[0].lower() + json_field[1:]
    return re.sub('(_[a-z])', lambda m: m.group(1)[1].upper(), json_field)
    
  # TODO: just save previous name somewhere and query it
  @staticmethod
  def json_var_name(variable: str):
    assert len(variable) > 0
    assert variable[0].islower()
    return re.sub('([A-Z])', lambda m: '_' + m.group(1).lower(), variable)
  
  # rules to generate class names (public data members)
  # Camel Case
  @staticmethod
  def cpp_class_name(json_field:str):
    json_field = json_field[0].upper() + json_field[1:]
    return re.sub('(_[a-z])', lambda m: m.group(1)[1].upper(), json_field)


  def array_parser_func(self, indent: str, fulltype: str, array_name: str, object_instance: str):
    assert fulltype.find('std::array') != -1, 'Expect `std::array<T, size>` string'
    array_parser = ''

    matched = re.search(r'< *([^,]+) *, *([0-9]+) *>', fulltype)
    assert matched != None
    innertype = matched.groups(2)[0]
    innersize = matched.groups(2)[1]

    if innertype not in self.methods_by_type:
      raise ValueError('Unsupported type')

    method = self.methods_by_type[innertype]
    array_parser += '{}const auto& values = json["{}"].GetArray();\n'.format(indent, array_name)
    array_parser += '{}for (size_t i = 0; i < {}; i++) {{\n'.format(indent, innersize)
    array_parser += '{}  {}.{}[i] = values[i].{}\n'.format(indent, object_instance, array_name, method)
    array_parser += '{}}}\n'.format(indent)

    return array_parser

  def buffer_parser_func(self, class_name: str, struct: list[tuple]):
    obj_instance = self.cpp_var_name(class_name)
    self.footer += 'inline void FromJson(const rapidjson::Value& json, {}& {}) {{\n'.format(
      class_name, obj_instance)
    for typename, variable in struct:
      if typename in self.used:
        # it's an object of custom type
        self.footer += '  FromJson(json["{}"], {}.{});\n'.format(
          self.json_var_name(variable),
          obj_instance,
          variable)
      elif typename.find('std::array') != -1:
        self.footer += self.array_parser_func('  ', typename, variable, obj_instance)
      else:
        self.footer += '  {}.{} = json["{}"].{};\n'.format(
          obj_instance, 
          variable,
          self.json_var_name(variable),
          self.methods_by_type[typename]
        )
    self.footer += '}\n\n'

  @staticmethod
  def dump_class(class_name: str, struct: list[tuple], ostream = sys.stdout):
    print('struct {} {{'.format(class_name), file = ostream)
    for typename, varaible in struct:
      print('  {} {};'.format(typename, varaible), file = ostream)
    print('};\n', file = ostream)
  
  # generate a class name as concatenation of class scopes
  # it returns the name that is not used yet
  def choose_class_name(self):
    assert len(self.scopes) > 0
    class_name = str()
    for scope in reversed(self.scopes):
      class_name = scope + class_name
      if class_name not in self.used:
        self.used.add(class_name)
        return class_name
    return None

  def generate(self, json_value: Any, ostream = sys.stdout):
    if isinstance(json_value, dict):
      for key in json_value:
        if isinstance(json_value[key], dict):
          # add(open) class declaration i.e., create dict
          self.structs += [[]]
          self.scopes += [ CodeGenerator.cpp_class_name(key) ]
          self.generate(json_value[key], ostream)
          typename = self.choose_class_name()
          assert typename != None, 'all class names are already reserved'
          # close class declaration
          self.scopes.pop()
          struct = self.structs.pop()
          if len(self.structs) > 0:
            self.structs[-1] += [(typename, CodeGenerator.cpp_var_name(key))]
          CodeGenerator.dump_class(typename, struct, ostream)
          self.buffer_parser_func(typename, struct)
        elif isinstance(json_value[key], str):
          # declare string variable
          self.structs[-1] += [('std::string', CodeGenerator.cpp_var_name(key))]
        elif isinstance(json_value[key], list):
          array_len = len(json_value[key])
          assert array_len > 0, "wrong JSON sample: empty list as input"
          element_typename = type(json_value[key][0]).__name__
          # declare array variable
          self.structs[-1] += [
            ('std::array<{}, {}>'.format(element_typename, array_len), 
            CodeGenerator.cpp_var_name(key))]
        else:
          type_name = type(json_value[key]).__name__
          # declare float/int variable 
          self.structs[-1] += [(type_name, CodeGenerator.cpp_var_name(key))]


template = (
  '// This file is auto generated by script\n' + 
  '// Date: {}\n')

includes = (
  '#include <string>\n' + 
  '#include <array>\n\n' + 
  '#include "rapidjson/document.h"\n' + 
  '#include "rapidjson/writer.h"\n' + 
  '#include "rapidjson/stringbuffer.h"\n')

data = {}
with open('db.json', 'r') as istream:
  data = json.load(istream)
  
with open('generated.hpp', 'w') as ostream:
  print(template.format(datetime.now().strftime("%d/%m/%Y %H:%M:%S")), file = ostream)
  print(includes, file = ostream)
  print('namespace json_autogenerated_classes {\n', file = ostream)
  code_generator = CodeGenerator([], [], set())
  code_generator.generate(data, ostream)
  print('} // namespace json_autogenerated_classes\n', file = ostream)
  print('namespace json_autogenerated_classes {\n', file = ostream)
  print(code_generator.footer, file = ostream)
  print('} // namespace json_autogenerated_classes', file = ostream)