graph [
  directed 1
  node [
    id 0
    label "('HelloWorld','class',None)"
  ]
  node [
    id 1
    label "('main','function',class[HelloWorld])"
  ]
  node [
    id 2
    label "('approve','function',class[HelloWorld].function[main])"
  ]
  node [
    id 3
    label "('approve','function',class[HelloWorld].function[main].function[approve])"
  ]
  node [
    id 4
    label "('lol','function',class[HelloWorld].function[main].function[approve].function[approve])"
  ]
  node [
    id 5
    label "('lol','function',class[HelloWorld].function[main].function[approve].function[approve].function[lol])"
  ]
  node [
    id 6
    label "('lol','function',class[HelloWorld].function[main].function[approve].function[approve].function[lol].function[lol])"
  ]
  node [
    id 7
    label "('Newclass','class',None)"
  ]
  edge [
    source 0
    target 1
    label "def"
  ]
  edge [
    source 0
    target 7
    label "inherits"
  ]
  edge [
    source 1
    target 2
    label "def"
  ]
  edge [
    source 2
    target 3
    label "def"
  ]
  edge [
    source 3
    target 4
    label "def"
  ]
  edge [
    source 4
    target 5
    label "def"
  ]
  edge [
    source 5
    target 6
    label "def"
  ]
]
