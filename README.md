Cuckoo2mist
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
>> from cuckoo2mist import class_mist
```

## Usage

Specify folder containing Cuckoo JSON logs.

```
$ python cuckoo2mist.py -i [Folder of Cuckoo logs]
```

Specify folder to save MIST file output

```
$ python cuckoo2mist.py -o [Folder of Cuckoo logs]
```
Open configuration directory

```
$ python cuckoo2mist.py -c [directory of conf file]
```

If all options are omitted, default values will be used.  

## Updates

**Changes in this fork**

1. More API calls are added.
2. More MIST levels added.
3. Order of API calls are retained by using python ordered dictionary.
4. ELF hash is changed to Murmurhash3, it is installed as dependency, the package is mmh3 2.5.1

**Upcoming changes**

1. Per-file MIST conversion & removal of generated MIST reports.

Work on this fork is still ongoing. Contributors are welcomed to help improve this fork.



