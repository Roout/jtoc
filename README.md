# JTOC: JSON to CPP Generator Tool

This is a custom cpp code generator I intend to use for my [platformer game](https://github.com/Roout/platformer).

## Purpose

The game has a lot of parameters and it should be comfortable to use **json** configurations to save them. The tool should help me with this. The main purpose is to help me in development of [this](https://github.com/Roout/platformer) game. I recently decided that it's time to introduce some json configs with constants because it's too much for me always recompile the game after changing any constant. Sometimes I wish to test the behaviour of units with different parameters. I also want to have one function `FromJson(...)` which will parse all config into object so this object (not the fucking `rapidjson::document`) will be accessed in the application. This way I will have autocompletion hints, no additional typecasts and searches in dictionaries, no additional checks whether the field exist or not, etc. It's a great help in development proccess.  

Another purpose is to play with python.

## Features

It generates:

- classes
- object parser functions: `FromJson(const rapidjson::Value&, T& object)`

Target cpp standard: c++11 or higher

## Restrictions

### Types

It's now only support several simple types:

```python
self.methods_by_type = {
  'bool': 'GetBool()', 
  'float': 'GetFloat()', 
  'int': 'GetInt()', 
  'std::string': 'GetString()'}
```

It also can generate arrays like `std::array<T, Size>` if `T` is a simple type from above.

Array of custom (user-defined) types is also supported but has strict restriction.
All subobjects of the same array **MUST** have the same structure i.e, all their **keys are SAME** (so they can be converted to the objects of the same type). Of course values can be different. See example below.

Snippet taken from [here](https://github.com/Roout/jtoc/blob/master/res/example_3.json)

```json
{
  "menu": {  
    "id": "file",  
    "value": "File",  
    "popup": {  
      "menuitem": [  
        { "value": "New", "onclick": "CreateDoc()"},  
        { "value": "Open", "onclick": "OpenDoc()"},  
        { "value": "Save", "onclick": "SaveDoc()"}  
      ]  
    }  
  }
}  
```

Cpp generator can handle now this type of schemas:

```cpp
struct Menuitem {
  std::string value;
  std::string onclick;
};

struct Popup {
  std::array<Menuitem, 3> menuitem;
};

struct Menu {
  std::string id;
  std::string value;
  Popup popup;
};
```

You can see more detailed output [here](https://github.com/Roout/jtoc/blob/master/res/example_3.hpp.txt)

### Names

Naming conventions? Thrown away...
Now it supports **JSON SCHEMA** with `snake_case_without_capitals`. These types and variables will be converted to `CamelCase` with uppercase first letter for class name and `camelCaseVariables` for other variables/data members.  
Obviously ACRONYMS not supported.

### Toolchain

- Python3

## Run

Provide input and output file names like in the example

```bash
$ ls
external/  gen.py  LICENSE  README.md  res/
$ py gen.py -h
usage: gen.py [-h] [-i INPUT] [-o OUTPUT]

Generate a c++ file from the json schema

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        path to json schema
  -o OUTPUT, --output OUTPUT
                        c++ file which will be generated from json schema
$ py gen.py -i res/example_0.json -o res/example_0.hpp
```
