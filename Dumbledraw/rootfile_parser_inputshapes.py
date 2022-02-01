#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import logging
import ROOT
import copy
logger = logging.getLogger(__name__)


class Rootfile_parser(object):

    _ggH_masses = [80,90,100,110,120,130,140,160,180,200,250,300,350,400,450,500,600,700,800,900,1000,1200,1400,1500,1600,1800,2000,2300,2600,2900,3200]
    _ggH_dataset_map = {
            "gg{proc}_{con}_{mass}".format(proc=proc, con=contrib, mass=mass): "susyggH_{mass}".format(mass=mass) \
                for proc in ["A", "H", "h"] \
                for mass in [80,90,100,110,120,130,140,160,180,200,250,300,350,400,450,500,600,700,800,900,1000,1200,1400,1500,1600,1800,2000,2300,2600,2900,3200] \
                for contrib in ["t", "b", "i"]
             }
    _ggH_process_map = {
            "gg{proc}_{con}_{mass}".format(proc=proc, con=contrib, mass=mass): "SUSYggH-gg{proc}_{con}".format(mass=mass, proc=proc, con=contrib) \
                for proc in ["A", "H", "h"] \
                for mass in [80,90,100,110,120,130,140,160,180,200,250,300,350,400,450,500,600,700,800,900,1000,1200,1400,1500,1600,1800,2000,2300,2600,2900,3200] \
                for contrib in ["t", "b", "i"]
            }

    _ggH_dataset_map_fraction = {
            "gg{proc}_{con}_{mass}_fraction".format(proc=proc, con=contrib, mass=mass): "susyggH_{mass}".format(mass=mass) \
                for proc in ["A", "H", "h"] \
                for mass in [80,90,100,110,120,130,140,160,180,200,250,300,350,400,450,500,600,700,800,900,1000,1200,1400,1500,1600,1800,2000,2300,2600,2900,3200] \
                for contrib in ["t", "b", "i"]
             }
    _ggH_process_map_fraction = {
            "gg{proc}_{con}_{mass}_fraction".format(proc=proc, con=contrib, mass=mass): "SUSYggH-gg{proc}_{con}-gg{proc}_{con}_fraction".format(mass=mass, proc=proc, con=contrib) \
                for proc in ["A", "H", "h"] \
                for mass in [80,90,100,110,120,130,140,160,180,200,250,300,350,400,450,500,600,700,800,900,1000,1200,1400,1500,1600,1800,2000,2300,2600,2900,3200] \
                for contrib in ["t", "b", "i"]
            }

    _ggH_dataset_map = dict(_ggH_dataset_map, **_ggH_dataset_map_fraction)
    _dataset_map = dict({
        "data": "data",
        "ZTT": "DY",
        "ZL": "DY",
        "ZJ": "DY",
        "TTT": "TT",
        "TTL": "TT",
        "TTJ": "TT",
        "VVT": "VV",
        "VVL": "VV",
        "VVJ": "VV",
        "W": "W",
        "EMB": "EMB",
        "QCDEMB": "QCD",
        "QCD": "QCDMC",
        "jetFakesEMB": "jetFakes",
        "jetFakes": "jetFakesMC",
        "ggH125": "ggH",
        "qqH125": "qqH",
        "wFakes": "wFakes",
    }, **_ggH_dataset_map)

    _ggH_process_map = dict(_ggH_process_map, **_ggH_process_map_fraction)
    _process_map = dict({
        "data": "data",
        "ZTT": "DY-ZTT",
        "ZL": "DY-ZL",
        "ZJ": "DY-ZJ",
        "TTT": "TT-TTT",
        "TTL": "TT-TTL",
        "TTJ": "TT-TTJ",
        "VVT": "VV-VVT",
        "VVL": "VV-VVL",
        "VVJ": "VV-VVJ",
        "W": "W",
        "EMB": "Embedded",
        "QCDEMB": "QCD",
        "QCD": "QCDMC",
        "jetFakesEMB": "jetFakes",
        "jetFakes": "jetFakesMC",
        "ggH125": "ggH125",
        "qqH125": "qqH125",
        "wFakes": "wFakes",
    }, **_ggH_process_map)

    def __init__(self, inputrootfilename, variable):
        self._rootfilename = inputrootfilename
        self._rootfile = ROOT.TFile(self._rootfilename, "READ")
        self._variable = variable

    @property
    def rootfile(self):
        return self._rootfile

    def get(self, channel, process, category=None, shape_type="Nominal"):
        dataset = self._dataset_map[process]
        if category is None:
            category = "" if "data" in process else "-" + self._process_map[process]
        else:
            category = "-" + category if "data" in process else "-" + "-".join([self._process_map[process], category])
        hist_hash = "{dataset}#{channel}{category}#{shape_type}#{variable}".format(
            dataset=dataset,
            channel=channel,
            category=category,
            shape_type=shape_type,
            variable=self._variable)
        logger.debug("Try to access %s in %s" % (hist_hash,
                                                 self._rootfilename))

        return self._rootfile.Get(hist_hash)

    def list_contents(self):
        return [key.GetTitle() for key in self._rootfile.GetListOfKeys()]

    def get_bins(self, channel, category):
        hist = self.get(channel, category)
        nbins = hist.GetNbinsX()
        bins = []
        for i in range(nbins):
            bins.append(hist.GetBinLowEdge(i + 1))
        bins.append(hist.GetBinLowEdge(i + 1) + hist.GetBinWidth(i + 1))
        return bins

    def get_values(self, channel, category):
        hist = self.get(channel, category)
        nbins = hist.GetNbinsX()
        values = []
        for i in range(nbins):
            values.append(hist.GetBinContent(i + 1))
        return values

    def __del__(self):
        logger.debug("Closing rootfile %s" % (self._rootfilename))
        self._rootfile.Close()
