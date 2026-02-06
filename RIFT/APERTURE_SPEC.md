# Aperture UI Framework Specification

**Version:** 1.0  
**Last Updated:** 2026-02-01  
**Layer:** Surface (UI Layer of RIFT)

---

## Table of Contents

1. [Philosophy](#philosophy)
2. [Component Structure](#component-structure)
3. [The RX Syntax (Rift XML)](#the-rx-syntax-rift-xml)
4. [State Management (The Focus System)](#state-management-the-focus-system)
5. [Event Handling](#event-handling)
6. [Conditionals & Lists in UI](#conditionals--lists-in-ui)
7. [Complete Code Examples](#complete-code-examples)

---

## Philosophy

### The Surface Layer of RIFT

Aperture represents the **Surface** layer of the RIFT ecosystem - the visual interface through which users interact with applications. Just as a geological aperture allows light to pass through rock layers, Aperture provides openings for data to flow from the core RIFT logic to the user's visual field.

**Core Principles:**

1. **Light & Clarity:** Components should be transparent in their purpose and behavior
2. **Reactive Surfaces:** UI elements respond instantly to state changes, like light refracting through crystal
3. **Geometric Precision:** Every component has well-defined boundaries and clear interfaces
4. **Optical Focus:** State management follows the metaphor of focusing and refocusing visual attention

**The RX (Rift XML) Innovation:**

RIFT's unique character allocation (`~` for less than, `!` for greater than) frees the traditional angle brackets `<` and `>` for a JSX-like syntax. This allows HTML-like structures to coexist naturally within RIFT code blocks, creating a seamless blend of logic and presentation.

---

## Component Structure

### Functional Components with Conduits

Aperture components are declared using RIFT's `conduit` keyword, treating UI elements as pure functions that transform props into visual output.

```rift
# Basic component structure
conduit ComponentName(props) @
    give <div @class="component-class">
        $@props.content#
    </div>
#
```

### Props System

Props are passed as standard RIFT function arguments, following the same patterns as regular conduits:

```rift
# With destructured props
conduit UserProfile(@name, @avatar, @role#) @
    give <div @class="user-profile">
        <img @src="$@avatar#" @alt="$@name#"/>
        <h2>$@name#</h2>
        <span @class="role">$@role#</span>
    </div>
#

# With default values
conduit Button(@text = "Click", @variant = "primary"#) @
    give <button @class="btn btn-$@variant#">
        $@text#
    </button>
#
```

### Component Composition

Components can be nested and composed naturally:

```rift
conduit App() @
    give <div @class="app">
        <Header @title="My App"/>
        <main>
            <UserProfile @name="Alice" @avatar="/avatar.jpg" @role="Developer"/>
            <Button @text="Get Started" @variant="secondary"/>
        </main>
    </div>
#
```

---

## The RX Syntax (Rift XML)

### HTML Tags in RIFT

RX allows standard HTML tags to be written directly within RIFT code blocks using the freed `<` and `>` characters:

```rift
conduit Navigation() @
    give <nav @class="navbar">
        <div @class="nav-brand">
            <h1>RIFT App</h1>
        </div>
        <ul @class="nav-menu">
            <li><a @href="/home">Home</a></li>
            <li><a @href="/about">About</a></li>
            <li><a @href="/contact">Contact</a></li>
        </ul>
    </nav>
#
```

### Attribute Syntax

Attributes use the `@` prefix to distinguish them from RIFT variables:

```rift
<div @class="container" @id="main-content" @data-user-id="$@userId#">
    <input @type="text" @placeholder="Enter name..." @value="$@inputValue#"/>
</div>
```

### Variable Interpolation in RX

RIFT's template string interpolation `$@variable#` works seamlessly within RX:

```rift
conduit Greeting(@name#) @
    give <div @class="greeting">
        <h1>Welcome, $@name#!</h1>
        <p>Today is $@currentDate#</p>
    </div>
#
```

### Self-Closing Tags

Standard HTML self-closing syntax is supported:

```rift
<img @src="$@imagePath#" @alt="Description"/>
<input @type="email" @placeholder="email@example.com"/>
<br/>
<hr/>
```

### Fragment Syntax

For multiple root elements, use fragments:

```rift
conduit TableRows(@data#) @
    give <>
        repeat item in @data @
            <tr @key="$@item.id#">
                <td>$@item.name#</td>
                <td>$@item.email#</td>
            </tr>
        #
    </>
#
```

---

## State Management (The Focus System)

### The Optical Metaphor

State management in Aperture follows the metaphor of optical focus - components can "focus" on specific data points and "refocus" when those points change.

### useFocus Hook

The primary state hook is `useFocus`, which creates a reactive state variable:

```rift
conduit Counter() @
    let @count, setCount = useFocus(0)
    
    give <div @class="counter">
        <h2>Count: $@count#</h2>
        <button @onClick="() =! setCount(@count + 1)">
            Increment
        </button>
        <button @onClick="() =! setCount(@count - 1)">
            Decrement
        </button>
    </div>
#
```

### useView Hook

For derived state that depends on other state or props:

```rift
conduit ShoppingCart(@items#) @
    let @items, setItems = useFocus(@items)
    let @total = useView(() =! @
        mut sum = 0
        repeat item in @items @
            sum = sum + (item.price * item.quantity)
        #
        give sum
    #)
    
    give <div @class="cart">
        <h3>Total: $$@total#</h3>
        repeat item in @items @
            <CartItem @item=item @key="$@item.id#"/>
        #
    </div>
#
```

### useTrack Hook

For tracking side effects and external data sources:

```rift
conduit DataComponent(@url#) @
    let @data, setData = useFocus(none)
    let @loading, setLoading = useFocus(yes)
    
    useTrack(() =! @
        async @
            try @
                let response = wait fetch(@url)
                let result = wait response.json()
                setData(result)
            catch error @
                print(`Error: $@error#`)
            #
            setLoading(no)
        #
    #, ~@url#!)
    
    give <div @class="data-component">
        check @loading @
            yes =! <div>Loading...</div>
            no =! check @data @
                none =! <div>No data available</div>
                _ =! <DataDisplay @data=@data/>
            #
        #
    </div>
#
```

---

## Event Handling

### Event Attribute Syntax

Events use the `on` prefix followed by the event name, with camelCase for multi-word events:

```rift
<button @onClick="handleClick">
    Click me
</button>

<input @onChange="handleChange" @value="$@value#"/>
<form @onSubmit="handleSubmit">
    <input @type="text" @onFocus="handleFocus" @onBlur="handleBlur"/>
</form>
```

### Event Handler Functions

Event handlers are standard RIFT conduits:

```rift
conduit FormComponent() @
    let @formData, setFormData = useFocus(@name: "", email: ""#)
    
    conduit handleChange(event) @
        let @name, @value = event.target
        setFormData(@...@formData, ~@name: @value#!)
    #
    
    conduit handleSubmit(event) @
        event.preventDefault()
        print(`Form submitted: $@json.stringify(@formData)#`)
    #
    
    give <form @onSubmit="handleSubmit">
        <input 
            @type="text" 
            @name="name" 
            @value="$@formData.name#" 
            @onChange="handleChange"
            @placeholder="Name"
        />
        <input 
            @type="email" 
            @name="email" 
            @value="$@formData.email#" 
            @onChange="handleChange"
            @placeholder="Email"
        />
        <button @type="submit">Submit</button>
    </form>
#
```

### Event Object Structure

Event objects follow standard web event patterns:

```rift
conduit ClickHandler(event) @
    # Mouse events
    print(`Clicked at: $@event.clientX#, $@event.clientY#`)
    print(`Button: $@event.button#`)
    print(`Target: $@event.target.tagName#`)
    
    # Keyboard events
    print(`Key: $@event.key#`)
    print(`Code: $@event.code#`)
    print(`Ctrl: $@event.ctrlKey#`)
#
```

---

## Conditionals & Lists in UI

### Conditional Rendering with RIFT's check

Use RIFT's pattern matching for conditional rendering:

```rift
conduit StatusDisplay(@status#) @
    give <div @class="status">
        check @status @
            "loading" =! <div @class="loading-indicator">Loading...</div>
            "success" =! <div @class="success-message">✓ Operation completed</div>
            "error" =! <div @class="error-message">✗ Error occurred</div>
            _ =! <div @class="unknown-status">Unknown status</div>
        #
    </div>
#
```

### If-Else Conditional Rendering

For simple conditions, use RIFT's if-else:

```rift
conduit UserGreeting(@user#) @
    give <div @class="greeting">
        if @user @
            give <h2>Welcome back, $@user.name#!</h2>
        else @
            give <h2>Please sign in</h2>
        #
    </div>
#
```

### List Rendering with repeat

Use RIFT's repeat loop for rendering lists:

```rift
conduit TodoList(@items#) @
    give <div @class="todo-list">
        <h3>Tasks ($@len(@items)# total)</h3>
        <ul>
            repeat item in @items @
                <li @key="$@item.id#" @class="todo-item">
                    <input 
                        @type="checkbox" 
                        @checked="$@item.completed#" 
                        @onChange="() =! toggleItem(@item.id)"
                    />
                    <span @class="$@item.completed ? 'completed' : ''#">
                        $@item.text#
                    </span>
                    <button @onClick="() =! deleteItem(@item.id)">
                        Delete
                    </button>
                </li>
            #
        </ul>
    </div>
#
```

### Dynamic Lists with useFocus

Combine state management with list rendering:

```rift
conduit DynamicList() @
    let @items, setItems = useFocus(~"Item 1", "Item 2", "Item 3"!)
    let @newItem, setNewItem = useFocus("")
    
    conduit addItem() @
        if @newItem @
            setItems(~...@items, @newItem#!)
            setNewItem("")
        #
    #
    
    conduit removeItem(index) @
        setItems(@items -> filter((_, i) =! i != index))
    #
    
    give <div @class="dynamic-list">
        <div @class="input-group">
            <input 
                @type="text" 
                @value="$@newItem#" 
                @onChange="(e) =! setNewItem(e.target.value)"
                @placeholder="Add new item"
            />
            <button @onClick="addItem" @disabled="not @newItem">
                Add
            </button>
        </div>
        
        <ul @class="item-list">
            repeat item in @items with index @
                <li @key="$@index#">
                    <span>$@item#</span>
                    <button @onClick="() =! removeItem(@index)">
                        Remove
                    </button>
                </li>
            #
        </ul>
    </div>
#
```

---

## Complete Code Examples

### Example 1: The Prism Counter

A simple counter component that demonstrates state management and event handling:

```rift
/* Prism Counter - Demonstrates basic state and events */
grab aperture

conduit PrismCounter() @
    let @count, setCount = useFocus(0)
    let @color, setColor = useFocus("blue")
    
    # Color cycling based on count
    useTrack(() =! @
        let colors = ~"blue", "green", "purple", "orange", "red"!
        let colorIndex = @count % len(colors)
        setColor(colors~colorIndex!)
    #, ~@count#!)
    
    conduit increment() @
        setCount(@count + 1)
    #
    
    conduit decrement() @
        setCount(@count - 1)
    #
    
    conduit reset() @
        setCount(0)
    #
    
    give <div @class="prism-counter" @style="border-color: $@color#">
        <div @class="display">
            <h2 @style="color: $@color#">$@count#</h2>
            <p @class="label">Prism Count</p>
        </div>
        
        <div @class="controls">
            <button 
                @onClick="decrement" 
                @class="btn decrement"
                @disabled="$@count <= 0#"
            >
                −
            </button>
            
            <button 
                @onClick="reset" 
                @class="btn reset"
                @disabled="$@count == 0#"
            >
                ⟲
            </button>
            
            <button 
                @onClick="increment" 
                @class="btn increment"
            >
                +
            </button>
        </div>
        
        <div @class="info">
            <small>Color changes with count (Optical Focus Demo)</small>
        </div>
    </div>
#

# CSS would be defined separately or via styled-components
```

### Example 2: User Profile Card

A component that accepts props and displays user information with conditional rendering:

```rift
/* User Profile Card - Props and conditional rendering */
grab aperture

conduit UserProfileCard(@user, @showDetails = yes#) @
    let @isExpanded, setIsExpanded = useFocus(no)
    
    conduit toggleDetails() @
        setIsExpanded(not @isExpanded)
    #
    
    conduit getInitials(name) @
        let parts = name -> split(" ")
        give parts 
            -> map((part) =! part~0!)
            -> join("")
            -> toUpper()
    #
    
    give <div @class="user-card">
        <div @class="header">
            check @user.avatar @
                some => <img @src="$@user.avatar#" @alt="$@user.name#" @class="avatar"/>
                none => <div @class="avatar-placeholder">$@getInitials(@user.name)#</div>
            #
            
            <div @class="user-info">
                <h3 @class="name">$@user.name#</h3>
                <p @class="title">$@user.title#</p>
            </div>
        </div>
        
        if @showDetails @
            give <div @class="details">
                <div @class="detail-row">
                    <span @class="label">Department:</span>
                    <span @class="value">$@user.department#</span>
                </div>
                
                <div @class="detail-row">
                    <span @class="label">Email:</span>
                    <a @href="mailto:$@user.email#" @class="value">$@user.email#</a>
                </div>
                
                if @user.phone @
                    give <div @class="detail-row">
                        <span @class="label">Phone:</span>
                        <a @href="tel:$@user.phone#" @class="value">$@user.phone#</a>
                    </div>
                #
                
                <div @class="detail-row">
                    <span @class="label">Status:</span>
                    <span @class="status $@user.status#">$@user.status#</span>
                </div>
                
                if @isExpanded and @user.bio @
                    give <div @class="bio">
                        <p>$@user.bio#</p>
                    </div>
                #
                
                <button 
                    @onClick="toggleDetails" 
                    @class="toggle-btn"
                    @disabled="not @user.bio"
                >
                    $@isExpanded ? "Show Less" : "Show More"#
                </button>
            </div>
        #
    </div>
#

# Usage example
conduit TeamPage() @
    let @team = useFocus(~
        @
            name: "Dr. Sarah Chen",
            title: "Lead Geologist",
            department: "Research",
            email: "sarah.chen@rift.dev",
            phone: "+1-555-0123",
            status: "active",
            bio: "Specializing in crystal formations and mineral analysis with 15 years of experience.",
            avatar: "/avatars/sarah.jpg"
        #,
        @
            name: "Marcus Rodriguez",
            title: "UI Engineer",
            department: "Development",
            email: "marcus.r@rift.dev",
            status: "active",
            bio: "Passionate about creating intuitive interfaces that bridge data and user experience."
        #
    !)
    
    give <div @class="team-page">
        <h1>Our Team</h1>
        <div @class="team-grid">
            repeat member in @team @
                <UserProfileCard 
                    @user=member 
                    @showDetails=yes 
                    @key="$@member.email#"
                />
            #
        </div>
    </div>
#
```

### Example 3: Data Grid

A data grid component that fetches data asynchronously and renders it with sorting and filtering:

```rift
/* Data Grid - Async data fetching with sorting and filtering */
grab aperture
grab json

conduit DataGrid(@url, @columns#) @
    let @data, setData = useFocus(~!)
    let @loading, setLoading = useFocus(yes)
    let @error, setError = useFocus(none)
    let @sortConfig, setSortConfig = useFocus(@key: none, direction: "asc"#)
    let @filterText, setFilterText = useFocus("")
    let @selectedRows, setSelectedRows = useFocus(~!)
    
    # Fetch data when URL changes
    useTrack(() =! @
        async @
            try @
                setLoading(yes)
                setError(none)
                
                let response = wait fetch(@url)
                if not response.ok @
                    fail "Network response was not ok"
                #
                
                let result = wait response.json()
                setData(result.data or result)
            catch err @
                setError(err.message or "Failed to fetch data")
            #
            setLoading(no)
        #
    #, ~@url#!)
    
    # Sorting logic
    conduit handleSort(key) @
        let direction = check @sortConfig.key == key @
            "asc" =! "desc"
            "desc" =! "asc"
            _ =! "asc"
        #
        setSortConfig(@key: key, direction: direction#)
    #
    
    # Filter and sort data
    let @processedData = useView(() =! @
        let filtered = @filterText 
            ? @data -> filter((row) =! @
                @columns -> some((col) =! @
                    let value = row~col.key!
                    value and value -> toString() -> toLower() -> includes(@filterText -> toLower())
                #)
            #)
            : @data
        
        if @sortConfig.key @
            give filtered -> sort((a, b) =! @
                let aVal = a~@sortConfig.key!
                let bVal = b~@sortConfig.key!
                
                let comparison = check aVal and bVal @
                    _ when aVal > bVal =! 1
                    _ when aVal < bVal =! -1
                    _ =! 0
                #
                
                give @sortConfig.direction == "desc" ? -comparison : comparison
            #)
        else @
            give filtered
        #
    #)
    
    # Row selection
    conduit toggleRowSelection(id) @
        setSelectedRows(
            @selectedRows -> includes(id)
                ? @selectedRows -> filter((rowId) =! rowId != id)
                : ~...@selectedRows, id!
        )
    #
    
    conduit selectAll() @
        if @selectedRows -> length == @processedData -> length @
            setSelectedRows(~!)
        else @
            setSelectedRows(@processedData -> map((row) =! row.id))
        #
    #
    
    give <div @class="data-grid">
        <div @class="grid-header">
            <h2>Data Grid</h2>
            <div @class="controls">
                <input 
                    @type="text" 
                    @placeholder="Filter data..." 
                    @value="$@filterText#"
                    @onChange="(e) =! setFilterText(e.target.value)"
                    @class="filter-input"
                />
                <button 
                    @onClick="selectAll" 
                    @class="select-all-btn"
                    @disabled="@processedData -> length == 0"
                >
                    $@selectedRows -> length == @processedData -> length ? "Deselect All" : "Select All"#
                </button>
            </div>
        </div>
        
        <div @class="grid-content">
            check @loading @
                yes =! <div @class="loading">Loading data...</div>
                no =! check @error @
                    some => <div @class="error">Error: $@error#</div>
                    none => check @processedData -> length @
                        0 => <div @class="no-data">No data available</div>
                        _ => <div @class="table-wrapper">
                            <table @class="data-table">
                                <thead>
                                    <tr>
                                        <th @class="select-column">
                                            <input 
                                                @type="checkbox" 
                                                @checked="$@selectedRows -> length > 0 and @selectedRows -> length == @processedData -> length#"
                                                @onChange="selectAll"
                                            />
                                        </th>
                                        repeat column in @columns @
                                            <th 
                                                @key="$@column.key#"
                                                @onClick="() =! handleSort(@column.key)"
                                                @class="$@sortConfig.key == @column.key ? 'sorted ' + @sortConfig.direction : ''#"
                                            >
                                                $@column.title#
                                                if @sortConfig.key == @column.key @
                                                    give <span @class="sort-indicator">
                                                        $@sortConfig.direction == "asc" ? "↑" : "↓"#
                                                    </span>
                                                #
                                            </th>
                                        #
                                    </tr>
                                </thead>
                                <tbody>
                                    repeat row in @processedData @
                                        <tr 
                                            @key="$@row.id#" 
                                            @class="$@selectedRows -> includes(@row.id) ? 'selected' : ''#"
                                        >
                                            <td @class="select-column">
                                                <input 
                                                    @type="checkbox" 
                                                    @checked="$@selectedRows -> includes(@row.id)#"
                                                    @onChange="() =! toggleRowSelection(@row.id)"
                                                />
                                            </td>
                                            repeat column in @columns @
                                                <td @key="$@column.key#">
                                                    check column.render @
                                                        some => column.render(row)
                                                        none => row~@column.key! or "—"
                                                    #
                                                </td>
                                            #
                                        </tr>
                                    #
                                </tbody>
                            </table>
                            
                            <div @class="grid-footer">
                                <span @class="row-count">
                                    Showing $@processedData -> length# of $@data -> length# rows
                                </span>
                                if @selectedRows -> length > 0 @
                                    give <span @class="selection-info">
                                        $@selectedRows -> length# row$@selectedRows -> length == 1 ? "" : "s"# selected
                                    </span>
                                #
                            </div>
                        </div>
                    #
                #
            #
        </div>
    </div>
#

# Usage example
conduit UsersPage() @
    let @columns = ~
        @
            key: "id",
            title: "ID",
            render: (row) =! <span @class="id-cell">$@row.id#</span>
        #,
        @
            key: "name",
            title: "Name"
        #,
        @
            key: "email",
            title: "Email",
            render: (row) =! <a @href="mailto:$@row.email#">$@row.email#</a>
        #,
        @
            key: "role",
            title: "Role"
        #,
        @
            key: "status",
            title: "Status",
            render: (row) =! <span @class="status $@row.status#">$@row.status#</span>
        #
    !
    
    give <div @class="users-page">
        <h1>User Management</h1>
        <DataGrid 
            @url="/api/users" 
            @columns=@columns
        />
    </div>
#
```

---

## Integration Notes

### Importing Aperture

```rift
grab aperture
```

### CSS Integration

Aperture components can be styled with standard CSS, CSS-in-JS, or utility classes:

```rift
conduit StyledComponent() @
    give <div @class="container bg-primary text-white p-4">
        <h1 @style="color: $@theme.primary#">Styled Content</h1>
    </div>
#
```

### Server-Side Rendering

Aperture supports server-side rendering out of the box:

```rift
# Server-side rendering example
grab aperture
grab http

http.get("/", conduit(req) @
    let html = aperture.renderToString(<App/>)
    give http.html(200, html)
#)
```

---

**Conclusion:**

Aperture brings the power of reactive UI development to RIFT through its innovative RX syntax and optical-themed state management. By leveraging RIFT's unique character allocation, it provides a seamless development experience where logic and presentation flow together like light through a perfectly calibrated aperture.
