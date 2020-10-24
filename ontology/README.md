Markdown documentation created by [pyLODE](http://github.com/rdflib/pyLODE) 2.8.3

# Movie Locations

## Metadata
* **URI**
  * `http://example.com/movieLocations/`
* **Ontology RDF**
  * RDF ([.\CleanOntology.ttl](turtle))

## Table of Contents
1. [Classes](#classes)
1. [Object Properties](#object-properties)
1. [Datatype Properties](#datatype-properties)
1. [Namespaces](#namespaces)
1. [Legend](#legend)


## Overview
![Overview](images/inferences/overview.png)
**Figure 1:** Ontology overview

## Classes
[Actor](#Actor),
[Character](#Character),
[Director](#Director),
[Genre](#Genre),
[Location](#Location),
[Movie](#Movie),
[Movie](#Movie1),
[NaturalPerson](#NaturalPerson),
[Person](#Person),
[Person](#Person1),
[Scene](#Scene),
[Series](#Series),
[Short](#Short),
[Show](#Show),
[TvEpisode](#TvEpisode),
[TvMiniSeries](#TvMiniSeries),
[TvMovie](#TvMovie),
[TvSeries](#TvSeries),
[TvSeries](#TvSeries1),
[TvShort](#TvShort),
[TvSpecial](#TvSpecial),
[Video](#Video),
[VideoGame](#VideoGame),
### Actor
Property | Value
--- | ---
URI | `http://example.com/movieLocations/Actor`
Super-classes |[ml:NaturalPerson](http://example.com/movieLocations/NaturalPerson) (c)<br />
### Character
Property | Value
--- | ---
URI | `http://example.com/movieLocations/Character`
Super-classes |[ml:Person](http://example.com/movieLocations/Person) (c)<br />
### Director
Property | Value
--- | ---
URI | `http://example.com/movieLocations/Director`
Super-classes |[ml:NaturalPerson](http://example.com/movieLocations/NaturalPerson) (c)<br />
### Genre
Property | Value
--- | ---
URI | `http://example.com/movieLocations/Genre`
### Location
Property | Value
--- | ---
URI | `http://example.com/movieLocations/Location`
### Movie
Property | Value
--- | ---
URI | `http://example.com/movieLocations/Movie`
Super-classes |[ml:Show](http://example.com/movieLocations/Show) (c)<br />
Sub-classes |[ml:TvMovie](http://example.com/movieLocations/TvMovie) (c)<br />
### NaturalPerson
Property | Value
--- | ---
URI | `http://example.com/movieLocations/NaturalPerson`
Super-classes |[ml:Person](http://example.com/movieLocations/Person) (c)<br />
Sub-classes |[ml:Director](http://example.com/movieLocations/Director) (c)<br />[ml:Actor](http://example.com/movieLocations/Actor) (c)<br />
### Person
Property | Value
--- | ---
URI | `http://example.com/movieLocations/Person`
Sub-classes |[ml:Character](http://example.com/movieLocations/Character) (c)<br />[ml:NaturalPerson](http://example.com/movieLocations/NaturalPerson) (c)<br />
### Scene
Property | Value
--- | ---
URI | `http://example.com/movieLocations/Scene`
### Series
Property | Value
--- | ---
URI | `http://example.com/movieLocations/Series`
Super-classes |[ml:Show](http://example.com/movieLocations/Show) (c)<br />
Sub-classes |[ml:TvSeries](http://example.com/movieLocations/TvSeries) (c)<br />
### Short
Property | Value
--- | ---
URI | `http://example.com/movieLocations/Short`
Super-classes |[ml:Show](http://example.com/movieLocations/Show) (c)<br />
Sub-classes |[ml:TvShort](http://example.com/movieLocations/TvShort) (c)<br />
### Show
Property | Value
--- | ---
URI | `http://example.com/movieLocations/Show`
Sub-classes |[ml:Short](http://example.com/movieLocations/Short) (c)<br />[ml:TvSpecial](http://example.com/movieLocations/TvSpecial) (c)<br />[ml:Video](http://example.com/movieLocations/Video) (c)<br />[ml:Movie](http://example.com/movieLocations/Movie) (c)<br />[ml:VideoGame](http://example.com/movieLocations/VideoGame) (c)<br />[ml:Series](http://example.com/movieLocations/Series) (c)<br />[ml:TvEpisode](http://example.com/movieLocations/TvEpisode) (c)<br />
### TvEpisode
Property | Value
--- | ---
URI | `http://example.com/movieLocations/TvEpisode`
Super-classes |[ml:Show](http://example.com/movieLocations/Show) (c)<br />
### TvMiniSeries
Property | Value
--- | ---
URI | `http://example.com/movieLocations/TvMiniSeries`
Super-classes |[ml:TvSeries](http://example.com/movieLocations/TvSeries) (c)<br />
### TvMovie
Property | Value
--- | ---
URI | `http://example.com/movieLocations/TvMovie`
Super-classes |[ml:Movie](http://example.com/movieLocations/Movie) (c)<br />
### TvSeries
Property | Value
--- | ---
URI | `http://example.com/movieLocations/TvSeries`
Super-classes |[ml:Series](http://example.com/movieLocations/Series) (c)<br />
Sub-classes |[ml:TvMiniSeries](http://example.com/movieLocations/TvMiniSeries) (c)<br />
### TvShort
Property | Value
--- | ---
URI | `http://example.com/movieLocations/TvShort`
Super-classes |[ml:Short](http://example.com/movieLocations/Short) (c)<br />
### TvSpecial
Property | Value
--- | ---
URI | `http://example.com/movieLocations/TvSpecial`
Super-classes |[ml:Show](http://example.com/movieLocations/Show) (c)<br />
### Video
Property | Value
--- | ---
URI | `http://example.com/movieLocations/Video`
Super-classes |[ml:Show](http://example.com/movieLocations/Show) (c)<br />
### VideoGame
Property | Value
--- | ---
URI | `http://example.com/movieLocations/VideoGame`
Super-classes |[ml:Show](http://example.com/movieLocations/Show) (c)<br />
### Movie
Property | Value
--- | ---
URI | `http://schema.org/Movie`
### TvSeries
Property | Value
--- | ---
URI | `http://schema.org/TvSeries`
### Person
Property | Value
--- | ---
URI | `http://xmlns.com/foaf/0.1/Person`

## Object Properties
[directs](#directs),
[hasActor](#hasActor),
[hasCharacter](#hasCharacter),
[hasDirector](#hasDirector),
[hasLocation](#hasLocation),
[hasScene](#hasScene),
[isCharacterIn](#isCharacterIn),
[isGenre](#isGenre),
[isGenreOf](#isGenreOf),
[isLocationOf](#isLocationOf),
[isSceneOf](#isSceneOf),
[playedBy](#playedBy),
[playsIn](#playsIn),
[actor](#actor),
[character](#character),
[director](#director),
[](directs)
### directs
Property | Value
--- | ---
URI | `http://example.com/movieLocations/directs`
[](hasActor)
### hasActor
Property | Value
--- | ---
URI | `http://example.com/movieLocations/hasActor`
[](hasCharacter)
### hasCharacter
Property | Value
--- | ---
URI | `http://example.com/movieLocations/hasCharacter`
[](hasDirector)
### hasDirector
Property | Value
--- | ---
URI | `http://example.com/movieLocations/hasDirector`
[](hasLocation)
### hasLocation
Property | Value
--- | ---
URI | `http://example.com/movieLocations/hasLocation`
[](hasScene)
### hasScene
Property | Value
--- | ---
URI | `http://example.com/movieLocations/hasScene`
[](isCharacterIn)
### isCharacterIn
Property | Value
--- | ---
URI | `http://example.com/movieLocations/isCharacterIn`
[](isGenre)
### isGenre
Property | Value
--- | ---
URI | `http://example.com/movieLocations/isGenre`
[](isGenreOf)
### isGenreOf
Property | Value
--- | ---
URI | `http://example.com/movieLocations/isGenreOf`
[](isLocationOf)
### isLocationOf
Property | Value
--- | ---
URI | `http://example.com/movieLocations/isLocationOf`
[](isSceneOf)
### isSceneOf
Property | Value
--- | ---
URI | `http://example.com/movieLocations/isSceneOf`
[](playedBy)
### playedBy
Property | Value
--- | ---
URI | `http://example.com/movieLocations/playedBy`
[](playsIn)
### playsIn
Property | Value
--- | ---
URI | `http://example.com/movieLocations/playsIn`
[](actor)
### actor
Property | Value
--- | ---
URI | `http://schema.org/actor`
[](character)
### character
Property | Value
--- | ---
URI | `http://schema.org/character`
[](director)
### director
Property | Value
--- | ---
URI | `http://schema.org/director`

## Datatype Properties
[bornIn](#bornIn),
[diedIn](#diedIn),
[hasEndYear](#hasEndYear),
[hasFullName](#hasFullName),
[hasLatitude](#hasLatitude),
[hasLongitude](#hasLongitude),
[hasPrimaryTitle](#hasPrimaryTitle),
[hasRating](#hasRating),
[hasRuntime](#hasRuntime),
[hasSceneName](#hasSceneName),
[hasStartYear](#hasStartYear),
[isAdult](#isAdult),
[](bornIn)
### bornIn
Property | Value
--- | ---
URI | `http://example.com/movieLocations/bornIn`
[](diedIn)
### diedIn
Property | Value
--- | ---
URI | `http://example.com/movieLocations/diedIn`
[](hasEndYear)
### hasEndYear
Property | Value
--- | ---
URI | `http://example.com/movieLocations/hasEndYear`
[](hasFullName)
### hasFullName
Property | Value
--- | ---
URI | `http://example.com/movieLocations/hasFullName`
[](hasLatitude)
### hasLatitude
Property | Value
--- | ---
URI | `http://example.com/movieLocations/hasLatitude`
[](hasLongitude)
### hasLongitude
Property | Value
--- | ---
URI | `http://example.com/movieLocations/hasLongitude`
[](hasPrimaryTitle)
### hasPrimaryTitle
Property | Value
--- | ---
URI | `http://example.com/movieLocations/hasPrimaryTitle`
[](hasRating)
### hasRating
Property | Value
--- | ---
URI | `http://example.com/movieLocations/hasRating`
[](hasRuntime)
### hasRuntime
Property | Value
--- | ---
URI | `http://example.com/movieLocations/hasRuntime`
[](hasSceneName)
### hasSceneName
Property | Value
--- | ---
URI | `http://example.com/movieLocations/hasSceneName`
[](hasStartYear)
### hasStartYear
Property | Value
--- | ---
URI | `http://example.com/movieLocations/hasStartYear`
[](isAdult)
### isAdult
Property | Value
--- | ---
URI | `http://example.com/movieLocations/isAdult`

## Named Individuals
## Namespaces
* **foaf**
  * `http://xmlns.com/foaf/0.1/`
* **ml**
  * `http://example.com/movieLocations/`
* **owl**
  * `http://www.w3.org/2002/07/owl#`
* **prov**
  * `http://www.w3.org/ns/prov#`
* **rdf**
  * `http://www.w3.org/1999/02/22-rdf-syntax-ns#`
* **rdfs**
  * `http://www.w3.org/2000/01/rdf-schema#`
* **schema**
  * `http://schema.org/`
* **sdo**
  * `https://schema.org/`
* **skos**
  * `http://www.w3.org/2004/02/skos/core#`
* **xsd**
  * `http://www.w3.org/2001/XMLSchema#`

## Legend
* Classes: c
* Object Properties: op
* Functional Properties: fp
* Data Properties: dp
* Annotation Properties: dp
* Properties: p
* Named Individuals: ni