Basic Tutorial
==============

In this tutorial we will go through some of the most common ways of using pytac.
The aim is to give you an understanding of the interface and how to find out what
is available.

The import of the aioca channel access library and epicscorelibs will
allow us to get some live values from the Diamond accelerators.

    $ pip install aioca epicscorelibs

These docs are able to be run and tested, but may return different values as
accelerator conditions will have changed.

    $ pytest docs


Loading the lattice
-------------------

The central object in pytac is the `lattice`. It holds the information about
all of the elements in the accelerator. All the data about the lattice and its
elements is stored in CSV files inside the pytac repository. We use the `load_csv`
module to load the data and initialise a `lattice` object; this is the normal
starting point for using pytac.

The "ring mode" describes one configuration of the elements in the lattice.
There is one set of CSV files for each ring mode. So when we load the lattice,
we specify the ring mode we want to load.

At the time of writing the normal ring mode in use at Diamond is "I04",
so let's load that::

    >>> import pytac
    >>> lattice = pytac.load_csv.load("I04")

The lattice object itself has some fields with its own properties::

    >>> lattice.get_fields()
    {'live': dict_keys(['beam_current', 'emittance_x', 'emittance_y', 'tune_x', 'tune_y', 's_position', 'energy'])}

The name "live" is referring to the data source - Pytac can also be set up with
additional data sources for simulation, but that isn't described here.

We can ask for the values of these fields. These commands will try to get the
real values from the live machine (so won't work if you're not on a suitable
Diamond network)::

    >>> lattice.get_value("energy", units=pytac.PHYS)
    np.float64(3000000000.0)
    >>> lattice.get_value("beam_current")
    296.773194429911

Families, elements and fields
-----------------------------

The elements in the lattice are grouped by families, and this is the most common
way to choose some to access. We can list the available families::

    >>> lattice.get_all_families()
    {'drift_drift_s2a', 'd2yc', 'd10_1', 'd09_6', 'hu64', 'd4b4ba0', 'd13_13', 'd104bar', 'd13_14', 'd104bad', 'd104baa', 'd3b', 'd13_1', 'd13_12', 'q3e', 'd2b4ba', 'dsext', 'd09_7', 'd4b', 'ux', 'q2ad', 'dlbm4ba0', 'dlbm4ba1', 'q2b', 'dk4bas21', 'd13_10', 'd13_6', 's1c', 'd09_1', 'd10_6', 'q3b', 'd054bal', 'd104ba1', 'q2d', 'mpw45', 'd2xl', 'd3b4ba', 'd6b4ba0', 'd2ya', 'hpmu', 'aperture', 'dlbm4bal1', 'vstr', 'd6b', 'u21', 'drbm4bar1', 'd3a', 'd1x', 'd09_10', 'source', 'q1ab', 'shim', 'd2xr', 'd3b4bar', 'd154bal', 'd104ba0r', 'htrim', 'd3aa', 'd5b', 's2be', 'bpm', 'drbm4bal2', 'dhs4bar3', 'd09_13', 'd13_5', 'd4a', 'd13_8', 'mpw15', 'q2ab', 'rf', 'd1a', 'd10_3', 's2d', 's2c', 'd1m4bal1', 'q1d', 'hstr', 'q1b', 'bb', 'spacer', 'bend', 'd104ba0', 'd09_8', 'd104bac', 'bbvmxs', 'd20_2', 'd10_9', 'd104bab', 'd054ba', 's1a', 'dk4bas22', 'd3ab', 's2b', 'd09_14', 'd09_3', 'd09_12', 'qm09', 'bbvmxl', 'bumpss', 'd154bar', 'd4ba', 'd10_8', 'd1d2', 'd4aa', 's4e', 'd1y', 'dlbm4bal2', 'dlb4bar', 'd13_3', 'd4bb', 'squad', 'kd1', 'q1be', 'd1yb', 'd13_2', 'mpw12', 'dhs4bar1', 's1d', 'u23b', 'q1ad', 'ap', 'd1aa', 'dbpm', 's1be', 'd1s4ba', 'wiggler', 'd13_7', 'di05', 'drbm4bal1', 'pad', 'rfcavity', 'd09_5', 'drift_s2a', 'drift', 'drbm4ba2', 'd4ab', 'qm13', 'dhs4bar2', 'd2yb', 'd1ab', 'dhs4bal2', 'd10_5', 'vtrim', 'd10_4', 'q3d', 'q2be', 'bump', 'd09_9', 'd2b', 'd1m4ba', 'u23a', 'd6bb', 'd20_1', 'hchica', 'dk4bas20', 'd09_2', 's3e', 'd6ba', 'd10_2', 'u27', 's2a', 'tempdrift', 'quadrupole', 's1b', 'sextupole', 'd10_7', 'dk4bas23', 'q4e', 'dlb4bal', 'drbm4bar2', 'dhs4ba', 'd1m4bal2', 'bpm10', 'd13_9', 'd1yad1ya', 'd2a', 'dhs4bal1'}

Let's get all the beam position monitors (BPMs). We do this by using get_elements
which takes an argument for family name - in this case we use the family name "BPM"::

    >>> bpms = lattice.get_elements('BPM')
    >>> print("Got {} BPMs".format(len(bpms)))
    Got 173 BPMs

Let's look at what we can find out about a single BPM.

Each one has some fields::

    >>> one_bpm = bpms[0]
    >>> one_bpm.get_fields()
    {'live': dict_keys(['x', 'y', 'enabled', 'x_fofb_disabled', 'x_sofb_disabled', 'y_fofb_disabled', 'y_sofb_disabled'])}

