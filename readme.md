# NOTE: This project is created for learning inner logic of an Interpred language, it is implemented in Pyhton, feel free to contribute and fork!!!

<p align="center">
<img width="300" height="400" alt="image" src="https://github.com/user-attachments/assets/58c6ed5b-16af-4f6d-8b6a-182e48f24921" />
</p>

# Build to exe is made using pyinstaller, refer documentation of pyinstaller for more info!!

# How to use??
```
  ./Rango.exe simply.rango  /// without debug and logging
  ./Rango.exe simply.rango  True /// with debug and logging
``` 

# Interpreter Language Documentation

This document provides an overview of the syntax and features of the **Interpreter Language**.  
It is an **object-oriented**, **block-scoped** language that supports **higher-order functions**, **complex expressions**, and **structured programming** constructs.

---

## Features

- **Object-Oriented Programming**
  - All attributes are **private**
  - Access controlled via **getters** and **setters**
  - Methods and attributes are accessed via the `->` operator
- **Block Scope**
  - Variables defined inside blocks are not visible outside
- **Higher-Order Functions**
  - Functions can be passed, returned, or assigned as values
- **Conditionals & Loops**
  - `if / else_if / else`
  - `repeat N times`
  - `till (condition)`
- **Complex Expressions**
  - Arithmetic, relational, and logical operators with precedence

---

## Variables

To create a variable:
``` 
a is value/expression/function_call/nil
```

- The keyword `is` is used for assignment.  
- There is no other way to define a variable.  

Example:
``` 
x is 10
y is x * 2
```

---

## Comments

To write comments use the `note` keyword:  
- `note` operator marks the start of a comment  
- `.` operator marks the end of a comment  

Example:
``` 
note This is a comment .
```

---

## Operators

### Arithmetic (with precedence)
- `+` (Addition)  
- `-` (Subtraction)  
- `*` (Multiplication)  
- `/` (Division)  

### Relational
- `eq` → equals  
- `noteq` → not equals  
- `lt` → less than  
- `gt` → greater than  
- `lteq` → less than or equal to  
- `gteq` → greater than or equal to  

### Logical
- `and`  
- `or`  

---

## Classes and Objects

### Defining a Class
``` 
class Y {
    var is 10;
    show(var);

    does y() {
        show("inside class Y");
    }

    itSelf a is itSelf y();
    show("checking inside Y", itSelf a);
}
```

- `class` keyword defines a new class.  
- `var` defines attributes (private by default).  
- `does` keyword defines methods.  
- `itSelf` is used to reference the current class’s **methods or attributes**.  
- If `itSelf` is not used, variables/functions are resolved from the **global scope**.  

---

### Creating Objects
``` 
create Y myObj;
```

### Accessing Methods
``` 
myObj->y();
```

### Accessing Attributes
``` 
myObj->getVar();
myObj->setVar(20);
```

---

## Control Structures

### If / Else If / Else
``` 
if(condition) {
    // code
} else_if(condition) {
    // code
} else {
    // code
}
```

### Loops

#### Repeat Loop
``` 
repeat 10 times {
    show("Hello");
}
```

#### Till Loop
``` 
till(x gt 10) {
    x = x + 1;
}
```

---

## Functions

- Functions are **first-class citizens**.  
- Can be passed as arguments, returned from functions, and assigned to variables.  

Example:
``` 
does square(x) {
    return x * x;
}

does apply(f, value) {
    return f(value);
}

show(apply(square, 5)); // prints 25
```

---

## Summary

The **Interpreter Language** is designed for clarity and flexibility:
- Private attributes with enforced access through getters/setters.  
- `itSelf` keyword ensures encapsulation inside classes.  
- Object-oriented with clean syntax for object creation and method calls.  
- Powerful control flow (`if`, `repeat`, `till`) and operator support.  
- Higher-order functions for functional-style programming.  

