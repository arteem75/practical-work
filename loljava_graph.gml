graph [
  directed 1
  node [
    id 0
    label "('Main','class',None,None)"
  ]
  node [
    id 1
    label "('Spectrum','class',None,None)"
  ]
  node [
    id 2
    label "('getEnergy','function',class[Spectrum],'()')"
  ]
  node [
    id 3
    label "('spectrum','field',class[Spectrum].function[getEnergy],None)"
  ]
  node [
    id 4
    label "('Ref','class',None,None)"
  ]
  node [
    id 5
    label "('value','field',class[Ref],None)"
  ]
  node [
    id 6
    label "('Ref','constructor',class[Ref],'()')"
  ]
  node [
    id 7
    label "('Ref','constructor',class[Ref].constructor[Ref],'(T value)')"
  ]
  node [
    id 8
    label "('isNull','function',class[Ref].constructor[Ref].constructor[Ref],'()')"
  ]
  node [
    id 9
    label "('get','function',class[Ref].constructor[Ref].constructor[Ref].function[isNull],'()')"
  ]
  node [
    id 10
    label "('set','function',class[Ref].constructor[Ref].constructor[Ref].function[isNull].function[get],'(T value)')"
  ]
  node [
    id 11
    label "('maxKey','function',class[Ref].constructor[Ref].constructor[Ref].function[isNull].function[get].function[set],'(Stream<T> stream, Function<T, Double> function)')"
  ]
  node [
    id 12
    label "('interpolate','function',class[Ref].constructor[Ref].constructor[Ref].function[isNull].function[get].function[set].function[maxKey],'(int x, int x0, int x1, int y0, int y1)')"
  ]
  node [
    id 13
    label "('interpolate','function',class[Ref].constructor[Ref].constructor[Ref].function[isNull].function[get].function[set].function[maxKey].function[interpolate],'(double x, double x0, double x1, double y0, double y1)')"
  ]
  node [
    id 14
    label "('getXByFrequency','function',class[Ref].constructor[Ref].constructor[Ref].function[isNull].function[get].function[set].function[maxKey].function[interpolate].function[interpolate],'(double frequency)')"
  ]
  node [
    id 15
    label "('getWidth','function',class[Ref].constructor[Ref].constructor[Ref].function[isNull].function[get].function[set].function[maxKey].function[interpolate].function[interpolate].function[getXByFrequency],'()')"
  ]
  node [
    id 16
    label "('getMaxSpectrumCoord','function',class[Ref].constructor[Ref].constructor[Ref].function[isNull].function[get].function[set].function[maxKey].function[interpolate].function[interpolate].function[getXByFrequency].function[getWidth],'()')"
  ]
  node [
    id 17
    label "('getMinSpectrumCoord','function',class[Ref].constructor[Ref].constructor[Ref].function[isNull].function[get].function[set].function[maxKey].function[interpolate].function[interpolate].function[getXByFrequency].function[getWidth].function[getMaxSpectrumCoord],'()')"
  ]
  node [
    id 18
    label "('foo','function',class[Ref].constructor[Ref].constructor[Ref].function[isNull].function[get].function[set].function[maxKey].function[interpolate].function[interpolate].function[getXByFrequency].function[getWidth].function[getMaxSpectrumCoord].function[getMinSpectrumCoord],'()')"
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
    source 4
    target 5
    label "def"
  ]
  edge [
    source 4
    target 6
    label "def"
  ]
  edge [
    source 6
    target 7
    label "def"
  ]
  edge [
    source 7
    target 8
    label "def"
  ]
  edge [
    source 8
    target 9
    label "def"
  ]
  edge [
    source 9
    target 10
    label "def"
  ]
  edge [
    source 10
    target 11
    label "def"
  ]
  edge [
    source 11
    target 12
    label "def"
  ]
  edge [
    source 12
    target 13
    label "def"
  ]
  edge [
    source 13
    target 14
    label "def"
  ]
  edge [
    source 14
    target 15
    label "def"
  ]
  edge [
    source 15
    target 16
    label "def"
  ]
  edge [
    source 16
    target 17
    label "def"
  ]
  edge [
    source 17
    target 18
    label "def"
  ]
]
