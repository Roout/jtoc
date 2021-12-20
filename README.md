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

### Names

Naming conventions? Thrown away...
Now it supports **JSON SCHEMA** with `snake_case_without_capitals`. These types and variables will be converted to `CamelCase` with uppercase first letter for class name and `camelCaseVariables` for other variables/data members.  
Obviously ACRONYMS not supported.

### Toolchain

- Python3

## Run

...
