# Darklands River Map

ASCII map of water links in Darklands, compiled by C. Michel Boucher (alsandor@netcom.ca).
Source: `rivermap.htm` (originally from darklands.net).

The water connections are divided into four primary basins:

- Rhine–North Sea
- Elbe
- Baltic
- Danube

## Legend

| Symbol | Meaning |
|---|---|
| `->`, `<-`, `/\|\`, `\\\|/` | One-way connection (arrow points in flow direction) |
| `unconnected` | City has land contact only from surrounding cities |
| `--`, `\|`, `+` | Two-way water connection |

## ASCII Map

```
==============================================================================

                            RHINE-NORTH SEA BASIN

             Gröningen
                          Leer-------------->Bremen------------------Hamburg
                           |                   |
               Zwölle------+       +-----------+------------+
                |  |               |           |            |
      Elburg----+  |             Kassel    Hannover----Braunschweig
                   |               |                        |
                 Deventer          |                        |
                   | |             |                     Goslar
                   | |           Fulda
     Nymwegen------+ |
     /|\   |         |
      |    |         |
      |  Xanten------+
      |    |
      +----+-------Wesel-------------------------Paderborn
           |         |
           |         |       Dortmund    Soest
   Kempen  |         |
           +------Duisberg
                     |
                     |
       Aachen      Köln
                     |
                     |
         Trier----Koblenz
           |         |                       Bamberg-------+
           |         |                          |          |
 Luxemburg |       Mainz------Frankfurt M       |       Nürnberg
           |         |                 |        |
           |         |                 +-----Würzburg
           |         |
         Nancy     Worms------Heidelberg
                     |         |     |            Hall
                     |         |     |
                  Speyer-------+  Stuttgart
                     |               |                 Nördlingen
                     |               |
                Strassburg        Rottweil
                     |
                     |       Freiburg B
                   Basel
                     |
                     +-------Zürich------Konstanz

==============================================================================

                                  ELBE BASIN

                                Furstenberg
                                    |
  ---Hamburg----Brandenberg------Berlin
        | |         |                            +--------------------+
        | |        \|/                           |                    |
        | +-----Magdeburg-------Wittenberg----Dresden-------Prag---Kuttenberg
        |        |  |               |  |         |          | |      /|\
    Luneberg     |  |               |  |         |          | |       |
                 |  +-----Leipzig---+  |         |          | |       |
                 |                     |         | Burglitz-+ |       |
                 |                     |         |   |        |       |
                 |  Erfurt             |         |   +--------+       |
                 |                     |         |   |                |
                 |                     |    St.Joachimstahl-----------+
                 +--------Freiberg-----+

==============================================================================

                               BALTIC SEA BASIN

             Naskskov----Vordingbord
                |
  Flensburg-----+
       |
   Schleswig
        |              +-----Stralsund
      Lubeck        Rostock      |       +-------------------------Danzig---+
        +---Wismar-----+         +----Stettin-------------+          |      |
                                         | |              |          |      |
                             Prenzlau    | +--Posen----Bromberg  Marienburg |
                                         | +--+  +-----+             |      |
                                    Frankfurt O----+   |             |      |
                                     Görlitz       |   |           Thorn----+
                                         |         |   |
                                         +--------Breslau

==============================================================================

                                DANUBIAN BASIN

                                                                 Teschen

                                                         +---Olmutz
                                                         |     |
                                                         |     |
                                                       Brunn   |
                                                         |     |
                                                         |     |
  +-------Regensburg-----Passau----Linz----------Wien---Pressburg
  |        |    |         |  |       |            |        |
  |        |    |         |  |       +----Steyr---+        |
 Ulm       |    |         |  |                             |
  |        |    +-München-+  +--Salzburg          Graz-----+
  |        |                       |
  +---Augsburg                     |
                     Kufstein------+
