cuckoo2mist
=====

## About

The Malware Instruction Set (MIST) is a representation for monitored behavior
of malicious software. The representation is optimized for effective and
efficient analysis of behavior using data mining and machine learning
techniques. It can be obtained automatically during analysis of malware with a
behavior monitoring tool or by converting existing behavior reports. The
representation is not restricted to a particular monitoring tool and thus can
also be used as a meta language to unify behavior reports of different sources.

A detailed description and technical background on the concept of MIST is provided in  the following article:

- "A Malware Instruction Set for Behavior-Based Analysis." Philipp Trinius, Carsten Willems, Thorsten Holz, and Konrad Rieck Technical report TR-2009-07, University of Mannheim, 2009

This fork converts Cuckoo Sandbox behaviour reports into MIST format.

## Package Installation

Install Python dependency

```
pip install setuptools
```

Install package

```
$ python setup.py build
$ python setup.py install
```

setup.py will install murmurhash3 dependency.
If successful, import package to python

```
>> import cuckoo2mist
```

## Usage

```
$ cuckoo2mist -c [directory of custom configuration files, omit to use default configuration] -i [directory of Cuckoo logs] -o [directory where MIST reports should be saved]
```

or for direct execution from source directory without installation:

```
$ python run-cuckoo2mist.py -c [directory of custom configuration files, omit to use default configuration] -i [directory of Cuckoo logs] -o [directory where MIST reports should be saved]
```

## Updates

**Changes in this fork**

In version 0.3:

1. More API calls are added.
2. More MIST levels added.
3. Order of API calls are retained by using python ordered dictionary.
4. ELF hash is changed to Murmurhash3, it is installed as dependency, the package is mmh3 2.5.1

In version 0.4:

1. Update on codebase to allow execution of application from console after installation.
2. Able to open and read JSON reports that are compressed with gzip format.
3. Able to log unmatched APIs together with respective categories.
4. Log file is now to be saved in user directory.
5. The matching of APIs' parameters is now case insensitive.
6. Minor code mistakes corrected.

**Upcoming changes**

1. Per-file MIST conversion & removal of generated MIST reports.

Work on this fork is still ongoing. Contributors are welcomed to help improve this fork.



