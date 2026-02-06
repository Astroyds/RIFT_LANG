const RIFT_COMPARE_DATA = {
  tasks: [
    {
      id: 'hello',
      label: 'Hello World',
      description: 'Smallest program that prints a greeting.',
      rift: `let name = "World"
print(` + "`Hello, $@name#!`" + `)`,
      samples: {
        JavaScript: `const name = "World";
console.log(` + "`Hello, ${name}!`" + `);`,
        TypeScript: `const name: string = "World";
console.log(` + "`Hello, ${name}!`" + `);`,
        Python: `name = "World"
print(f"Hello, {name}!")`,
        Go: `package main

import "fmt"

func main() {
    name := "World"
    fmt.Printf("Hello, %s!", name)
}`,
        Rust: `fn main() {
    let name = "World";
    println!("Hello, {}!", name);
}`,
        Java: `public class Main {
    public static void main(String[] args) {
        String name = "World";
        System.out.printf("Hello, %s!", name);
    }
}`,
        "C#": `using System;

class Program {
    static void Main() {
        var name = "World";
        Console.WriteLine($"Hello, {name}!");
    }
}`,
        Ruby: `name = "World"
puts "Hello, #{name}!"`,
        PHP: `<?php
$name = "World";
echo "Hello, {$name}!";`,
        Swift: `let name = "World"
print("Hello, \(name)!")`,
        Kotlin: `fun main() {
    val name = "World"
    println("Hello, $name!")
}`,
        C: `#include <stdio.h>

int main() {
    const char *name = "World";
    printf("Hello, %s!", name);
    return 0;
}`,
        "C++": `#include <iostream>

int main() {
    std::string name = "World";
    std::cout << "Hello, " << name << "!";
    return 0;
}`,
        Lua: `local name = "World"
print("Hello, " .. name .. "!")`,
        Elixir: `name = "World"
IO.puts("Hello, #{name}!")`,
        Haskell: `main = do
    let name = "World"
    putStrLn ("Hello, " ++ name ++ "!")`
      }
    },
    {
      id: 'fizzbuzz',
      label: 'FizzBuzz',
      description: 'Branching and loop control with ranges.',
      rift: `repeat i in 1..100 @
    let output = check yes @
        yes when i % 15 == 0 =! "FizzBuzz"
        yes when i % 3 == 0  =! "Fizz"
        yes when i % 5 == 0  =! "Buzz"
        _                     =! i
    #
    print(output)
#`,
      samples: {
        JavaScript: `for (let i = 1; i <= 100; i++) {
  let output = "";
  if (i % 15 === 0) output = "FizzBuzz";
  else if (i % 3 === 0) output = "Fizz";
  else if (i % 5 === 0) output = "Buzz";
  else output = i;
  console.log(output);
}`,
        TypeScript: `for (let i = 1; i <= 100; i++) {
  let output: string | number;
  if (i % 15 === 0) output = "FizzBuzz";
  else if (i % 3 === 0) output = "Fizz";
  else if (i % 5 === 0) output = "Buzz";
  else output = i;
  console.log(output);
}`,
        Python: `for i in range(1, 101):
    if i % 15 == 0:
        print("FizzBuzz")
    elif i % 3 == 0:
        print("Fizz")
    elif i % 5 == 0:
        print("Buzz")
    else:
        print(i)`,
        Go: `package main

import "fmt"

func main() {
    for i := 1; i <= 100; i++ {
        if i%15 == 0 {
            fmt.Println("FizzBuzz")
        } else if i%3 == 0 {
            fmt.Println("Fizz")
        } else if i%5 == 0 {
            fmt.Println("Buzz")
        } else {
            fmt.Println(i)
        }
    }
}`,
        Rust: `fn main() {
    for i in 1..=100 {
        if i % 15 == 0 {
            println!("FizzBuzz");
        } else if i % 3 == 0 {
            println!("Fizz");
        } else if i % 5 == 0 {
            println!("Buzz");
        } else {
            println!("{}", i);
        }
    }
}`,
        Java: `public class Main {
    public static void main(String[] args) {
        for (int i = 1; i <= 100; i++) {
            if (i % 15 == 0) {
                System.out.println("FizzBuzz");
            } else if (i % 3 == 0) {
                System.out.println("Fizz");
            } else if (i % 5 == 0) {
                System.out.println("Buzz");
            } else {
                System.out.println(i);
            }
        }
    }
}`,
        "C#": `using System;

class Program {
    static void Main() {
        for (int i = 1; i <= 100; i++) {
            if (i % 15 == 0) Console.WriteLine("FizzBuzz");
            else if (i % 3 == 0) Console.WriteLine("Fizz");
            else if (i % 5 == 0) Console.WriteLine("Buzz");
            else Console.WriteLine(i);
        }
    }
}`,
        Ruby: `for i in 1..100
  if i % 15 == 0
    puts "FizzBuzz"
  elsif i % 3 == 0
    puts "Fizz"
  elsif i % 5 == 0
    puts "Buzz"
  else
    puts i
  end
end`,
        PHP: `<?php
for ($i = 1; $i <= 100; $i++) {
    if ($i % 15 == 0) {
        echo "FizzBuzz\n";
    } elseif ($i % 3 == 0) {
        echo "Fizz\n";
    } elseif ($i % 5 == 0) {
        echo "Buzz\n";
    } else {
        echo $i . "\n";
    }
}`,
        Swift: `for i in 1...100 {
    if i % 15 == 0 {
        print("FizzBuzz")
    } else if i % 3 == 0 {
        print("Fizz")
    } else if i % 5 == 0 {
        print("Buzz")
    } else {
        print(i)
    }
}`,
        Kotlin: `fun main() {
    for (i in 1..100) {
        when {
            i % 15 == 0 -> println("FizzBuzz")
            i % 3 == 0 -> println("Fizz")
            i % 5 == 0 -> println("Buzz")
            else -> println(i)
        }
    }
}`,
        C: `#include <stdio.h>

int main() {
    for (int i = 1; i <= 100; i++) {
        if (i % 15 == 0) printf("FizzBuzz\n");
        else if (i % 3 == 0) printf("Fizz\n");
        else if (i % 5 == 0) printf("Buzz\n");
        else printf("%d\n", i);
    }
    return 0;
}`,
        "C++": `#include <iostream>

int main() {
    for (int i = 1; i <= 100; i++) {
        if (i % 15 == 0) std::cout << "FizzBuzz\n";
        else if (i % 3 == 0) std::cout << "Fizz\n";
        else if (i % 5 == 0) std::cout << "Buzz\n";
        else std::cout << i << "\n";
    }
    return 0;
}`,
        Lua: `for i = 1, 100 do
  if i % 15 == 0 then
    print("FizzBuzz")
  elseif i % 3 == 0 then
    print("Fizz")
  elseif i % 5 == 0 then
    print("Buzz")
  else
    print(i)
  end
end`,
        Elixir: `Enum.each(1..100, fn i ->
  cond do
    rem(i, 15) == 0 -> IO.puts("FizzBuzz")
    rem(i, 3) == 0 -> IO.puts("Fizz")
    rem(i, 5) == 0 -> IO.puts("Buzz")
    true -> IO.puts(i)
  end
end)`,
        Haskell: `main = mapM_ putStrLn [fizz i | i <- [1..100]]

fizz i
  | i ` + "`mod`" + ` 15 == 0 = "FizzBuzz"
  | i ` + "`mod`" + ` 3 == 0 = "Fizz"
  | i ` + "`mod`" + ` 5 == 0 = "Buzz"
  | otherwise = show i`
      }
    },
    {
      id: 'pipeline',
      label: 'Array Pipeline',
      description: 'Filter and map a list of records.',
      rift: `let users = ~
    @id: 1, name: "Ava", active: yes#,
    @id: 2, name: "Jun", active: no#,
    @id: 3, name: "Li", active: yes#
!

let active = users
    -! filter((u) =! u.active == yes)
    -! map((u) =! u.name)

print(active)`,
      samples: {
        JavaScript: `const users = [
  { id: 1, name: "Ava", active: true },
  { id: 2, name: "Jun", active: false },
  { id: 3, name: "Li", active: true }
];

const active = users
  .filter((u) => u.active)
  .map((u) => u.name);

console.log(active);`,
        TypeScript: `type User = { id: number; name: string; active: boolean };

const users: User[] = [
  { id: 1, name: "Ava", active: true },
  { id: 2, name: "Jun", active: false },
  { id: 3, name: "Li", active: true }
];

const active = users
  .filter((u) => u.active)
  .map((u) => u.name);

console.log(active);`,
        Python: `users = [
    {"id": 1, "name": "Ava", "active": True},
    {"id": 2, "name": "Jun", "active": False},
    {"id": 3, "name": "Li", "active": True},
]

active = [u["name"] for u in users if u["active"]]
print(active)`,
        Go: `package main

import "fmt"

type User struct {
    ID     int
    Name   string
    Active bool
}

func main() {
    users := []User{
        {ID: 1, Name: "Ava", Active: true},
        {ID: 2, Name: "Jun", Active: false},
        {ID: 3, Name: "Li", Active: true},
    }

    active := []string{}
    for _, u := range users {
        if u.Active {
            active = append(active, u.Name)
        }
    }

    fmt.Println(active)
}`,
        Rust: `#[derive(Debug)]
struct User {
    id: i32,
    name: &'static str,
    active: bool,
}

fn main() {
    let users = vec![
        User { id: 1, name: "Ava", active: true },
        User { id: 2, name: "Jun", active: false },
        User { id: 3, name: "Li", active: true },
    ];

    let active: Vec<&str> = users
        .iter()
        .filter(|u| u.active)
        .map(|u| u.name)
        .collect();

    println!("{:?}", active);
}`,
        Java: `import java.util.List;
import java.util.stream.Collectors;

record User(int id, String name, boolean active) {}

public class Main {
    public static void main(String[] args) {
        List<User> users = List.of(
            new User(1, "Ava", true),
            new User(2, "Jun", false),
            new User(3, "Li", true)
        );

        List<String> active = users.stream()
            .filter(User::active)
            .map(User::name)
            .collect(Collectors.toList());

        System.out.println(active);
    }
}`,
        "C#": `using System;
using System.Collections.Generic;
using System.Linq;

record User(int Id, string Name, bool Active);

class Program {
    static void Main() {
        var users = new List<User> {
            new(1, "Ava", true),
            new(2, "Jun", false),
            new(3, "Li", true)
        };

        var active = users
            .Where(u => u.Active)
            .Select(u => u.Name)
            .ToList();

        Console.WriteLine(string.Join(", ", active));
    }
}`,
        Ruby: `users = [
  { id: 1, name: "Ava", active: true },
  { id: 2, name: "Jun", active: false },
  { id: 3, name: "Li", active: true }
]

active = users.select { |u| u[:active] }.map { |u| u[:name] }
puts active.join(", ")`,
        PHP: `<?php
$users = [
  ["id" => 1, "name" => "Ava", "active" => true],
  ["id" => 2, "name" => "Jun", "active" => false],
  ["id" => 3, "name" => "Li", "active" => true],
];

$active = array_map(
  fn($u) => $u["name"],
  array_filter($users, fn($u) => $u["active"])
);

echo implode(", ", $active);`,
        Swift: `struct User {
    let id: Int
    let name: String
    let active: Bool
}

let users = [
    User(id: 1, name: "Ava", active: true),
    User(id: 2, name: "Jun", active: false),
    User(id: 3, name: "Li", active: true)
]

let active = users.filter { $0.active }.map { $0.name }
print(active)`,
        Kotlin: `data class User(val id: Int, val name: String, val active: Boolean)

fun main() {
    val users = listOf(
        User(1, "Ava", true),
        User(2, "Jun", false),
        User(3, "Li", true)
    )

    val active = users.filter { it.active }.map { it.name }
    println(active)
}`,
        C: `#include <stdio.h>

int main() {
    const char *names[] = {"Ava", "Jun", "Li"};
    int active[] = {1, 0, 1};

    printf("[");
    for (int i = 0; i < 3; i++) {
        if (active[i]) {
            printf("%s", names[i]);
        }
        if (i < 2) {
            printf(", ");
        }
    }
    printf("]\n");
    return 0;
}`,
        "C++": `#include <iostream>
#include <vector>

struct User {
    int id;
    std::string name;
    bool active;
};

int main() {
    std::vector<User> users = {
        {1, "Ava", true},
        {2, "Jun", false},
        {3, "Li", true}
    };

    std::vector<std::string> active;
    for (const auto &u : users) {
        if (u.active) active.push_back(u.name);
    }

    for (const auto &name : active) {
        std::cout << name << " ";
    }
    std::cout << std::endl;
    return 0;
}`,
        Lua: `local users = {
  { id = 1, name = "Ava", active = true },
  { id = 2, name = "Jun", active = false },
  { id = 3, name = "Li", active = true }
}

local active = {}
for _, u in ipairs(users) do
  if u.active then
    table.insert(active, u.name)
  end
end

print(table.concat(active, ", "))`,
        Elixir: `users = [
  %{id: 1, name: "Ava", active: true},
  %{id: 2, name: "Jun", active: false},
  %{id: 3, name: "Li", active: true}
]

active = users |> Enum.filter(& &1.active) |> Enum.map(& &1.name)
IO.inspect(active)`,
        Haskell: `data User = User { name :: String, active :: Bool }

main = do
  let users = [User "Ava" True, User "Jun" False, User "Li" True]
  let activeNames = [name u | u <- users, active u]
  print activeNames`
      }
    }
  ],
  languages: [
    "JavaScript",
    "TypeScript",
    "Python",
    "Go",
    "Rust",
    "Java",
    "C#",
    "Ruby",
    "PHP",
    "Swift",
    "Kotlin",
    "C",
    "C++",
    "Lua",
    "Elixir",
    "Haskell"
  ]
};