```

## Adjacency listings (water connections only)

Cities not listed below are land-contact-only (per the legend, "unconnected"):
Gröningen, Aachen, Luxemburg, Dortmund, Soest, Kempen, Hall, Nördlingen,
Freiburg B, Erfurt, Prenzlau, Teschen.

### Rhine–North Sea Basin

- **Leer** -> Bremen *(one-way, downstream)*
- **Bremen** -- Hamburg, Leer (inbound only), Kassel, Hannover, Braunschweig
- **Hannover** -- Bremen, Braunschweig
- **Braunschweig** -- Bremen, Hannover, Goslar
- **Goslar** -- Braunschweig
- **Kassel** -- Bremen, Fulda
- **Fulda** -- Kassel
- **Leer** -- Zwölle, Bremen *(outbound only)*
- **Zwölle** -- Leer, Elburg, Deventer
- **Elburg** -- Zwölle
- **Deventer** -- Zwölle, Nymwegen, Xanten
- **Nymwegen** -- Deventer; Wesel -> Nymwegen *(one-way inbound)*
- **Xanten** -- Deventer, Wesel
- **Wesel** -- Xanten, Paderborn, Duisberg; -> Nymwegen *(one-way)*
- **Paderborn** -- Wesel
- **Duisberg** -- Wesel, Köln
- **Köln** -- Duisberg, Koblenz
- **Koblenz** -- Köln, Trier, Mainz
- **Trier** -- Koblenz, Nancy
- **Nancy** -- Trier
- **Mainz** -- Koblenz, Frankfurt M, Worms
- **Frankfurt M** -- Mainz, Würzburg
- **Würzburg** -- Frankfurt M, Bamberg
- **Bamberg** -- Würzburg, Nürnberg
- **Nürnberg** -- Bamberg
- **Worms** -- Mainz, Heidelberg, Speyer
- **Heidelberg** -- Worms, Speyer, Stuttgart
- **Speyer** -- Worms, Heidelberg, Strassburg
- **Stuttgart** -- Heidelberg, Rottweil
- **Rottweil** -- Stuttgart
- **Strassburg** -- Speyer, Basel
- **Basel** -- Strassburg, Zürich
- **Zürich** -- Basel, Konstanz
- **Konstanz** -- Zürich

### Elbe Basin

- **Furstenberg** -- Berlin
- **Hamburg** -- Brandenberg, Magdeburg, Luneberg
- **Brandenberg** -- Hamburg, Berlin; -> Magdeburg *(one-way south, `\|/`)*
- **Berlin** -- Brandenberg, Furstenberg
- **Luneberg** -- Hamburg
- **Magdeburg** -- Hamburg, Wittenberg, Leipzig, Freiberg; Brandenberg -> *(inbound only)*
- **Wittenberg** -- Magdeburg, Dresden, Leipzig, Freiberg
- **Leipzig** -- Magdeburg, Wittenberg
- **Freiberg** -- Magdeburg, Wittenberg
- **Dresden** -- Wittenberg, Prag, Kuttenberg (alternate route), St.Joachimstahl
- **Prag** -- Dresden, Kuttenberg, Burglitz
- **Burglitz** -- Prag
- **Kuttenberg** -- Prag, Dresden (alternate); St.Joachimstahl -> Kuttenberg *(one-way, `/|\`)*
- **St.Joachimstahl** -- Dresden; -> Kuttenberg *(one-way outbound)*

### Baltic Sea Basin

- **Naskskov** -- Vordingbord, Flensburg
- **Vordingbord** -- Naskskov
- **Flensburg** -- Naskskov, Schleswig
- **Schleswig** -- Flensburg, Lubeck
- **Lubeck** -- Schleswig, Wismar
- **Wismar** -- Lubeck, Rostock
- **Rostock** -- Wismar, Stralsund
- **Stralsund** -- Rostock, Stettin
- **Stettin** -- Stralsund, Danzig, Posen, Frankfurt O
- **Danzig** -- Stettin, Marienburg, Thorn
- **Marienburg** -- Danzig, Thorn
- **Thorn** -- Danzig, Marienburg
- **Posen** -- Stettin, Bromberg, Frankfurt O
- **Bromberg** -- Posen, Breslau
- **Frankfurt O** -- Stettin, Posen, Görlitz, Breslau (alternate)
- **Görlitz** -- Frankfurt O, Breslau
- **Breslau** -- Bromberg, Görlitz, Frankfurt O (alternate)

### Danubian Basin

- **Ulm** -- Regensburg, Augsburg
- **Augsburg** -- Ulm, Regensburg
- **Regensburg** -- Ulm, Augsburg, Passau, München
- **Passau** -- Regensburg, München, Linz, Salzburg
- **München** -- Regensburg, Passau
- **Linz** -- Passau, Wien, Steyr
- **Steyr** -- Linz, Wien
- **Wien** -- Linz, Steyr, Pressburg
- **Pressburg** -- Wien, Graz, Brunn, Olmutz
- **Graz** -- Pressburg
- **Salzburg** -- Passau, Kufstein
- **Kufstein** -- Salzburg
- **Olmutz** -- Brunn, Pressburg
- **Brunn** -- Olmutz, Pressburg

## Notes

- One-way edges noted with `(one-way)`. They represent rivers that can only be travelled in one direction (downstream-only).
- The Dresden ↔ Kuttenberg alternate route (shown by the U-shape over the Elbe line) and the Frankfurt O ↔ Breslau alternate (shown by the second vertical past Görlitz) are extra connections beyond the obvious chain.
- Encoding: the source HTML is Windows-1252; the `?`/replacement characters in the original have been resolved to ö/ü as appropriate.
