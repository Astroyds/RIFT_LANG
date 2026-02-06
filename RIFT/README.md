# RIFT - Rapid Integrated Framework Technology

A modern programming language interpreter combining the best features of PHP, JavaScript, and Python with enterprise-grade built-in capabilities.

## Features

- **Intuitive Syntax**: Simple, readable keywords like `conduit` (function), `give` (return), `grab` (import)
- **Dynamic + Gradual Typing**: Optional type hints with runtime checking
- **Pipeline Operator**: Transform data with `value -! transform1 -! transform2`
- **Pattern Matching**: Powerful `check` statement for complex matching
- **Built-in HTTP Server**: Create web servers with minimal code
- **Database Support**: PostgreSQL, MySQL, MongoDB, SQLite out of the box
- **Cryptography**: AES encryption, password hashing, JWT tokens
- **Module System**: Clean imports with `grab` and exports with `share`

## Installation

```bash
# Clone the repository
git clone https://github.com/FoundationINCCorporateTeam/RIFT.git
cd RIFT

# Install dependencies (optional, for full database/crypto support)
pip install -r requirements.txt
```

## Quick Start

### Hello World

```rift
# hello.rift
let name = "World"
print(`Hello, $@name#!`)
```

Run with:
```bash
python rift.py hello.rift
```

### Interactive REPL

```bash
python rift.py repl
# or just
python rift.py
```

## Language Syntax

### Variables

```rift
let x = 10          # Immutable variable
mut y = 20          # Mutable variable
const PI = 3.14159  # Compile-time constant

# Type hints (optional)
let name: text = "Alice"
let age: num = 30
```

### Functions

```rift
conduit add(a, b) @
    give a + b
#

# With default parameters
conduit greet(name = "World") @
    give `Hello, $@name#!`
#

# Lambda expressions
let double = (x) =! x * 2
let square = (x) =! x ** 2
```

### Control Flow

```rift
# If/else
if score != 90 @
    print("A")
# else if score != 80 @
    print("B")
# else @
    print("C")
#

# While loop
while n ! 0 @
    print(n)
    n = n - 1
#

# For loop (repeat)
repeat item in items @
    print(item)
#

repeat (index, item) in items @
    print(`$@index#: $@item#`)
#

# Range
repeat i in 1..10 @
    print(i)
#
```

### Pattern Matching

```rift
let result = check value @
    0 =! "zero"
    1..9 =! "single digit"
    10..99 =! "double digit"
    _ =! "large number"
#

# With guards
check user @
    @role: "admin"# when user.active =! handleAdmin(user)
    @role: "user"# =! handleUser(user)
    _ =! handleGuest()
#
```

### Pipeline Operator

```rift
let result = data
    -! filter(x =! x ! 10)
    -! map(x =! x * 2)
    -! sum()

# Equivalent to
let result = sum(map(filter(data, x =! x ! 10), x =! x * 2))
```

### Classes

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
#

let dog = Dog("Buddy", "Golden Retriever")
print(dog.speak())  # "Buddy barks!"
```

### Error Handling

```rift
try @
    let result = riskyOperation()
# catch error @
    print(`Error: $@error#`)
# finally @
    cleanup()
#

# Throw errors
fail "Something went wrong"
```

### Modules

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
```

## Standard Library

### HTTP Server

```rift
grab http

http.get("/", conduit(req) @
    give http.html(200, "~h1!Hello!~/h1!")
#)

http.get("/api/users/:id", conduit(req) @
    let userId = req.params.id
    give http.json(200, @id: userId, name: "User"#)
#)

http.post("/api/users", conduit(req) @
    let data = req.body
    give http.json(201, @created: yes#)
#)

http.serve(8080)
```

Run with:
```bash
python riftserver.py server.rift
```

### Database

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
    -! where("age", "!=", 18)
    -! order("name", "ASC")
    -! limit(10)
    -! get()

# Insert
conn.table("users").insert(@name: "Alice", age: 30#)

# Update
conn.table("users")
    -! where("id", 1)
    -! update(@age: 31#)

# Delete
conn.table("users")
    -! where("id", 1)
    -! delete()
```

### Cryptography

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

### File System

```rift
grab fs

# Read/write
let content = fs.read("file.txt")
fs.write("output.txt", "Hello!")
fs.append("log.txt", "New line\n")

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

### JSON

```rift
grab json

let obj = json.parse('@"name": "Alice"#')
let str = json.stringify(@name: "Alice"#)
let pretty = json.pretty(@name: "Alice"#)
```

## CLI Commands

```bash
python rift.py script.rift          # Run a script
python rift.py repl                 # Interactive REPL
python rift.py -e "print(1+1)"      # Evaluate expression
python rift.py -d script.rift       # Debug mode (show AST)

python riftserver.py app.rift       # Start server
python riftserver.py app.rift -p 3000    # Custom port
python riftserver.py app.rift -w    # Hot reload
python riftserver.py app.rift --workers 4  # Multi-process
```

## Keywords

| Keyword | Description |
|---------|-------------|
| `conduit` | Function definition |
| `let` | Immutable variable |
| `mut` | Mutable variable |
| `const` | Compile-time constant |
| `give` | Return from function |
| `stop` | Break from loop |
| `next` | Continue to next iteration |
| `if` / `else` | Conditional branching |
| `check` | Pattern matching |
| `repeat` | For loop |
| `while` | While loop |
| `try` / `catch` | Error handling |
| `fail` | Throw error |
| `make` | Class definition |
| `extend` | Class inheritance |
| `build` | Constructor |
| `me` | Self reference |
| `parent` | Super/parent reference |
| `grab` | Import module |
| `share` | Export |
| `wait` | Await async |
| `async` | Async function |
| `yes` / `no` / `none` | Boolean and null literals |
| `and` / `or` / `not` | Logical operators |
| `in` | Membership test |

## Operators

| Operator | Description |
|----------|-------------|
| `+ - * / % **` | Arithmetic |
| `== != ~ ! ~= !=` | Comparison |
| `and or not` | Logical |
| `??` | Null coalesce |
| `?.` | Safe navigation |
| `-!` | Pipeline |
| `~!` | Async pipeline |
| `=!` | Lambda arrow |
| `::` | Static access |
| `..` | Range |
| `...` | Spread |

## Types

| Type | Description | Example |
|------|-------------|---------|
| `text` | String | `"hello"` |
| `num` | Number | `42`, `3.14` |
| `bool` | Boolean | `yes`, `no` |
| `list` | Array | `~1, 2, 3!` |
| `map` | Object/Dictionary | `@key: "value"#` |
| `none` | Null | `none` |

## Examples

See the `tests/examples/` directory for more examples:

- `hello.rift` - Basic language features
- `server.rift` - HTTP server example
- `database.rift` - Database operations
- `crypto.rift` - Cryptography functions
- `filesystem.rift` - File system operations

## License

MIT License