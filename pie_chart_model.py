# -*- coding: utf-8 -*-

import re
import os
import MySQLdb
import shutil
import pickle

import base_model

class Column_Chart(object):

    @classmethod
    def get_pie_chart_javascript(self, ChartName, ContainerName, Title, DataStr):
        char_javascript = '''
         var  __ChartName__ = new Highcharts.Chart({
            chart: {
                renderTo: '__ContainerName__',
                plotBackgroundColor: null,
                plotBorderWidth: null,
                plotShadow: false
            },
            title: {
                text: '__Title__'
            },
            tooltip: {
                formatter: function() {
                    return '<b>'+ this.point.name +'</b>: '+ this.percentage +' %';
                }
            },
            plotOptions: {
                pie: {
                    allowPointSelect: true,
                    cursor: 'pointer',
                    dataLabels: {
                        enabled: false
                        },
                        showInLegend: true
                }
            },
            series: [{
                type: 'pie',
                name: 'Browser share',
                data: [
                    __DataStr__
                ]
            }]
        });
        '''
        char_javascript = char_javascript.replace('__ChartName__',ChartName)
        char_javascript = char_javascript.replace('__ContainerName__',ContainerName)
        char_javascript = char_javascript.replace('__Title__',Title)
        char_javascript = char_javascript.replace('__DataStr__',DataStr)
        return char_javascript

    @classmethod
    def get_str(self, Pie_data_dic):
        result = ''
        for a_key in Pie_data_dic.keys():
            if result:
                result = result + ",['" + a_key + "'," + str(Pie_data_dic[a_key]) + ']'
            else:
                result = result + "['" + a_key + "'," + str(Pie_data_dic[a_key]) + ']'
        return result

    @classmethod
    def get_table_str(self, data_dic):
        result = '<table class="listing">'
        for a_key in data_dic:
            result = result + "<tr><td>" + a_key + "</td><td>" + unicode(data_dic[a_key]) + "</td></tr>"
        result = result + "</table>"
        return result
