#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: ts=4 sw=4 expandtab ai

from base import Base


class PartitionTable(Base):

    def __init__(self):
        self.command_base = "partition_table"