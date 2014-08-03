#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import argparse
from collections import namedtuple
import sys
import abc

try:
    from functools import singledispatch
except ImportError:
    from singledispatch import singledispatch

import libvirt
import xmltodict
import six
import simplejson
from prettytable import PrettyTable


class NetworkInterfaceCard(namedtuple(
    'NetworkInterfaceCard',
    [
        'name',
        'domain',
        'network',
        'type',
        'hwaddr',
        'model',
    ],
)):
    pass


def getnics(domain):
    name = domain.get('name')
    devices = domain.get('devices')
    ifaces = devices.get('interface')
    return _getnics_from_iface(ifaces, name)


@singledispatch
def _getnics_from_iface(iface, domain):
    raise NotImplementedError()


def _drill(d, chain):
    target = d
    for element in chain:
        target = target.get(element)
    return target


@_getnics_from_iface.register(dict)
def _getnics_from_iface_dict(iface, domain):
    name = _drill(iface, ['target', '@dev'])
    net_type = _drill(iface, ['@type'])
    network = _drill(iface, ['source']).get('@' + net_type)
    hwaddr = _drill(iface, ['mac', '@address'])
    model = _drill(iface, ['model', '@type'])

    nic = NetworkInterfaceCard(
        name=name,
        domain=domain,
        network=network,
        type=net_type,
        hwaddr=hwaddr,
        model=model,
    )

    return [nic]


@_getnics_from_iface.register(list)
def _getnics_from_iface_list(ifaces, domain):
    return [_getnics_from_iface_dict(iface, domain)[0] for iface in ifaces]


@six.add_metaclass(abc.ABCMeta)
class PrintFormatter(object):

    @abc.abstractmethod
    def formatize(self, nics):
        pass

    @classmethod
    def new_instance(cls, fmt):
        mappings = {
            'table': TableFormatter,
            'json': JsonFormatter,
        }
        return mappings.get(fmt)()


class TableFormatter(PrintFormatter):

    def formatize(self, nics):
        table_rows = ['Tap', 'Domain', 'Network', 'Type', 'HWAddr', 'Model']
        table = PrettyTable(table_rows)

        for nic in nics:
            table.add_row([
                nic.name,
                nic.domain,
                nic.network,
                nic.type,
                nic.hwaddr,
                nic.model,
            ])

        return str(table)


class JsonFormatter(PrintFormatter):

    def formatize(self, nics):
        return simplejson.dumps(nics, indent=4, namedtuple_as_object=True)


def _execute(args):
    connection = libvirt.open(args.connect)

    nics = []
    for domain_id in connection.listDomainsID():
        domain = connection.lookupByID(domain_id)
        domain_xml = domain.XMLDesc()
        domain_dict = xmltodict.parse(domain_xml).get('domain')
        nics += getnics(domain_dict)

    formatter = PrintFormatter.new_instance(args.format)
    print(formatter.formatize(nics))


def _parse_args():
    description = 'Python Script for Libvirt Acceleration SHortcut'
    arg_parser = argparse.ArgumentParser(description=description)

    option_c_help = 'Connection URI'
    default_connect = 'qemu:///system'
    arg_parser.add_argument(
        '-c', '--connect',
        type=str,
        required=False, default=default_connect,
        help=option_c_help,
    )

    option_f_help = 'Print Format'
    format_choices = ['table', 'json']
    default_format = format_choices[0]
    arg_parser.add_argument(
        '-f', '--format',
        choices=format_choices,
        required=False, default=default_format,
        help=option_f_help,
    )

    option_d_help = 'Debug Mode'
    default_debug = False
    arg_parser.add_argument(
        '-d', '--debug',
        action='store_true',
        required=False, default=default_debug,
        help=option_d_help,
    )

    subcommand_help = 'Sub Command'
    subparsers = arg_parser.add_subparsers(
        help=subcommand_help,
    )

    sub_tap_list_help = 'Tap List'
    subparsers.add_parser(
        'tap-list',
        help=sub_tap_list_help,
    )

    return arg_parser.parse_args()


def main():
    try:
        args = _parse_args()
        _execute(args)
    except BaseException as e:
        print('Error: %s' % e, file=sys.stderr)
        if args.debug:
            import traceback
            print(traceback.format_exc(), file=sys.stderr)

if __name__ == '__main__':
    main()
