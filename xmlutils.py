# -*- coding: utf-8 -*-

from xml.etree.ElementTree import TreeBuilder

class StripNamespace(TreeBuilder):
    def start(self, tag, attrib):
        index = tag.find('}')
        if index != -1:
            tag = tag[index+1:]
        super(StripNamespace, self).start(tag, attrib)
    def end(self, tag):
        index = tag.find('}')
        if index != -1:
            tag = tag[index+1:]
        super(StripNamespace, self).end(tag)