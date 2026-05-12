# D38999-3MF

![Mated connector system shell size
C](images/mated_back.jpg)

In this repository we developed a MIL-DTL-38999 style
connector system that can be 3D-printed. It was inspired by
[this thing](https://www.thingiverse.com/thing:3129731) by
[fdavies](https://www.thingiverse.com/fdavies/designs). The
connector system uses Molex
[1561](https://www.molex.com/en-us/products/series-chart/1561)
and
[1560](https://www.molex.com/en-us/products/series-chart/1560)
stamped circular crimp contacts. 
> Note this connector system
does not claim full compatibility and compliance with the
standards mentioned. 

## Introduction

MIL-DTL-38999 connectors are widely adopted in the aerospace
industry. You may take a look at the different variants at
leading manufacturers like [Amphenol
Aerospace](https://www.amphenol-aerospace.com/products/mil-dtl-38999-connectors)
or [ITT Cannon](https://www.ittcannon.com/38999-style). A
really common type is the type III variant which features a
triple start thread for mating.

These connectors are durable,
[scoop-proof](https://www.microwaves101.com/encyclopedias/scoop-proof-connectors)
and satisfying to work with. However, they are also
expensive and thus not an option for small or hobby
projects. This project aims to change that by making these
connectors accessible to a broader audience via additive
manufacturing. Surely these versions will never match the
characteristics of the industrial versions but they make the
D38999 concept with almost all advantages accessible to more people than just industry
branches. 

## Specifications and Features

- 336 unique connector systems in nine different sizes
- M3 bolt holes for mounting of receptacle
- Polarized and scoop proof
- Up to 61 contacts per connector
- 1.25 turns to fully lock
- cheap and accessible contacts <0.10€ per contact
- mated length 30mm
- max footprint 46 x 46 mm

## Usage

A connector system consists of a receptacle and a plug. You
can mate the plug to the receptacle by turning the plug on
the receptacle until the keys align. The connectors should
move closer together at that point. Then you pull the
connection closed by rotating the coupling nut on the plug
clockwise. Turn the coupling nut until the groove on the
receptacle is covered by the nut. To release the connector rotate the coupling nut
counter-clockwise.

![Animation showing mating of
connectors](images/connector_mating.gif)

*Animation of
connectors mating*

To build a connector system you have to 
1. choose shells, and
2. choose an insert arrangement. 

We will go into more detail of these two steps in the
following sections.

### Shells

Shells are the frames of the connector system that in turn
hold the fixture (insert) that locates the electrical
contacts. They are the outermost part of the connector and
thus are called shells. Their primary function is the
mechanical mating.

The shells are characterized by part numbers in this format:

`D38999-<ST>A<S><XXX><K>`
where
- `D38999` is the connector series code,
- `<ST>` is the shell type,
- `A` is the service class for additive manufacturing
  (choosen by us)
- `<S>` is the size code,
- `<XXX>` is the insert arrangement identifier, and
- `<K>` is the keying code.

The individual parts for the part number are addressed int
he following sections

#### Shell types

There are two shell types supported at the moment: 
- straight plugs (code `26`)
  ![Straight plug part code
  D38999-26ACXXXN](images/plug_front.jpg) *A D38999-26ACXXXN
  shell*
- wall mount receptacles (code `20`)
  ![Wall mount receptacle part code
  D38999-20ACXXXN](images/receptacle_front.jpg) *A
  D38999-20ACXXXN shell*
  
#### Shell sizes

The shell size determines only the diameter of a
shell. The length i.e. the dimension in direction of the
mating axis is not affected by this. 

The available shell sizes are listed in the following table.
Note that there are military and civil codes for the shell
size. For the shells the military code is used in this repository.

| military code | `A` | `B` | `C` | `D` | `E` | `F` | `G` | `H` | `J` |
| --------------| - | - | - | - | - | - | - | - | - |
| civil code |` 9` | `11` | `13` | `15` | `17` | `19` | `21` | `23` | `25` |

![Shell size B and C
plugs](images/different_size_plugs.jpg)*Different shell size
plugs: size B on the left and size C on the right*

In general larger connectors can hold inserts with more electrical contacts.

#### Shell keying

Shells of the same size can have different keying options.
Only plugs and receptacles with matching **keying options and
shell sizes** can
mate.

This mechanically prevents mating of wrong connector pairs.
The behavior is achieved by having five keys or keyways around the plug
or receptacle, respectively, in a unique pattern for every
keying option. Note that the exact pattern can also change depending
on the shell size.

The available keying options are: 

`N, A, B, C, D, E`

Here option `N` is the most common "normal" option.

#### Building shell part numbers

In conclusion, to build a shell part number you 
1. select the shell type,
2. select the shell size,
3. select the shell keying.

The CAD models for the shells are found in the `/models/`
directory. They are modeled using [FreeCAD](https://www.freecad.org).

### Inserts

Inserts are the inner parts of the connector system that
locate the electrical contacts. The insert arrangement part
numbers look like this:

`<SZ>-<IA><G>` where
- `<SZ>` is the shell size, 
- `<IA>` is the insert arrangement, and
- `<G>` is the gender.

#### Shell size

The shell size determines which shell sizes the insert can
be used with. It primarily determines the outside diameter
of the insert. 

All shell sizes have at least two insert arrangements
available right now.

#### Insert arrangement

The insert arrangement determines how the contacts are
arranged in the insert. The code hints how many contacts
can find place in a insert. This is not always the case.

The following insert arrangements (combined with the shell
size) are available

| Insert Arrangement Name | Number of contacts | Tested |
|------------------------|-------------------| -------- |
| 9-3                    | 3                 | :white_check_mark: |
| 9-98                   | 3                 | :white_check_mark: |
| 11-2                   | 2                 | :white_check_mark: |
| 11-4                   | 4                 | :white_check_mark: |
| 11-5                   | 5                 | :white_check_mark: |
| 11-98                  | 6                 | :white_check_mark: |
| 11-99                  | 7                 | :white_check_mark: |
| 13-4                   | 4                 | :white_check_mark: |
| 13-8                   | 8                 | :white_check_mark: |
| 13-98                  | 10                | :white_check_mark: |
| 15-5                   | 5                 | :white_check_mark: |
| 15-15                  | 15                | :white_check_mark: |
| 15-18                  | 18                | :white_check_mark: |
| 15-19                  | 19                | :white_check_mark: |
| 15-97                  | 12                | :white_check_mark: |
| 17-6                   | 6                 | :x: |
| 17-8                   | 8                 | :x: |
| 17-11                  | 11                | :x: |
| 17-26                  | 26                | :x: |
| 19-11                  | 11                | :x: |
| 19-28                  | 28                | :x: |
| 19-30                  | 30                | :x: |
| 19-32                  | 32                | :x: |
| 21-11                  | 11                | :x: |
| 21-16                  | 16                | :x: |
| 21-24                  | 24                | :x: |
| 21-25                  | 25                | :x: |
| 21-27                  | 27                | :x: |
| 21-29                  | 26                | :x: |
| 21-39                  | 39                | :x: |
| 21-75                  | 4                 | :x: |
| 21-76                  | 4                 | :x: |
| 23-21                  | 21                | :x: |
| 23-32                  | 32                | :x: |
| 23-34                  | 34                | :x: |
| 23-36                  | 36                | :x: |
| 23-53                  | 53                | :x: |
| 23-55                  | 55                | :x: |
| 23-97                  | 16                | :x: |
| 23-99                  | 11                | :x: |
| 25-4                   | 56                | :x: |
| 25-8                   | 8                 | :x: |
| 25-10                  | 8                 | :x: |
| 25-11                  | 11                | :x: |
| 25-19                  | 19                | :x: |
| 25-20                  | 30                | :x: |
| 25-21                  | 30                | :x: |
| 25-24                  | 24                | :x: |
| 25-29                  | 29                | :x: |
| 25-37                  | 37                | :x: |
| 25-43                  | 43                | :x: |
| 25-46                  | 46                | :x: |
| 25-47                  | 46                | :x: |
| 25-61                  | 61                | :x: |
| 25-90                  | 46                | :x: |
| 25-91                  | 46                | :x: |

Where possible standard insert arrangements are used as
specified in MIL-STD-1560C.

Not all inserts have been tested yet. Feel free to
contribute here.

#### Gender

The gender determines whether the insert is designed to hold
pin contacts (Molex 1560, code `P`) or socket contacts
(Molex 1561, code `S`). 

This impacts the length of the insert but any gender of
insert can be installed in any receptacle or plug as long as
the shell size matches. 

In general, the plug that can be moved around gets the socket insert because these
contacts are less exposed and less prone to damage. The
receptacle receives the pin insert.

#### Building insert part numbers

In conclusion, to build a part number of an insert you need
to
1. choose the shell size, 
2. choose how many contacts you need,
3. choose the gender.

Most of the time you'll want to get both genders of an
insert, however.

Insert are automatically generated through scripts located
in `/scripts/`. The base models are designed in
[FreeCAD](https://www.freecad.org) and are located in `/models/` 

## Manufacturing and Assembly

There are a few important notices you should follow when
building your connector system. These steps are described in
the following section.

### Manufacturing

[Download](https://www.printables.com/@leandermerbe_4394823/collections/3171811) or [export](/scripts/) the model files and slice them. We had
good results with 0.2mm layer height. Print the shells in
the orientation shown in the figure below.

![Print orientation
shells](images/connector_system_printing_orientation.png)*Recommended
printing
orientation for plug, receptacle, and inserts.*

The plug is a two body part that is print in place.

> **IMPORTANT**
> 
> Disable support generation for the plug shell. You will
> not be able to remove the support.

The print time varies and can take up to multiple hours.

### Assembly

After the print is finished remove the parts. You can now
turn the coupling nut on the plug shell to break it loose
from the core. If this does not work right away you can use
a matching receptacle to fix the core in place and get a
better grip on it. 

![Breaking the coupling nut of the plug
loose](images/breaking_coupling_nut_loose.JPG)*Breaking the
coupling nut loose from the plug core.*

Now you clean the insert contact holes with a 2mm drill.
This removes any strings or seams formed during
manufacturing. You may use a cordless drill to speed up the
process. 

![Cleaning contact
holes](images/cleaning_insert_contact_fixture.JPG)*Cleaning
the contact holes with a 2mm drill*

Next, insert the inserts into the shells. Depending on the
fit you may want to glue them in permanently with superglue
or shim them with e.g. a piece of paper.

![Insertion of
inserts](images/insert_insertion.JPG)*Insertion of inserts*

Afterward, crimp the cables/wires with the Molex 1560 or
1561 contacts and insert the contacts into the appropriate
insert depending on the gender. You may use a pair of pliers
here to exert more force but the contact should go in rather
smoothly. Insert the contacts into the insert so far that
the contact is just barely inside of the insert.

![Installing the contacts](images/contact_insertion.JPG)
*Installing crimp contacts*


At last, you have your completed connector system:
![Completed connector
system](images/assembled_connector_system.JPG)*Completed
connector system*

## Developer Instructions

So you want to have a deeper look into this repository and
how the CAD files are working? We look at three parts here
1. the CAD files,
2. exporting the models, and
3. generating inserts.

### CAD files

The CAD files are developed with
[FreeCAD](https://www.freecad.org/) and split into only four
files
1. a file for the receptacle `/models/D38999-26AXXXXX.FCStd`,
2. a file for the plug `/models/D38999-20AXXXXX.FCStd`,
3. a file for the pin inserts `/models/PinInserts.FCStd`, and 
4. a file for the socket inserts. `/models/SocketInserts.FCStd`

Historically, the receptacle and plug files contained the
geometry of the inserts. When automation was deployed in
the insert generation this was changed.

The models are parametrized and the shell size and keying
option can be changed by accessing the corresponding attributes of the
`Receptacle_core` or `Plug_core` parts in the property
inspector. Note that keying options vary for shell sizes and
are thus given with the keying code and all applicable shell
sizes afterward. 

The insert models are generated automatically and also
exported in one go. The models for them contain the
base body that fits into the shell and a tool body that is
used to form the contact fixtures for all inserts. 

### Export

As there are a lot of geometries to export, this process is
automated with scripts located in `/scripts/`. The export is split into different procedures for
inserts and shells. It uses python and the python interface
of FreeCAD. Before starting you need to install
dependencies: 
```bash
> cd ./scripts/
> python3 -m venv .venv
> source .venv/bin/activate
> pip install -r requirements.txt 
> # this is for the export using FreeCAD python
> freecad.pip install -r requirements.txt
```

Then you can start the export which is described for shells
and inserts separately.

#### Shells

To export shells we use the `export_shells.py` script. It
changes the keying option and shell size of both shell
models, recomputes the model and exports a `.3mf` to
`/output/`. Note that the export can take up to six minutes.

To run it type:

```bash
> cd scripts
> freecad.cli export_shells.py
```

After the run your output directory should look like this (abbreviated).

```bash
> tree ./output/
./output/
├── plugs
│   ├── A
│   │   ├── D38999-26AAXXXA.3mf
│   │   ├── D38999-26AAXXXB.3mf
│   │   ├── D38999-26AAXXXC.3mf
│   │   ├── D38999-26AAXXXD.3mf
│   │   ├── D38999-26AAXXXE.3mf
│   │   └── D38999-26AAXXXN.3mf
│   ├── B
│   │   └── ...
│   ├── C
│   │   └── ...
│   ├── D
│   │   └── ...
│   ├── E
│   │   └── ...
│   ├── F
│   │   └── ...
│   ├── G
│   │   └── ...
│   ├── H
│   │   └── ...
│   └── J
│   │   └── ...
└── wall_mount_receptacles
    ├── A
    │   ├── D38999-20AAXXXA.3mf
    │   ├── D38999-20AAXXXB.3mf
    │   ├── D38999-20AAXXXC.3mf
    │   ├── D38999-20AAXXXD.3mf
    │   ├── D38999-20AAXXXE.3mf
    │   └── D38999-20AAXXXN.3mf
    ├── B
    │   └── ...
    ├── C
    │   └── ...
    ├── D
    │   └── ...
    ├── E
    │   └── ...
    ├── F
    │   └── ...
    ├── G
    │   └── ...
    ├── H
    │   └── ...
    └── J
        └── ...
```

The geometries are exported sorted by shell type, shell size
and then keying option. 

#### Inserts

The insert export is a two step process. First the
dimensions are extracted from the MIL-STD-1560 pdf. This is
done with python via the following command. It may take a
few minutes to run. 

```bash
> cd scripts
> python3 extract_dimension_tables.py
```
The script scans the standard for any inserts for the D38999
Series III connectors that have no contacts smaller than
size 20. This ensures the Molex 1560 and 1561 contacts fit
into the insert. 

After the command the `/dimensions/` directory should
look like this:

```bash
tree dimensions/
dimensions/
├── 11-2_contact_positions.csv
├── 11-4_contact_positions.csv
├── ...
├── applicable_insert_arrangements.csv
├── MIL-STD-1560C_CHG-2.pdf
└── overview.csv
```

The `*_contact_positions.csv` files contain the positions
for the contacts of every insert-arrangement. The
`applicable_insert_arrangements.csv` is a simple list of all
insert arrangements that are available for this connector
series. Likewise `overview.csv` lists the available insert
arrangements with the available amounts of contacts, as in
the table above. 

Next, the FreeCAD CLI is used to generate all inserts that
are in the `dimensions` directory. Note that you may define
custom insert arrangements with unique file names following
the naming convention. This script can take a few minutes to
run. 

```bash
> cd scripts
> freecad.cli insert_generator.py
```

Now the `output` directory should contain all exported
insert models. 

```bash
> tree output
output
└── inserts
    ├── A
    │   ├── 9-3P.3mf
    │   ├── 9-3S.3mf
    │   ├── 9-98P.3mf
    │   └── 9-98S.3mf
    ├── B
    │   └── ...
    ├── C
    │   └── ...
    ├── D
    │   └── ...
    ├── E
    │   └── ...
    ├── F
    │   └── ...
    ├── G
    │   └── ...
    ├── H
    │   └── ...
    └── J
        └── ...
```


## Credits

This project was inspired by [this
thing](https://www.thingiverse.com/thing:3129731) by
[fdavies](https://www.thingiverse.com/fdavies/designs).
Though the models have been developed independently and the
features have been radically altered.

The standards used for design are 
- [MIL-DTL-38999](http://everyspec.com/MIL-SPECS/MIL-SPECS-MIL-DTL/MIL-DTL-38999M_AMENDMENT-2_57021/)
    - [MIL-DTL-38999/20](https://everyspec.com/MIL-SPECS/MIL-SPECS-MIL-DTL/MIL-DTL-38999_20G_AMENDMENT-2_42842/)
    - [MIL-DTL-38999/26](https://everyspec.com/MIL-SPECS/MIL-SPECS-MIL-DTL/MIL-DTL-38999_26E_302/) 
- [MIL-STD-1560](http://everyspec.com/MIL-STD/MIL-STD-1500-1599/MIL-STD-1560C_CHG-2_56319/)
 
## License

This work is licensed under [CC BY-NC-SA
4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.de).
See `LICENSE`for complete license text.