The fields represent a property of the BPM that can change. For example, x and y
are the measured positions::

    >>> one_bpm.get_value("x")
    0.047219

Devices
-------

Each field has a `device` object associated with it, which knows how to set and
get the value::

    >>> one_bpm.get_device("x")
    <pytac.device.EpicsDevice at 0x7f4290a71f10>

The `device` object knows the PV names for reading and writing the value of the
field. Each field might have a "setpoint" or "readback" handle, which could be
associated with different PV names.

You can use either strings or pytac constants to specify which handle to use::

    >>> readback_pv = one_bpm.get_pv_name("x_sofb_disabled", "readback")
    >>> same_readback_pv = one_bpm.get_pv_name("x_sofb_disabled", pytac.RB)
    >>> print(readback_pv, same_readback_pv)
    SR01C-PC-HBPM-01:SLOW:DISABLED SR01C-PC-HBPM-01:SLOW:DISABLED

Some fields are read-only, in which case there is no setpoint PV to get::

    >>> try:
    ...     one_bpm.get_pv_name("x_sofb_disabled", pytac.SP)
    ... except Exception as e:
    ...     print(e)
    Device SR01C-DI-EBPM-01 has no setpoint PV.

It's not normally necessary to interact with the `device` directly; you can do
most things through methods of the `element` or `lattice`. E.g. ``element.get_value``
above and ``lattice.get_element_pv_names``::

    >>> lattice.get_element_pv_names('BPM', 'y', 'readback')[:10]
    ['SR01C-DI-EBPM-01:SA:Y', 'SR01C-DI-EBPM-02:SA:Y', 'SR01C-DI-EBPM-03:SA:Y', 'SR01C-DI-EBPM-04:SA:Y', 'SR01C-DI-EBPM-05:SA:Y', 'SR01C-DI-EBPM-06:SA:Y', 'SR01C-DI-EBPM-07:SA:Y', 'SR02C-DI-EBPM-01:SA:Y', 'SR02C-DI-EBPM-02:SA:Y', 'SR02C-DI-EBPM-03:SA:Y']

Unit conversions
----------------

Many fields can be represented in either engineering units or physics units.
For example, for a magnet field, the physics unit would be the field strength
and the engineering unit would be the current applied by the magnet power supply
controller::

    >>> # Get a corrector magnet
    >>> corrector = lattice.get_elements("HSTR")[5]
    >>> # Request
    >>> corrector.get_value("x_kick", units=pytac.ENG)
    -3.0552401542663574

In order to get the unit itself, we have to ask for the ``unitconv`` object associated
with the field::

    >>> corrector.get_unitconv("x_kick").eng_units
    'A'

Magnet fields
-------------

This seems like a good time to talk about the names for the magnetic fields of magnets.

In accelerator physics we refer to the different components of magnetic fields
as |a_n| for vertical fields and |b_n| for horizontal fields, where n is:

.. |a_n| replace:: a\ :sub:`n`\
.. |b_n| replace:: b\ :sub:`n`\

=====   ===========
n       Field
=====   ===========
0       Dipole
1       Quadrupole
2       Sextupole
...     ...
=====   ===========

These names are used for the ``field``\s associated with magnet `element`\s in pytac.

For corrector magnets, although the corrector field acts like a dipole, it is given
the name ``x_kick`` or ``y_kick`` so that it can be easily distinguished. An example
of this is when several magnets are combined into the same `element`. The following
example shows an element which combines a corrector, a skew quadrupole and a
sextupole::

    >>> an_element = lattice.get_elements("HSTR")[12]
    >>> print("Fields:", an_element.get_fields())
    Fields: {'live': dict_keys(['b2', 'x_kick', 'h_fofb_disabled', 'h_sofb_disabled', 'y_kick', 'v_fofb_disabled', 'v_sofb_disabled', 'a1'])}
    >>> print("Families:", an_element.families)
    Families: ['hstr', 's4e', 'sextupole', 'squad', 'vstr']

Other methods of thr lattice
----------------------------

To finish off for now, let's look at some more of the methods of the `lattice`

``lattice.get_element_values`` lets you get all the live values for a field from a
while family of elements. E.g. the currents for the horizontal corrector magnets.
There is also an analogous command ``lattice.set_element_values``::

    >>> lattice.get_element_values("HSTR", "x_kick", "readback")
    [-0.24839822947978973,
    0.7639292478561401,
    -0.4572945237159729,
    -0.1370551735162735,
    0.6560376882553101,
    -3.0552401542663574,
    3.0576119422912598,
    0.6859914660453796,
    -0.8835821747779846,
    0.37336450815200806,
    -0.397186279296875,
    -0.3592968285083771,
    1.5479310750961304,
    -0.2497788667678833,
    -0.3833305537700653,
    0.04267336428165436,
    0.387008398771286,
    2.083509922027588,
    -2.213555335998535,
    2.316075086593628,
    -1.2140284776687622,
    0.4225691556930542,
    -0.3863433301448822,
    0.1559593677520752,
    2.3147804737091064,
    ...
    2.295074939727783,
    -0.5442541241645813,
    -1.0026730298995972,
    0.33420810103416443,
    -0.2033674269914627]

`s` position is the position of an element in metres around the ring.

There is a method to get the `s` positions of all elements in a family::

    >>> lattice.get_family_s("BPM")[:10]
    [4.38,
    8.806500000000002,
    11.374000000000002,
    12.559000000000005,
    14.942500000000006,
    18.005000000000003,
    21.270000000000003,
    26.93,
    30.360759,
    32.076129]
