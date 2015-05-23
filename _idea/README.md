Intellij IDEA Dragonfly Grammar
===============================

[Dragonfly](https://github.com/t4ngo/dragonfly)
+
[Aenea](https://github.com/dictation-toolbox/aenea)
Grammar that allows enables basic voice coding capability in Intellij IDEA.


## Grammar Overview

**NOTE:** This readme is by no means a comprehensive guide the grammar!
Take the time to read through idea.py to learn about all of the different
things that the grammar can do.  I think you'll find that it does quite a 
bit out of the box :)

This grammar follows the following basic spec (which should look familiar
if you've read over the Dragonfly docs):
 
```[<repeatable_rule>] [parrot [<i>]] [<terminal_rule>]```

### Repeatable Commands

The workhorse of the grammar is `repeatable_rule` which allows continuous
chaining of commands.  `repeatable_rule` includes sub-rules that enables
all of the following text insertions:

  * letters
  * symbols
  * numbers
  * aenea-vocabulary
  * formatted dictations
  
For example: dictating `camel hello world laip raip` sends the keystrokes
for `helloWorld()` to the application.
   
It also includes rules that enable navigation throughout the current editor
window and modifying text'

For example `wiki ninety five doll left two` move the cursor to line 95, then
move the cursor to the end of the line, then move the cursor two characters
to the left.

Or `up two wipe` which will move the cursor up two lines then delete the 
current line. `Key('up, up, c-y')`

### Multiplying Commands

Next up is the `[parrot [<i>]]` portion of the grammar which acts as a
multiplier for `repeatable_rule'.  Any repetition of command in repeat rule 
can optionally be "parroted" "i" times.

For example: `camel hello world parrot three` sends keystrokes for
`helloWorldhelloWorldhelloWorld`.

"Parroting" commands wisely can save you a lot of time.  Get familiar with it!

### Terminal Commands

Infrequently used commands that you probably don't need to say in a continuous
stream like some of the other commands in `repeatable_rule`.  These commands
enable refactoring variable names, manipulating editor split frames, and more.
There is even support for the
[emacsIDEAs plugin](https://plugins.jetbrains.com/plugin?pr=idea&pluginId=7163)
mixed in here as well.  I'll leave it up to you to check out the code for this
one!
