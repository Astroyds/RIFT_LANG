# RIFT Language Syntax Definition

**Version:** 1.0  
**Last Updated:** 2026-01-28

## Table of Contents

1. [Introduction](#introduction)
2. [Lexical Structure](#lexical-structure)
3. [Grammar Specification](#grammar-specification)
4. [Type System](#type-system)
5. [Operators](#operators)
6. [Control Flow](#control-flow)
7. [Functions](#functions)
8. [Classes and Objects](#classes-and-objects)
9. [Pattern Matching](#pattern-matching)
10. [Module System](#module-system)
11. [Error Handling](#error-handling)
12. [Asynchronous Programming](#asynchronous-programming)
13. [Standard Library](#standard-library)
14. [Complete Examples](#complete-examples)

---

## Introduction

RIFT (Rapid Integrated Framework Technology) is a modern, dynamically-typed programming language that combines the best features of PHP, JavaScript, and Python with enterprise-grade built-in capabilities. RIFT uses unique character delimiters to create a distinctive visual syntax:

- **Blocks:** `@` (open) and `#` (close) instead of `{` and `}`
- **Arrays/Lists:** `~` (open) and `!` (close) instead of `[` and `]`
- **Parentheses:** `(` and `)` remain unchanged

---

## Lexical Structure

### 2.1 Character Set

RIFT source files are encoded in UTF-8. The language uses ASCII characters with special delimiters:

- **Block delimiters:** `@` `#`
- **Array delimiters:** `~` `!`
- **Grouping delimiters:** `(` `)`

### 2.2 Comments

```rift
# Single-line comment

/* Multi-line
   comment */
```

### 2.3 Identifiers

**Syntax:**
```
identifier ::= (letter | '_') (letter | digit | '_')*
letter     ::= 'a'..'z' | 'A'..'Z'
digit      ::= '0'..'9'
```

**Examples:**
```rift
myVariable
_privateVar
userName123
```

**Rules:**
- Must start with a letter or underscore
- Can contain letters, digits, and underscores
- Case-sensitive
- Cannot be a reserved keyword

### 2.4 Keywords

RIFT reserves the following keywords:

| Category | Keywords |
|----------|----------|
| **Declarations** | `let`, `mut`, `const`, `conduit`, `make` |
| **Control Flow** | `if`, `else`, `while`, `repeat`, `check`, `when` |
| **Loop Control** | `stop`, `next` |
| **Functions** | `give`, `yield` |
| **Classes** | `build`, `extend`, `me`, `parent`, `static`, `get`, `set` |
| **Modules** | `grab`, `share`, `as` |
| **Error Handling** | `try`, `catch`, `finally`, `fail` |
| **Async** | `async`, `wait` |
| **Operators** | `and`, `or`, `not`, `in` |
| **Literals** | `yes`, `no`, `none` |

### 2.5 Literals

#### 2.5.1 Boolean Literals

```rift
yes    # true
no     # false
```

#### 2.5.2 Null Literal

```rift
none   # null/nil/undefined
```

#### 2.5.3 Numeric Literals

```rift
# Decimal integers
42
1_000_000

# Decimal floating-point
3.14159
2.5e10
1.5e-5

# Hexadecimal
0xFF
0x1A2B

# Binary
0b1010
0b1111_0000
```

#### 2.5.4 String Literals

```rift
# Single-quoted strings
'Hello, World!'
'Line 1\nLine 2'

# Double-quoted strings
"Hello, World!"
"Tab\tSeparated"

# Template strings (with interpolation)
`Hello, $@name#!`
`Result: $@x + y#`
`Nested: $@user.name.toUpper()#`
```

**Escape sequences:**
- `\n` - newline
- `\t` - tab
- `\r` - carriage return
- `\\` - backslash
- `\'` - single quote
- `\"` - double quote
- `\0` - null character

#### 2.5.5 Array Literals

```rift
~!                    # Empty array
~1, 2, 3!            # Numeric array
~"a", "b", "c"!      # String array
~1, "two", yes!      # Mixed types
~1, 2, ...rest!      # Spread operator
```

#### 2.5.6 Map Literals (Objects/Dictionaries)

```rift
@#                           # Empty map
@name: "Alice", age: 30#     # Simple map
@
    firstName: "Alice",
    lastName: "Smith",
    age: 30,
    active: yes
#

# Computed property names
@~key!: value#

# Shorthand property
let name = "Alice"
@name#  # Equivalent to @name: name#
```

### 2.6 Operators and Punctuation

**Arithmetic:** `+`, `-`, `*`, `/`, `%`, `**`  
**Comparison:** `==`, `!=`, `~`, `!`, `~=`, `!=`  
**Logical:** `and`, `or`, `not`  
**Assignment:** `=`, `+=`, `-=`, `*=`, `/=`  
**Special:** `??`, `?.`, `?~`, `-!`, `~-`, `~!`, `=!`, `::`, `..`, `...`  
**Delimiters:** `@`, `#`, `~`, `!`, `(`, `)`, `,`, `.`, `:`, `;`, `?`, `@`

---

## Grammar Specification

### 3.1 Program Structure

```bnf
program        ::= statement*

statement      ::= declaration
                 | expression_stmt
                 | control_flow
                 | block
                 | import_stmt
                 | export_stmt

block          ::= '@' statement* '#'
```

### 3.2 Declarations

```bnf
declaration    ::= var_decl
                 | const_decl
                 | function_decl
                 | class_decl

var_decl       ::= ('let' | 'mut') IDENTIFIER (':' type)? ('=' expression)? ';'?
const_decl     ::= 'const' IDENTIFIER (':' type)? '=' expression ';'?
function_decl  ::= 'conduit' IDENTIFIER '(' parameters? ')' (':' type)? block
class_decl     ::= 'make' IDENTIFIER ('extend' IDENTIFIER)? '@' class_body '#'

parameters     ::= parameter (',' parameter)*
parameter      ::= IDENTIFIER (':' type)? ('=' expression)?
```

### 3.3 Expressions

```bnf
expression     ::= assignment
assignment     ::= IDENTIFIER '=' expression
                 | pipeline
pipeline       ::= null_coalesce ('-!' null_coalesce)*
null_coalesce  ::= logical_or ('??' logical_or)*
logical_or     ::= logical_and ('or' logical_and)*
logical_and    ::= equality ('and' equality)*
equality       ::= comparison (('==' | '!=') comparison)*
comparison     ::= range (('~' | '!' | '~=' | '!=') range)*
range          ::= additive ('..' additive)?
additive       ::= multiplicative (('+' | '-') multiplicative)*
multiplicative ::= power (('*' | '/' | '%') power)*
power          ::= unary ('**' unary)*
unary          ::= ('not' | '-' | '+') unary
                 | postfix
postfix        ::= primary (call | member | index)*
call           ::= '(' arguments? ')'
member         ::= '.' IDENTIFIER
                 | '?.' IDENTIFIER
index          ::= '~' expression '!'
                 | '?~' expression '!'
primary        ::= literal
                 | IDENTIFIER
                 | '(' expression ')'
                 | lambda
                 | array_literal
                 | map_literal
```

### 3.4 Control Flow

```bnf
if_stmt        ::= 'if' expression block ('else' (if_stmt | block))?
while_stmt     ::= 'while' expression block
repeat_stmt    ::= 'repeat' pattern 'in' expression block
check_stmt     ::= 'check' expression '@' case_clause* '#'
case_clause    ::= pattern ('when' expression)? '=!' (expression | block)
```

---

## Type System

### 4.1 Built-in Types

| Type | Description | Example |
|------|-------------|---------|
| `num` | Numbers (int/float) | `42`, `3.14` |
| `text` | Strings | `"hello"` |
| `bool` | Booleans | `yes`, `no` |
| `list` | Arrays | `~1, 2, 3!` |
| `map` | Objects/Dictionaries | `@key: "value"#` |
| `none` | Null/undefined | `none` |
| `conduit` | Functions | `(x) =! x * 2` |

### 4.2 Type Annotations

Type annotations are optional and provide runtime type checking:

```rift
let name: text = "Alice"
let age: num = 30
let active: bool = yes
let items: list = ~1, 2, 3!
let user: map = @name: "Alice"#

conduit add(a: num, b: num): num @
    give a + b
#
```

### 4.3 Type Checking

RIFT performs runtime type checking when type annotations are present:

```rift
let x: num = "hello"  # Runtime error: Type mismatch
```

---

## Operators

### 5.1 Operator Precedence

From highest to lowest precedence:

| Level | Operators | Description | Associativity |
|-------|-----------|-------------|---------------|
| 1 | `()`, `~!`, `.`, `?.` | Grouping, indexing, member access | Left |
| 2 | `**` | Exponentiation | Right |
| 3 | `not`, `-`, `+` | Unary operators | Right |
| 4 | `*`, `/`, `%` | Multiplicative | Left |
| 5 | `+`, `-` | Additive | Left |
| 6 | `..` | Range | Left |
| 7 | `~`, `!`, `~=`, `!=` | Comparison | Left |
| 8 | `==`, `!=` | Equality | Left |
| 9 | `and` | Logical AND | Left |
| 10 | `or` | Logical OR | Left |
| 11 | `??` | Null coalescing | Left |
| 12 | `-!`, `~!` | Pipeline | Left |
| 13 | `=!` | Lambda arrow | Right |
| 14 | `=`, `+=`, `-=`, `*=`, `/=` | Assignment | Right |

### 5.2 Arithmetic Operators

```rift
let a = 10 + 5      # Addition: 15
let b = 10 - 5      # Subtraction: 5
let c = 10 * 5      # Multiplication: 50
let d = 10 / 5      # Division: 2
let e = 10 % 3      # Modulo: 1
let f = 2 ** 8      # Exponentiation: 256
```

### 5.3 Comparison Operators

```rift
10 == 10    # Equal: yes
10 != 5     # Not equal: yes
10 ~ 20     # Less than: yes
10 ! 5      # Greater than: yes
10 ~= 10    # Less or equal: yes
10 != 5     # Greater or equal: yes
```

### 5.4 Logical Operators

```rift
yes and no      # Logical AND: no
yes or no       # Logical OR: yes
not yes         # Logical NOT: no
```

### 5.5 Special Operators

#### Null Coalescing (`??`)

```rift
let value = maybeNull ?? "default"
```

#### Safe Navigation (`?.`)

```rift
let name = user?.profile?.name
```

#### Safe Indexing (`?~`)

```rift
let item = array?~0!
```

#### Pipeline (`-!`)

```rift
let result = data
    -! filter((x) =! x ! 10)
    -! map((x) =! x * 2)
    -! sum()
```

#### Async Pipeline (`~!`)

```rift
let result = wait fetchData()
    ~! processData
    ~! saveData
```

#### Lambda Arrow (`=!`)

```rift
let double = (x) =! x * 2
let add = (a, b) =! a + b
```

#### Static Access (`::`)

```rift
Math::PI
String::fromCharCode(65)
```

#### Range (`..`)

```rift
repeat i in 1..10 @
    print(i)
#
```

#### Spread (`...`)

```rift
let arr1 = ~1, 2, 3!
let arr2 = ~...arr1, 4, 5!  # ~1, 2, 3, 4, 5!

conduit sum(...numbers) @
    give numbers -! reduce((a, b) =! a + b, 0)
#
```

---

## Control Flow

### 6.1 If-Else Statements

```rift
if score != 90 @
    print("A")
# else if score != 80 @
    print("B")
# else if score != 70 @
    print("C")
# else @
    print("F")
#
```

### 6.2 While Loops

```rift
mut count = 0
while count ~ 10 @
    print(count)
    count = count + 1
#
```

### 6.3 Repeat Loops (For Loops)

#### Iterate over array

```rift
let items = ~"apple", "banana", "cherry"!
repeat item in items @
    print(item)
#
```

#### Iterate with index

```rift
repeat (index, item) in items @
    print(`$@index#: $@item#`)
#
```

#### Range iteration

```rift
repeat i in 1..10 @
    print(i)
#

repeat i in 0..100 @
    if i % 2 == 0 @
        print(i)
    #
#
```

### 6.4 Loop Control

```rift
repeat i in 1..100 @
    if i % 7 == 0 @
        stop  # Break out of loop
    #
    
    if i % 2 == 0 @
        next  # Continue to next iteration
    #
    
    print(i)
#
```

---

## Functions

### 7.1 Function Declaration

```rift
conduit greet(name) @
    give `Hello, $@name#!`
#

conduit add(a, b) @
    give a + b
#
```

### 7.2 Type Annotations

```rift
conduit multiply(a: num, b: num): num @
    give a * b
#
```

### 7.3 Default Parameters

```rift
conduit greet(name = "World") @
    give `Hello, $@name#!`
#

print(greet())          # "Hello, World!"
print(greet("Alice"))   # "Hello, Alice!"
```

### 7.4 Rest Parameters

```rift
conduit sum(...numbers) @
    mut total = 0
    repeat n in numbers @
        total = total + n
    #
    give total
#

print(sum(1, 2, 3, 4, 5))  # 15
```

### 7.5 Lambda Expressions

```rift
# Single expression
let double = (x) =! x * 2

# Multiple parameters
let add = (a, b) =! a + b

# No parameters
let getRandom = () =! Math.random()

# With block body
let complex = (x) =! @
    let squared = x * x
    let doubled = squared * 2
    give doubled
#
```

### 7.6 Higher-Order Functions

```rift
conduit applyTwice(fn, value) @
    give fn(fn(value))
#

let result = applyTwice((x) =! x * 2, 5)  # 20
```

### 7.7 Closures

```rift
conduit makeCounter() @
    mut count = 0
    give () =! @
        count = count + 1
        give count
    #
#

let counter = makeCounter()
print(counter())  # 1
print(counter())  # 2
print(counter())  # 3
```

---

## Classes and Objects

### 8.1 Class Declaration

```rift
make Person @
    build(name, age) @
        me.name = name
        me.age = age
    #
    
    conduit greet() @
        give `Hello, I'm $@me.name#!`
    #
    
    conduit birthday() @
        me.age = me.age + 1
    #
#
```

### 8.2 Creating Instances

```rift
let alice = Person("Alice", 30)
print(alice.greet())      # "Hello, I'm Alice!"
alice.birthday()
print(alice.age)          # 31
```

### 8.3 Inheritance

```rift
make Animal @
    build(name) @
        me.name = name
    #
    
    conduit speak() @
        give `$@me.name# makes a sound`
    #
#

make Dog extend Animal @
    build(name, breed) @
        me.name = name
        me.breed = breed
    #
    
    conduit speak() @
        give `$@me.name# barks!`
    #
    
    conduit wagTail() @
        give `$@me.name# wags tail happily`
    #
#

let dog = Dog("Buddy", "Golden Retriever")
print(dog.speak())      # "Buddy barks!"
print(dog.wagTail())    # "Buddy wags tail happily"
```

### 8.4 Static Members

```rift
make Math @
    static PI = 3.14159
    
    static conduit square(x) @
        give x * x
    #
#

print(Math::PI)           # 3.14159
print(Math::square(5))    # 25
```

### 8.5 Getters and Setters

```rift
make Rectangle @
    build(width, height) @
        me._width = width
        me._height = height
    #
    
    get area() @
        give me._width * me._height
    #
    
    set width(value) @
        if value ! 0 @
            me._width = value
        #
    #
#

let rect = Rectangle(10, 5)
print(rect.area)    # 50
rect.width = 20
print(rect.area)    # 100
```

---

## Pattern Matching

### 9.1 Basic Pattern Matching

```rift
let result = check value @
    0 =! "zero"
    1 =! "one"
    2 =! "two"
    _ =! "other"
#
```

### 9.2 Range Patterns

```rift
let grade = check score @
    90..100 =! "A"
    80..89  =! "B"
    70..79  =! "C"
    60..69  =! "D"
    _       =! "F"
#
```

### 9.3 Type Patterns

```rift
let description = check value @
    num    =! "It's a number"
    text   =! "It's a string"
    bool   =! "It's a boolean"
    list   =! "It's an array"
    map    =! "It's a map"
    _      =! "Unknown type"
#
```

### 9.4 Destructuring Patterns

```rift
let point = @x: 10, y: 20#

check point @
    @x: 0, y: 0# =! print("Origin")
    @x: x, y: 0# =! print(`On X-axis at $@x#`)
    @x: 0, y: y# =! print(`On Y-axis at $@y#`)
    @x: x, y: y# =! print(`Point at ($@x#, $@y#)`)
#
```

### 9.5 Guard Clauses

```rift
check user @
    @role: "admin"# when user.active =! handleAdmin(user)
    @role: "user"# when user.active  =! handleUser(user)
    @role: "guest"#                   =! handleGuest(user)
    _                                  =! handleInactive(user)
#
```

---

## Module System

### 10.1 Importing Modules

```rift
# Import entire module
grab http

# Import specific items
grab crypto.hash
grab crypto.hashpass

# Import with alias
grab http as web

# Import all exports
grab utils.*

# Import from relative path
grab ./helpers
grab ../config
```

### 10.2 Exporting

```rift
# Export variable
share PI = 3.14159

# Export function
share conduit add(a, b) @
    give a + b
#

# Export class
share make User @
    build(name) @
        me.name = name
    #
#

# Default export
share default conduit main() @
    print("Main function")
#
```

### 10.3 Module Example

**math.rift:**
```rift
share PI = 3.14159
share E = 2.71828

share conduit square(x) @
    give x * x
#

share conduit cube(x) @
    give x * x * x
#
```

**app.rift:**
```rift
grab math.PI
grab math.square

print(PI)           # 3.14159
print(square(5))    # 25
```

---

## Error Handling

### 11.1 Try-Catch-Finally

```rift
try @
    let result = riskyOperation()
    print(result)
# catch error @
    print(`Error occurred: $@error#`)
# finally @
    cleanup()
#
```

### 11.2 Throwing Errors

```rift
conduit divide(a, b) @
    if b == 0 @
        fail "Division by zero"
    #
    give a / b
#
```

### 11.3 Custom Error Types

```rift
make ValidationError extend Error @
    build(message, field) @
        me.message = message
        me.field = field
    #
#

conduit validateAge(age) @
    if age ~ 0 @
        fail ValidationError("Age cannot be negative", "age")
    #
    if age ! 150 @
        fail ValidationError("Age is unrealistic", "age")
    #
#
```

---

## Asynchronous Programming

### 12.1 Async Functions

```rift
async conduit fetchUser(id) @
    let response = wait http.get(`/api/users/$@id#`)
    give response.json()
#
```

### 12.2 Await

```rift
async conduit main() @
    let user = wait fetchUser(123)
    print(user.name)
#
```

### 12.3 Async Pipeline

```rift
async conduit processData() @
    let result = wait fetchData()
        ~! validateData
        ~! transformData
        ~! saveData
    
    give result
#
```

### 12.4 Promise-like Behavior

```rift
async conduit example() @
    try @
        let data = wait fetchData()
        print(data)
    # catch error @
        print(`Failed: $@error#`)
    #
#
```

---

## Standard Library

### 13.1 HTTP Module

```rift
grab http

# Define routes
http.get("/", conduit(req) @
    give http.html(200, "~h1!Hello!~/h1!")
#)

http.post("/api/users", conduit(req) @
    give http.json(201, @created: yes#)
#)

# Multi-method route
http.route("/api/items/:id", ~"GET", "PUT", "DELETE"!, conduit(req) @
    give check req.method @
        "GET" =! http.json(200, @action: "get", id: req.params.id#)
        "PUT" =! http.json(200, @action: "update", id: req.params.id#)
        "DELETE" =! http.json(204, none)
    #
#)

http.get("/api/users/:id", conduit(req) @
    let userId = req.params.id
    give http.json(200, @id: userId, name: "User"#)
#)

http.post("/api/users", conduit(req) @
    let data = req.body
    give http.json(201, @created: yes#)
#)

# Start server
http.serve(8080)
```

### 13.2 Database Module

```rift
grab db

# SQLite
let conn = db.sql("sqlite:///app.db")

# PostgreSQL
let pg = db.postgres("postgresql://user:pass@localhost/db")

# MongoDB
let mongo = db.mongo("mongodb://localhost:27017/db")

# Query builder
let users = conn.table("users")
    -> where("age", "!=", 18)
    -> order("name", "ASC")
    -> limit(10)
    -> get()

# Get single record
let user = conn.table("users")
    -> where("name", "Alice")
    -> first()

# Count records
let count = conn.table("users")
    -> where("active", yes)
    -> count()

# Insert
conn.table("users").insert(@name: "Alice", age: 30#)

# Raw SQL
conn.raw("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")

# Update
conn.table("users")
    -> where("id", 1)
    -> update(@age: 30#)

# Delete
conn.table("users")
    -> where("id", 1)
    -> delete()

# Close connection
conn.close()
```

### 13.3 Cryptography Module

```rift
grab crypto

# Hashing
let hash = crypto.hash("data")
let hash512 = crypto.hash512("data")

# Password hashing
let hashed = crypto.hashpass("password123")
let valid = crypto.checkpass("password123", hashed)

# Encryption
let encrypted = crypto.encrypt("secret data", "key")
let decrypted = crypto.decrypt(encrypted, "key")

# JWT tokens
let token = crypto.token(@userId: 123#, "secret")
let payload = crypto.verify(token, "secret")

# Random
let randomStr = crypto.random(32)
let uuid = crypto.uuid()
```

### 13.4 File System Module

```rift
grab fs

# Read/write
let content = fs.read("file.txt")
fs.write("output.txt", "Hello!")
fs.append("log.txt", "New line\n")

# File stats
let stats = fs.stat("file.txt")

# Directory operations
fs.mkdir("new_dir")
fs.rmdir("old_dir")
let files = fs.list(".")

# Path utilities
let full = fs.join("path", "to", "file.txt")
let dir = fs.dirname(full)
let name = fs.basename(full)
let ext = fs.extname(full)
```

### 13.5 JSON Module

```rift
grab json

let obj = json.parse('@"name": "Alice"#')
let str = json.stringify(@name: "Alice"#)
let pretty = json.pretty(@name: "Alice"#)
```

---

## Complete Examples

### 14.1 Hello World

```rift
let name = "World"
print(`Hello, $@name#!`)
```

### 14.2 FizzBuzz

```rift
repeat i in 1..100 @
    let output = check yes @
        yes when i % 15 == 0 =! "FizzBuzz"
        yes when i % 3 == 0  =! "Fizz"
        yes when i % 5 == 0  =! "Buzz"
        _                     =! i
    #
    print(output)
#
```

### 14.3 Fibonacci Sequence

```rift
conduit fibonacci(n) @
    if n ~= 1 @
        give n
    #
    give fibonacci(n - 1) + fibonacci(n - 2)
#

repeat i in 0..10 @
    print(fibonacci(i))
#
```

### 14.4 Web Server

```rift
grab http

let users = ~
    @id: 1, name: "Alice"#,
    @id: 2, name: "Bob"#
!

http.get("/", conduit(req) @
    give http.html(200, "~h1!Welcome to RIFT!~/h1!")
#)

http.get("/api/users", conduit(req) @
    give http.json(200, users)
#)

http.get("/api/users/:id", conduit(req) @
    let id = req.params.id -! parseInt()
    let user = users -! find((u) =! u.id == id)
    
    if user == none @
        give http.json(404, @error: "User not found"#)
    #
    
    give http.json(200, user)
#)

http.post("/api/users", conduit(req) @
    let newUser = req.body
    newUser.id = users.length + 1
    users.push(newUser)
    give http.json(201, newUser)
#)

print("Server running on http://localhost:8080")
http.serve(8080)
```

### 14.5 Class-Based Todo List

```rift
make TodoList @
    build() @
        me.todos = ~!
        me.nextId = 1
    #
    
    conduit add(title) @
        let todo = @
            id: me.nextId,
            title: title,
            completed: no
        #
        me.todos.push(todo)
        me.nextId = me.nextId + 1
        give todo
    #
    
    conduit complete(id) @
        let todo = me.todos -! find((t) =! t.id == id)
        if todo != none @
            todo.completed = yes
        #
    #
    
    conduit remove(id) @
        me.todos = me.todos -! filter((t) =! t.id != id)
    #
    
    conduit list() @
        give me.todos
    #
    
    conduit pending() @
        give me.todos -! filter((t) =! not t.completed)
    #
#

let list = TodoList()
list.add("Learn RIFT")
list.add("Build an app")
list.add("Deploy to production")

list.complete(1)

print("All todos:")
print(list.list())

print("\nPending todos:")
print(list.pending())
```

### 14.6 Async Data Processing

```rift
grab http
grab json

async conduit fetchUserData(userId) @
    let response = wait http.get(`https://api.example.com/users/$@userId#`)
    give json.parse(response.body)
#

async conduit processUsers(userIds) @
    let results = ~!
    
    repeat id in userIds @
        try @
            let user = wait fetchUserData(id)
            results.push(user)
        # catch error @
            print(`Failed to fetch user $@id#: $@error#`)
        #
    #
    
    give results
#

async conduit main() @
    let userIds = ~1, 2, 3, 4, 5!
    let users = wait processUsers(userIds)
    
    print(`Fetched $@users.length# users`)
    repeat user in users @
        print(`- $@user.name#`)
    #
#

wait main()
```

---

## Appendix A: Reserved Keywords

Complete list of reserved keywords in RIFT:

```
and, as, async, build, catch, check, conduit, const, else, extend,
fail, finally, get, give, grab, if, in, let, make, me, mut, next,
no, none, not, or, parent, repeat, set, share, static, stop, try,
wait, when, while, yield, yes
```

---

## Appendix B: Operator Summary

| Operator | Name | Example | Description |
|----------|------|---------|-------------|
| `+` | Addition | `a + b` | Add numbers or concatenate strings |
| `-` | Subtraction | `a - b` | Subtract numbers |
| `*` | Multiplication | `a * b` | Multiply numbers |
| `/` | Division | `a / b` | Divide numbers |
| `%` | Modulo | `a % b` | Remainder after division |
| `**` | Exponentiation | `a ** b` | Raise to power |
| `==` | Equal | `a == b` | Test equality |
| `!=` | Not equal | `a != b` | Test inequality |
| `~` | Less than | `a ~ b` | Compare values |
| `!` | Greater than | `a ! b` | Compare values |
| `~=` | Less or equal | `a ~= b` | Compare values |
| `!=` | Greater or equal | `a != b` | Compare values |
| `and` | Logical AND | `a and b` | Both must be true |
| `or` | Logical OR | `a or b` | At least one must be true |
| `not` | Logical NOT | `not a` | Negate boolean |
| `??` | Null coalesce | `a ?? b` | Use b if a is none |
| `?.` | Safe navigation | `obj?.prop` | Access if not none |
| `?~` | Safe index | `arr?~0!` | Index if not none |
| `-!` | Pipeline | `x -! f` | Pass x to function f |
| `~!` | Async pipeline | `x ~! f` | Async pipeline |
| `=!` | Lambda arrow | `(x) =! x` | Define lambda |
| `::` | Static access | `Class::method` | Access static member |
| `..` | Range | `1..10` | Create range |
| `...` | Spread | `...arr` | Spread elements |

---

## Appendix C: Standard Library Modules

| Module | Description |
|--------|-------------|
| `http` | HTTP server and client |
| `db` | Database connections (SQL, NoSQL) |
| `crypto` | Cryptography and hashing |
| `fs` | File system operations |
| `json` | JSON parsing and serialization |
| `math` | Mathematical functions |
| `string` | String manipulation |
| `array` | Array utilities |
| `date` | Date and time handling |
| `regex` | Regular expressions |

---

**End of RIFT Syntax Definition**
